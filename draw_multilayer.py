#!/usr/bin/env python
"""
Plot multi-graphs in 3D.
"""
from os import name
import numpy as np
import matplotlib 
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import networkx as nx

from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Line3DCollection

import renormalizer
import converter


class MultilayerGraph(object):

    def __init__(self, graphs, node_labels=None, layout=nx.spring_layout, ax=None, 
                 positions_uniform=None, clusters=None, color_list=[], node_size_list=[]):
        """Given an ordered list of graphs [g1, g2, ..., gn] that represent
        different layers in a multi-layer network, plot the network in
        3D with the different layers separated along the z-axis.

        Within a layer, the corresponding graph defines the connectivity.
        Between layers, nodes in subsequent layers are connected if
        they have the same node ID.

        Arguments:
        ----------
        graphs : list of networkx.Graph objects
            List of graphs, one for each layer.

        node_labels : dict node ID : str label or None (default None)
            Dictionary mapping nodes to labels.
            If None is provided, nodes are not labelled.

        layout_func : function handle (default networkx.spring_layout)
            Function used to compute the layout.

        ax : mpl_toolkits.mplot3d.Axes3d instance or None (default None)
            The axis to plot to. If None is given, a new figure and a new axis are created.

        """

        # book-keeping
        self.graphs = graphs
        self.total_layers = len(graphs) - 1 ##### TODO find a better way to deal with the uppermost layer

        self.node_labels = node_labels
        self.layout = layout

        self.positions_uniform = positions_uniform
        self.clusters = clusters
        self.color_list = color_list
        self.node_size_list = node_size_list

        if ax:
            self.ax = ax
        else:
            fig = plt.figure()
            fig.set_figheight(25)
            fig.set_figwidth(20)
            self.ax = fig.add_subplot(111, projection='3d')

        # create internal representation of nodes and edges
        self.get_nodes()
        self.get_edges_within_layers()
        self.get_edges_between_layers()

        # compute layout and plot
        self.get_node_positions_uniform()
        self.draw()


    def get_nodes(self):
        """Construct an internal representation of nodes with the format (node ID, layer)."""
        self.nodes = []
        for z, g in enumerate(self.graphs[:-1]):
            self.nodes.extend([(node, z) for node in g.nodes()])


    def get_edges_within_layers(self):
        """Remap edges in the individual layers to the internal representations of the node IDs."""
        self.edges_within_layers = []
        for z, g in enumerate(self.graphs[:-1]):
            self.edges_within_layers.extend([((source, z), (target, z)) for source, target in g.edges()])


    def get_edges_between_layers(self):
        """Determine edges between layers. Nodes in previous layers connect to 
        the supernode that contains it in the next layer."""
        self.edges_between_layers = []
        for z1 in range(len(self.graphs[:-2])):
            z2 = z1 + 1
            nodes_down = list(self.clusters[z1].keys())
            nodes_up = list(self.clusters[z1].values())

            # TODO assuming the membership dict has # keys = # values
            self.edges_between_layers.extend([((nodes_down[i], z1), (nodes_up[i], z2)) 
                                              for i in range(len(nodes_down))])

        # Old way: node i in layer z1 maps to node i in z2
        # self.edges_between_layers = []
        # for z1, g in enumerate(self.graphs[:-2]):
        #     z2 = z1 + 1
        #     h = self.graphs[z2]
        #     shared_nodes = set(g.nodes()) & set(h.nodes())
        #     self.edges_between_layers.extend([((node, z1), (node, z2)) for node in shared_nodes])


    def get_node_positions(self, *args, **kwargs):
        """Get the node positions in the multilayer graph."""
        # What we would like to do, is apply the layout function to a combined, multilayer network.
        # However, networkx layout functions are not implemented for the multi-dimensional case.
        # Futhermore, even if there was such a layout function, there probably would be no straightforward way to
        # specify the planarity requirement for nodes within a layer.
        # Therefor, we compute the layout for the full network in 2D, and then apply the
        # positions to the nodes in all planes.
        # For a force-directed layout, this will approximately do the right thing.
        # TODO: implement FR in 3D with layer constraints.

        composition = self.graphs[0]
        for h in self.graphs[1:]:
            composition = nx.compose(composition, h)

        pos = self.layout(composition, *args, **kwargs)

        self.node_positions = dict()
        for z, g in enumerate(self.graphs[:-1]):
            self.node_positions.update({(node, z) : (*pos[node], z) for node in g.nodes()})


    def get_node_positions_uniform(self):
        
        composition = self.graphs[0]
        for h in self.graphs[1:-1]:
            composition = nx.compose(composition, h)

        pos = self.positions_uniform

        self.node_positions = dict()
        for z, _ in enumerate(self.graphs[:-1]):
            self.node_positions.update({(node, z) : (pos[z][node][0], 
                                                     pos[z][node][1], 
                                                     3*z) for node in pos[z].keys()})            


    def draw_nodes(self, nodes, *args, **kwargs):
        x, y, z = zip(*[self.node_positions[node] for node in nodes])
        self.ax.scatter(x, y, z, *args, **kwargs)


    def draw_edges(self, edges, *args, **kwargs):
        segments = [(self.node_positions[source], self.node_positions[target]) for source, target in edges]
        line_collection = Line3DCollection(segments, *args, **kwargs)
        self.ax.add_collection3d(line_collection)


    def get_extent(self, pad=0.1):
        xyz = np.array(list(self.node_positions.values()))
        xmin, ymin, _ = np.min(xyz, axis=0)
        xmax, ymax, _ = np.max(xyz, axis=0)
        dx = xmax - xmin
        dy = ymax - ymin
        return (xmin - pad * dx, xmax + pad * dx), \
               (ymin - pad * dy, ymax + pad * dy)


    def draw_plane(self, z, *args, **kwargs):
        pad = 0.05
        (xmin, xmax), (ymin, ymax) = self.get_extent(pad=pad)
        u = np.linspace(xmin, xmax, 1000)
        v = np.linspace(ymin, ymax, 1000)
        U, V = np.meshgrid(u, v)
        W = 3*z*np.ones_like(U)

        # Configuring the text in each plane
        if z == 0:
            text = "Original network"
        else:
            text = "Renormalized layer {}".format(z)
        self.ax.plot_surface(U, V, W, *args, **kwargs)
        self.ax.text(xmin+pad, ymin+pad, 3*z-8*pad, text, (1,0,0), size='large', style='oblique', 
                     weight='bold', color='grey')
        # surf._facecolors2d = surf._facecolor3d
        # surf._edgecolors2d = surf._edgecolor3d


    def draw_node_labels(self, node_labels, *args, **kwargs):
        for node, z in self.nodes:
            if node in node_labels:
                ax.text(*self.node_positions[(node, 3*z)], node_labels[node], *args, **kwargs)


    def color_nodes(self, cmap_name="Spectral"):
        cmap = plt.get_cmap(cmap_name)
        color_dict = dict()

        for i in range(len(self.clusters)):
            self.color_list.append([])
            clusters = list((self.clusters[i].items()))
            clusters_unique = set([cluster[1] for cluster in clusters])
            
            clusters_covered = []
            for j in range(len(self.clusters[i])):
                node = clusters[j][0]
                cluster_id = clusters[j][1]
                if cluster_id not in clusters_covered:
                    clusters_covered.append(cluster_id)

                try: # Summing unique cluster ids and dividing by total sum of cluster ids
                    color_dict[node] = cmap(sum(clusters_covered)/sum(clusters_unique))
                except: # In case there is only node 0 left for the denominator
                    color_dict[node] = cmap(cluster_id)

                self.color_list[i].append(color_dict[node])


    def size_nodes(self, base_size=100):
        """ Storing node sizes according to their degrees """
        for z in range(self.total_layers):
            degree_dict = dict(self.graphs[z].degree)
            self.node_size_list.append([base_size*deg+base_size for deg in degree_dict.values()])


    def draw(self):
        self.size_nodes(100)
        self.color_nodes()
        self.draw_edges(self.edges_within_layers,  color='k', alpha=0.15, linestyle='-', zorder=2, linewidths=0.4)
        self.draw_edges(self.edges_between_layers, color='k', alpha=0.4, linestyle='--', zorder=2, linewidths=1.0)

        for z in range(self.total_layers):
            self.draw_plane(z, alpha=0.05, cmap='gray', label="teste")
            self.draw_nodes([node for node in self.nodes if node[1]==z], 
                            alpha=1, s=self.node_size_list[z], zorder=3, c=self.color_list[z])

        if self.node_labels:
            self.draw_node_labels(self.node_labels,
                                  horizontalalignment='center',
                                  verticalalignment='center',
                                  zorder=100)


