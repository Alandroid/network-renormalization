import matplotlib 
matplotlib.use('Agg') 
from matplotlib import pylab as plt
import math
import networkx as nx
import mercator

import renormalizer
import converter

# Basic usage
import community as community_louvain
import networkx as nx

from matplotlib import pyplot as plt


def coarsen_nodes_louvain(graph):
    membership = community_louvain.generate_dendrogram(graph)

    return membership


def embed_mercator(infile):
    mercator.embed(infile + ".txt", infile)
    parameters_json = converter.convert_to_json(infile)

    index_list = [node['index'] for node in parameters_json['nodes'].values()]
    angles_list = [node['theta'] for node in parameters_json['nodes'].values()]
    kappas_list = [node['kappa'] for node in parameters_json['nodes'].values()]
    radius_h2_list = [node['r'] for node in parameters_json['nodes'].values()]

    angles_dict = dict(zip(index_list, angles_list))
    kappas_dict = dict(zip(index_list, kappas_list))
    radius_h2_dict = dict(zip(index_list, radius_h2_list))

    return angles_dict, kappas_dict, radius_h2_dict


def cast_membership_to_cluster(current_membership):
    cluster = dict()

    for key, value in current_membership.items():
        cluster[value] = [key] if value not in cluster.keys() else cluster[value] + [key]

    # Converting the values from lists to dicts
    # for key, list_cluster in cluster.items():
    #     cluster[key] = dict((i, list_cluster[i]) for i in range(len(list_cluster)))

    return cluster


def write_link_file(links, outfile):
    """ https://stackoverflow.com/questions/899103/writing-a-list-to-a-file-with-python/899176 """
    with open('{}.txt'.format(outfile), 'w') as f:
        for (x, y) in links:
            f.write("{} {}\n".format(x, y))


def search_clusters(value, dic):
    ''' 
    Find the author of this function !!!
    '''
    if hasattr(dic, 'items'):
        for key in dic:
            for item in dic[key]:
                if item == value:
                    return key


def coarsen_links(cluster, links):
    # Renormalizing the links

    coarsened_links = []
    for cluster_id in cluster:
        for node in cluster[cluster_id]:
            for (x, y) in links:
                if y == node:
                    coarsened_links.append((search_clusters(x, cluster), cluster_id))
                if x == node:
                    coarsened_links.append((cluster_id, search_clusters(y, cluster)))  

    # Removing duplicates and self-loops
    coarsened_links = list(set(map(tuple, map(sorted, coarsened_links))))
    coarsened_links = [link for link in coarsened_links if link[0] != link[1]]

    return coarsened_links


def form_network_uniform(angles, links, renorm_step):
    N = len(angles)    # Updating the number of nodes
    R = N/(2*math.pi)  # In S1, R is constant for each step

    G = nx.Graph()

    # Ordering the nodes by original angle (before normalizing it)
    angles_ordered = dict(sorted(angles.items(), key=lambda item: item[1]))

    # Add a constant angle bias to align the layers
    # flag_layer = 0
    # if renorm_step > 0: 
    #     flag_layer = 1

    # Adding the nodes
    uniform_angles = {}
    position = {}
    node_iter = 0
    for cluster_id in angles_ordered:
        if node_iter == 0:
            bias = angles_ordered[cluster_id]
        current_angle = 2*math.pi*(node_iter/N) #+ flag_layer*bias
        uniform_angles[cluster_id] = current_angle
        position[cluster_id] = (R * math.cos(float(current_angle)), 
                                R * math.sin(float(current_angle)))
        G.add_node(int(cluster_id))
        node_iter += 1

    pos_nodes = nx.spring_layout(G, pos=position, fixed=list(position.keys()))

    # Only considering non-directed, non-weighted networks
    links = list(set(map(tuple, map(sorted, links))))
    G.add_edges_from(links)

    return G, pos_nodes, uniform_angles


