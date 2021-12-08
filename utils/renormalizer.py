from operator import sub
import numpy as np
from numpy.lib.function_base import angle
np.seterr("raise")
import math
import networkx as nx


def read_links(infile):
    links = []
    links_file = open(infile + '.txt', 'r+')
    for row in links_file:
        first = int(row.split(" ")[0])
        second = int(row.split(" ")[1].split("\n")[0])
        links.append((first, second))

    return links


def search_clusters(value, dic):
    # TODO: author
    if hasattr(dic, 'items'):
        for key in dic:
            for item in dic[key]:
                if item == value:
                    return key


def renormalize_nodes(cluster_kappas, cluster_angles, beta):
    renormalized_angles = {}
    renormalized_kappas = {}

    # Renormalizing the hidden degrees
    for i in cluster_kappas:
        kappas = np.array(list(cluster_kappas[i].values())) ###[1:]
        renormalized_kappas[i] = np.sum(kappas**beta)**(1/beta)
       
    # Renormalizing the angles
    for i in cluster_angles:
        angles = np.array(list(cluster_angles[i].values())) ###[1:]
        kappas = np.array(list(cluster_kappas[i].values())) ###[1:]

        numerator = (angles**beta).dot(kappas**beta)
        denominator = renormalized_kappas[i]
        renormalized_angles[i] = (numerator**(1/beta))/denominator

    return renormalized_kappas, renormalized_angles


def renormalize_links(cluster_kappas, links):
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

    return renormalized_links


def form_network(angles, links):
    N = len(angles)    # Updating the number of nodes
    R = N/(2*math.pi)  # In S1, R is constant for each step

    G = nx.Graph()

    # Adding the nodes
    position = {}
    for cluster_id in angles:
        position[cluster_id] = (R * math.cos(float(angles[cluster_id])), 
                                R * math.sin(float(angles[cluster_id])))
        G.add_node(cluster_id)

    pos_nodes = nx.spring_layout(G, pos=position, fixed=list(position.keys()))

    # Only considering non-directed, non-weighted networks
    links = list(set(map(tuple, map(sorted, links))))
    G.add_edges_from(links)   

    return G, pos_nodes


def form_network_uniform(angles, links, renorm_step):
    N = len(angles)    # Updating the number of nodes
    R = N/(2*math.pi)  # In S1, R is constant for each step

    G = nx.Graph()

    # Ordering the nodes by original angle (before normalizing it)
    angles_ordered = dict(sorted(angles.items(), key=lambda item: item[1]))

    # Add a constant angle bias to align the layers
    flag_layer = 0
    if renorm_step > 0: 
        flag_layer = 1

    # Adding the nodes
    uniform_angles = {}
    position = {}
    node_iter = 0
    for cluster_id in angles_ordered:
        if node_iter == 0:
            bias = angles_ordered[cluster_id]
        current_angle = 2*math.pi*(node_iter/N) + flag_layer*bias
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
    flag_layer = 0
    if renorm_step > 0: 
        flag_layer = 1

    # Adding the nodes
    uniform_angles = {}
    position = {}
    node_iter = 0
    for cluster_id in angles_ordered:
        if node_iter == 0:
            bias = angles_ordered[cluster_id]
        current_angle = 2*math.pi*(node_iter/N) + flag_layer*bias
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


