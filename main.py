import mercator as mktr
import math
import networkx as nx
from matplotlib import pylab as plt
import random as rd
from collections import OrderedDict
import numpy as np


def search_clusters(key, dic):
    if hasattr(dic,'items'):
        for k in dic:
            for value in dic[k]:
                if value == key:
                    return k


#emb = mktr.embed("karate_network.txt", output_name="rede_teste.txt")

infile = 'karate_network.txt'
links_file = open(infile, 'r+')
outfile = infile.split(".")[0] + "_step__0.pdf"

theta = [
   1.44041,
   6.23715,
     5.311,
   1.28297,
   2.49892,
   2.63209,
   2.65796,
   1.62686,
   3.98758,
   5.21079,
   2.50646,
   1.52629,
   1.33973,
   1.05508,
   5.05451,
    4.9911,
   2.68651,
  0.824205,
   5.08854,
   0.14207,
   4.95233,
   0.72676,
   5.01895,
   6.14769,
   6.06176,
   5.93969,
   5.11764,
   5.70784,
   5.17443,
   5.81763,
   4.19226,
  0.291503,
   3.52876,
   3.94216
]


radii_h2 = [ 
    3.9647, 
    4.36491, 
    3.7328 ,
    7.71664,
    10.3964,
    9.93667,
    10.0296,
    8.69941,
    8.61662,
    14.0491,
    10.436 ,
    14.3513,
    12.4851,
    9.29678,
    13.0424,
    12.8272,
    11.5599,
    11.3453,
    13.1994,
    10.1995,
    12.6094,
    11.3383,
    12.9363,
    11.6839,
    11.732 ,
    11.7199,
    13.3457,
    11.4904,
    13.705 ,
    11.6531,
    9.82493,
    10.2414,
    8.39207,
    9.34447
]


kappa = [
    51.6276,
    42.2647,
    57.9746,
    7.90966,
    2.07141,
    2.60666,
    2.48829,
    4.83896,
    5.04347,
    0.333487,
    2.03072,
    0.286727,
    0.728947,
    3.5895,
    0.551683,
    0.614348,
    1.15774,
    1.28886,
    0.510025,
    2.2857,
    0.685025,
    1.29335,
    0.581743,
    1.0881,
    1.06225,
    1.06869,
    0.474045,
    1.19868,
    0.396101,
    1.10502,
    2.75644,
    2.23828,
    5.64275,
    3.50493
]


index = [
    0,
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    12,
    13,
    14,
    15,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    23,
    24,
    25,
    26,
    27,
    28,
    29,
    30,
    31,
    32,
    33
]

G = nx.Graph()
N = len(theta)
R = N/(2*math.pi) # On S1 this is the formula, constant for each coarsening step
#C = 1
#k_bar = 2#int(input('Enter the desired average degree: '))
#R = -(2/C)*math.log(math.pi*k_bar/(8*N))


#position = {}
# Distributing the nodes
for i in range(N):
    #position[index[i]] = (R*math.cos(theta[i]), R*math.sin(theta[i]))
    G.add_node(index[i])

#pos = nx.spring_layout(G, pos=position, fixed=list(position.keys()))

# plt.figure(figsize=(10,10)) 
# nx.draw_networkx_nodes(G, pos, node_color='r', node_size=200)

# Distributing the links
links = []
for row in links_file:
    first = int(row.split(" ")[0])
    second = int(row.split(" ")[1].split("\n")[0])
    links.append((first, second))
    G.add_edge(first, second)

# Here we only consider non-directed, weightless networks
links = list(set(map(tuple, map(sorted, links))))

# nx.draw_networkx_edges(G, pos)
# #nx.draw(G, node_size=50, width=0.3)
# plt.savefig("karate_hyperbolic.pdf")
# plt.close()


#########################
# Renormalization step: #
#########################

nmbr_renorm_steps = int(input('How many renormalization steps do you want to perform? '))
r = int(input('Enter the desired cluster size: '))

angles_indexed = dict(zip(index, theta))
kappas_indexed = dict(zip(index, kappa))