if __name__ == '__main__':

    infile = 'karate_network'

    #mercator.embed(infile + ".txt", infile + ".txt")
    parameters_json = converter.convert_to_json(infile)

    index_list = [node['index'] for node in parameters_json['nodes'].values()]
    angles_list = [node['theta'] for node in parameters_json['nodes'].values()]
    kappas_list = [node['kappa'] for node in parameters_json['nodes'].values()]
    radius_h2_list = [node['r'] for node in parameters_json['nodes'].values()]

    angles_dict = dict(zip(index_list, angles_list))
    kappas_dict = dict(zip(index_list, kappas_list))
    raidus_h2_dict = dict(zip(index_list, radius_h2_list))

    graphs, pos_nodes, membership_dict, kappas = renormalizer.renormalize_network(infile,
                                                                                  kappas_dict, 
                                                                                  angles_dict)

    fig = plt.figure()
    fig.set_figheight(25)
    fig.set_figwidth(20)
    ax = fig.add_subplot(111, projection='3d')
    MultilayerGraph(graphs, ax=ax, layout=nx.spring_layout, 
                    positions_uniform=pos_nodes, clusters=membership_dict)
    ax.set_axis_off()

    plt.savefig("multilayer_renormalization.pdf")
    plt.close()


## TODO TODO TODO:
# 3) Lines connecting nodes that generate next layer's clusters
# 5) Solve ordering problem for the planes (mayavi lib)
# 5) Choose what to do w/ the last layer