def form_network_uniform_hybrid(angles, links, renorm_step):
    N = len(angles)    # Updating the number of nodes
    R = N/(2*math.pi)  # In S1, R is constant for each step

    G = nx.Graph()

    # Ordering the nodes by original angle (before normalizing it)
    angles_ordered = dict(sorted(angles.items(), key=lambda item: item[1]))

    # Add a constant angle bias to align the layers
    # flag_layer = 0
    # if renorm_step > 0: 
    #     flag_layer = 1

    # Adding the nodes
    uniform_angles = {}
    position = {}
    node_iter = 0
    for cluster_id in angles_ordered:
        if node_iter == 0:
            bias = angles_ordered[cluster_id]
        current_angle = 2*math.pi*(node_iter/N)# + flag_layer*bias
        # Now we store both the angle before and after uniformization
        uniform_angles[cluster_id] = {"original_angle": angles_ordered[cluster_id],
                                      "uniform_angle": current_angle} 
        position[cluster_id] = (R * math.cos(float(angles_ordered[cluster_id])), 
                                R * math.sin(float(angles_ordered[cluster_id])))
        G.add_node(int(cluster_id))
        node_iter += 1

    pos_nodes = nx.spring_layout(G, pos=position, fixed=list(position.keys()))

    # Only considering non-directed, non-weighted networks
    links = list(set(map(tuple, map(sorted, links))))
    G.add_edges_from(links)

    return G, pos_nodes, uniform_angles


def coarsen_multilayer(infile, outfile):

    graphs = []
    pos_nodes = []
    kappas_list = []

    ## TODO: find a way to put all this inside a while to not repeat it
    angles_dict, kappas_dict, radius_h2_dict = embed_mercator(infile)
    links = renormalizer.read_links(infile)

    coarsen_step = 0
    # Form the new network
    G, current_pos, uniform_angles = form_network_uniform_hybrid(angles_dict, links, coarsen_step)
    #G, current_pos, uniform_angles = form_network_uniform(angles_dict, links, coarsen_step)
    graphs.append(G)
    pos_nodes.append(current_pos)
    kappas_list.append(kappas_dict)

    membership_list = coarsen_nodes_louvain(graphs[0])
    #membership_list.append(membership_list[len(membership_list)-1])
    total_steps = len(membership_list)

    # Transforming the lists back into the format used in the renormalization file
    cluster = cast_membership_to_cluster(membership_list[coarsen_step])
    links = coarsen_links(cluster, links)
    write_link_file(links, outfile)

    # TODO this way we make case 0 outside and inside from 1 onwards
    for coarsen_step in range(1, total_steps):

        angles_dict, kappas_dict, radius_h2_dict = embed_mercator(outfile)
        links = renormalizer.read_links(outfile)

        G, current_pos, uniform_angles = form_network_uniform_hybrid(angles_dict, links, coarsen_step)
        #G, current_pos, uniform_angles = form_network_uniform(angles_dict, links, coarsen_step)
        graphs.append(G)
        pos_nodes.append(current_pos)
        kappas_list.append(kappas_dict)

        # Transforming the lists back into the format I used in the renormalization file
        cluster = cast_membership_to_cluster(membership_list[coarsen_step])
        links = coarsen_links(cluster, links)
        outfile = infile + "_louvain_step__{}".format(coarsen_step)
        write_link_file(links, outfile)
        # Don't print communities in final step -- TODO in this case

    graphs.append(graphs[len(graphs)-1])
    pos_nodes.append(pos_nodes[len(pos_nodes)-1])
    membership_list.append(membership_list[len(membership_list)-1])
    kappas_list.append(kappas_list[len(kappas_list)-1])

    return graphs, pos_nodes, membership_list, kappas_list



infile = 'karate_network'
outfile = infile + "_louvain_step_0"
graphs, pos_nodes, membership_dict, kappas = coarsen_multilayer(infile, outfile)

#membership_dict.append({}) # The last graph is plotted without clusters
# for i in range(len(graphs)):
#     plt.figure(figsize=(10, 10))
#     plt.axis('off')

#     membership_list = [v for (_,v) in membership_dict[i].items()]
#     degree_dict = dict(graphs[i].degree)
#     node_size_list = [100*deg+100 for deg in degree_dict.values()]

#     if membership_list:
#         nx.draw_networkx_nodes(graphs[i], pos_nodes[i], node_size=node_size_list,
#                                cmap=plt.cm.Spectral, node_color=membership_list)
#     else:
#         nx.draw_networkx_nodes(graphs[i], pos_nodes[i], node_size=node_size_list, 
#                                cmap=plt.cm.Spectral)

#     nx.draw_networkx_edges(graphs[i], pos_nodes[i], alpha=0.3)
#     #nx.draw_networkx_labels(graphs[i], pos_nodes[i])

#     outfile = outfile.split("__")[0] + "__" + str(i) + ".pdf"
#     plt.savefig(outfile)
#     plt.close()