def find_clusters(kappas, angles, r):
    """
    This function sets the cluster attribution for the nodes. This
    is the simpler implementation, with constant cluster size
    
    """
    cluster_angles = {}
    cluster_kappas = {}
    diff_dict = {}
    angles_copy = angles.copy()
    kappas_copy = kappas.copy()

    # TODO simplify this
    id_cluster = 0
    for i in angles:
        if i in angles_copy:
            cluster_angles[int(id_cluster)] = {}
            cluster_kappas[id_cluster] = {}
            diff_dict[i] = math.inf

            for j in angles:
                if j in angles_copy: # Creating a dict to find the closest neighbors
                    diff_dict[j] = abs(angles_copy[i] - angles_copy[j])

            # Ordering the dict to find the smallest angular distances
            diff_dict = dict(sorted(diff_dict.items(), key=lambda item: item[1]))

            cluster_size = 0
            for k in diff_dict.copy():
                if cluster_size < r and k in diff_dict: # Including i itself
                    cluster_angles[int(id_cluster)][int(k)] = angles_copy[k]
                    cluster_kappas[int(id_cluster)][int(k)] = kappas_copy[k]
                    # Once assigned, remove the node from list of possibilities
                    angles_copy.pop(k)
                    kappas_copy.pop(k)
                    diff_dict.pop(k)
                    cluster_size += 1
     
            id_cluster += 1

    return cluster_kappas, cluster_angles


def find_clusters_hybrid(kappas, uniform_angles_ordered, r):
    cluster_angles = {}
    cluster_kappas = {}
    cluster_size = 0

    id_cluster = 0
    cluster_angles[int(id_cluster)] = {}
    cluster_kappas[int(id_cluster)] = {}


    for node in uniform_angles_ordered:
        if cluster_size == r:  # Cluster is full
            cluster_size = 0
            id_cluster += 1
            cluster_angles[int(id_cluster)] = {}
            cluster_kappas[int(id_cluster)] = {}

        cluster_angles[int(id_cluster)][int(node)] = uniform_angles_ordered[node]['uniform_angle']
        cluster_kappas[int(id_cluster)][int(node)] = kappas[node]
        cluster_size += 1

    return cluster_kappas, cluster_angles


def find_clusters_uniform(kappas, uniform_angles_ordered, r):
    cluster_angles = {}
    cluster_kappas = {}
    cluster_size = 0

    id_cluster = 0
    cluster_angles[int(id_cluster)] = {}
    cluster_kappas[int(id_cluster)] = {}


    for node in uniform_angles_ordered:
        if cluster_size == r:  # Cluster is full
            cluster_size = 0
            id_cluster += 1
            cluster_angles[int(id_cluster)] = {}
            cluster_kappas[int(id_cluster)] = {}

        cluster_angles[int(id_cluster)][int(node)] = uniform_angles_ordered[node]
        cluster_kappas[int(id_cluster)][int(node)] = kappas[node]
        cluster_size += 1

    return cluster_kappas, cluster_angles


def store_membership(cluster_angles):
    membership = {}

    for i in cluster_angles:
        for node in cluster_angles[i]:
            membership[node] = i

    return membership


def renormalize_network(infile, kappas, angles):
    graphs = []
    pos_nodes = []
    membership_list = []

    links = read_links(infile)

    r = int(input('Enter the desired cluster size: '))
    total_renorm_steps = 1 + int(input('How many renormalization steps do you want to perform? '))
    beta = 2 #int(input('Enter the beta coefficient: '))
    # TODO do not hardcode this

    for renorm_step in range(total_renorm_steps + 1):
        # Form the new network
        #G, current_pos = form_network(angles, links)
        #G, current_pos, uniform_angles = form_network_uniform(angles, links, renorm_step)
        G, current_pos, uniform_angles = form_network_uniform_hybrid(angles, links, renorm_step)

        graphs.append(G)
        pos_nodes.append(current_pos)

        #cluster_kappas, cluster_angles = find_clusters(kappas, angles, r)
        #cluster_kappas, cluster_angles = find_clusters_uniform(kappas, uniform_angles, r)
        cluster_kappas, cluster_angles = find_clusters_hybrid(kappas, uniform_angles, r)


        # Perform the renormalization of the nodes and links
        kappas, angles = renormalize_nodes(cluster_kappas, cluster_angles, beta)

        links = renormalize_links(cluster_kappas, links)

        # Don't print communities in final step
        #if renorm_step < total_renorm_steps:
        current_membership = store_membership(cluster_angles)
        membership_list.append(current_membership)

    return graphs, pos_nodes, membership_list, kappas
