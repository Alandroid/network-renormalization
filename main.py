#!/usr/bin/env python
"""
Plot multi-graphs in 3D using the class MultilayerGraph.

Code modified from Paul Brodersen's response to the following post:
https://stackoverflow.com/questions/60392940/multi-layer-graph-in-networkx
"""

import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import networkx as nx
import mercator

from utils import renormalizer, converter, multilayer_graph

path = str(input('What\'s the name of the input file? (It should be inside the \'data\' folder)\n'))

infile = 'data/' + path

# mercator.embed(infile + ".txt", infile)
parameters_json = converter.convert_to_json(infile)
beta = converter.get_beta(infile)

index_list = [node['index'] for node in parameters_json['nodes'].values()]
angles_list = [node['theta'] for node in parameters_json['nodes'].values()]
kappas_list = [node['kappa'] for node in parameters_json['nodes'].values()]
radius_h2_list = [node['r'] for node in parameters_json['nodes'].values()]

angles_dict = dict(zip(index_list, angles_list))
kappas_dict = dict(zip(index_list, kappas_list))
radius_h2_dict = dict(zip(index_list, radius_h2_list))

## Renormalization multilayer
graphs, pos_nodes, membership_dict, kappas = renormalizer.renormalize_network(
    infile,
    kappas_dict,
    angles_dict,
    beta
)
pdf_file_name = "results/multilayer_renormalization_" + infile.split("/")[1] + ".pdf"

for i in range(len(graphs)):
    converter.convert_edgefile_to_adj(graphs[i], infile, i)

fig = plt.figure()
fig.set_figheight(25)
fig.set_figwidth(20)
ax = fig.add_subplot(111, projection='3d')
multilayer_graph.MultilayerGraph(
    graphs, ax=ax, layout=nx.spring_layout, 
    positions_uniform=pos_nodes, clusters=membership_dict
)
ax.set_axis_off()

plt.savefig(pdf_file_name)
plt.close()


## TODO:
# 1) Choose what to do w/ the last layer