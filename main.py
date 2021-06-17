import matplotlib 
matplotlib.use('Agg') 
from matplotlib import pylab as plt
import networkx as nx
import mercator

import renormalizer
import converter


infile = 'karate_network'
outfile = infile + "_step__0.pdf"

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
membership_dict.append({}) # The last graph is plotted without clusters

for i in range(len(graphs)):
    plt.figure(figsize=(10, 10))
    plt.axis('off')
    
    # membership_ordered = []
    # for key in sorted(membership_list[i]): # TODO this code block is suitable for the old version
    #     membership_ordered.append(membership_list[i][key])

    membership_list = [v for (_,v) in membership_dict[i].items()]
    degree_dict = dict(graphs[i].degree)
    node_size_list = [100*deg+100 for deg in degree_dict.values()]

    if membership_list:
        nx.draw_networkx_nodes(graphs[i], pos_nodes[i], node_size=node_size_list,
                               cmap=plt.cm.Spectral, node_color=membership_list)
    else:
        nx.draw_networkx_nodes(graphs[i], pos_nodes[i], node_size=node_size_list, 
                               cmap=plt.cm.Spectral)

    nx.draw_networkx_edges(graphs[i], pos_nodes[i], alpha=0.3)
    #nx.draw_networkx_labels(graphs[i], pos_nodes[i])

    outfile = outfile.split("__")[0] + "__" + str(i) + ".pdf"
    plt.savefig(outfile)
    plt.close()