for renorm_step_indx in range(nmbr_renorm_steps):

    print("\n\nIteration {}".format(renorm_step_indx))
    print("Angles indexed: {}".format(angles_indexed))
    print("Kappas indexed: {}\n\n".format(kappas_indexed))
    cluster_angles = {}
    cluster_kappas = {}
    diff_dict = {}

    angles_indexed_copy = angles_indexed.copy()
    kappas_indexed_copy = kappas_indexed.copy()


    m = 0   # TODO will we always want the 1st vertex to start in 0?
    for i in angles_indexed:
        if i in angles_indexed_copy:
            cluster_angles[m] = {}
            cluster_kappas[m] = {}
            diff_dict[i] = math.inf

            for j in angles_indexed:
                if j in angles_indexed_copy:
                    diff_dict[j] = abs(angles_indexed_copy[i] - angles_indexed_copy[j])

            diff_dict = dict(sorted(diff_dict.items(), key=lambda item: item[1]))

            cluster_size = 0
            for k in diff_dict.copy():
                if cluster_size < r and k in diff_dict: # Including i itself
                    cluster_angles[m][k] = angles_indexed_copy[k]
                    cluster_kappas[m][k] = kappas_indexed_copy[k]
                    angles_indexed_copy.pop(k)
                    kappas_indexed_copy.pop(k)
                    diff_dict.pop(k)
                    cluster_size += 1

            m += 1

    print("\n\nCluster angles: {}\n\n".format(cluster_angles))
    print("\n\nCluster kappas: {}\n\n".format(cluster_kappas))

    position = {}
    # Distributing the nodes
    for i in range(len(angles_indexed)):
        position[i] = (R*math.cos(angles_indexed[i]), R*math.sin(angles_indexed[i]))
    print(position)
    pos = nx.spring_layout(G, pos=position, fixed=list(position.keys()))

  

    membership = {}
    for i in cluster_angles:
        for node in cluster_angles[i]:
            membership[node] = i

    plt.figure(figsize=(10,10))
    plt.axis('off')
    nx.draw_networkx_nodes(G, pos, node_size=200, cmap=plt.cm.RdYlBu, node_color=list(membership.values()))
    nx.draw_networkx_edges(G, pos, alpha=0.3)

    outfile = outfile.split("__")[0] + "__" + str(renorm_step_indx) + ".pdf"
    plt.savefig(outfile)
    plt.close()

    ########################################

    beta = 2 #!!! TODO do not hardcode this
    renormalized_angles = {}
    renormalized_kappas = {}


    # Renormalizing the hidden degrees
    for i in cluster_kappas:
        renormalized_kappas[i] = np.sum(np.array(list(cluster_kappas[i].values())[1:])**beta)**(1/beta)

    print("Renormalized kappas: {}\n\n".format(renormalized_kappas))


    # Renormalizing the angles
    for i in cluster_angles:
        angles = np.array(list(cluster_angles[i].values())[1:])
        kappas = np.array(list(cluster_kappas[i].values())[1:])

        numerator = (angles**beta).dot(kappas**beta)
        denominator = renormalized_kappas[i]

        renormalized_angles[i] = (numerator**(1/beta))/denominator

    print("Renormalized angles: {}\n\n".format(renormalized_angles))


    # Renormalizing the links
    renormalized_links = []
    for cluster_id in cluster_kappas:
        for subnode in cluster_kappas[cluster_id]:
            for (x, y) in links:
                if y == subnode:
                    renormalized_links.append((search_clusters(x, cluster_kappas), cluster_id))
                if x == subnode:
                    renormalized_links.append((cluster_id, search_clusters(y, cluster_kappas)))


    # Removing duplicates and self-loops
    renormalized_links = list(set(map(tuple, map(sorted, renormalized_links))))
    renormalized_links = [link for link in renormalized_links if link[0] != link[1]]

    ## TODO DOUBLE CHECK THAT THE LINKS ARE BEING GROUPED CORRECTLY

    # Updating the radius
    N = len(renormalized_angles)
    R = N/(2*math.pi)  # Since we are dealing with S1, we will use R constant in the plot

    # Putting it all together to form the new network
    G = nx.Graph()

    # Adding and drawing the nodes
    position = {}
    for cluster_id in renormalized_angles:
        position[cluster_id] = (R * math.cos(float(renormalized_angles[cluster_id])), 
                    R * math.sin(float(renormalized_angles[cluster_id])))
        G.add_node(cluster_id)

    pos = nx.spring_layout(G, pos=position, fixed=list(position.keys()))
    plt.figure(figsize=(10,10)) 
    nx.draw_networkx_nodes(G, pos, node_color='r', node_size=200)

    # Adding and drawing the links
    G.add_edges_from(renormalized_links)   
    nx.draw_networkx_edges(G, pos, width=0.3)

    membership = {}
    for node in renormalized_angles:
        membership[node] = node

    plt.figure(figsize=(10,10))
    plt.axis('off')
    nx.draw_networkx_nodes(G, pos, node_size=200, cmap=plt.cm.RdYlBu, node_color=list(membership.values()))
    nx.draw_networkx_edges(G, pos, alpha=0.3)

    outfile = outfile.split("__")[0] + "__" + str(renorm_step_indx + 1) +".pdf"
    plt.savefig(outfile)
    plt.close()

    print("angles begore: ", angles_indexed)

    angles_indexed = renormalized_angles
    kappas_indexed = renormalized_kappas

    print("angles after: ", angles_indexed)


    ### TODO treat case in which there is only 1 node left in a cluster