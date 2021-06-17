import numpy as np
np.seterr("raise")
import math
import networkx as nx


def search_clusters(key, dic):
    if hasattr(dic,'items'):
        for k in dic:
            for value in dic[k]:
                if value == key:
                    return k


def renormalize_nodes(cluster_kappas, cluster_angles, beta):
    renormalized_angles = {}
    renormalized_kappas = {}

    # Renormalizing the hidden degrees
    for i in cluster_kappas:
        kappas = np.array(list(cluster_kappas[i].values())[1:])
        if kappas.size > 0:
            renormalized_kappas[i] = np.sum(kappas**beta)**(1/beta)
        else: # If we have a single node, just pass it forward to the next layer
            renormalized_kappas[i] = list(cluster_kappas[i].values())[0] ## TODO correct this horrible gambiarra
       
    # Renormalizing the angles
    for i in cluster_angles:
        angles = np.array(list(cluster_angles[i].values())[1:])
        kappas = np.array(list(cluster_kappas[i].values())[1:])

        # Treating the case of a single node
        if angles.size == 0:
            angles = np.array(list(cluster_angles[i].values())[0])
        if kappas.size == 0:
            kappas = np.array(list(cluster_kappas[i].values())[0])

        try:
            numerator = (angles**beta).dot(kappas**beta)
        except:
            numerator = angles*kappas**beta

        denominator = renormalized_kappas[i]
        renormalized_angles[i] = (numerator**(1/beta))/denominator

    return renormalized_kappas, renormalized_angles


def renormalize_links(cluster_kappas, cluster_angles, links):
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


def renormalize_network(infile, index, theta, kappa):
    graphs = []
    pos_nodes = []

    renormalized_angles



    for renorm_step_indx in range(nmbr_renorm_steps):



    N = len(renormalized_angles) # Updating the number of nodes
    R = N/(2*math.pi)            # In S1, R is constant for each step

    # Forming the new network
    G = nx.Graph()

    # Adding and drawing the nodes
    position = {}
    for cluster_id in renormalized_angles:
        position[cluster_id] = (R * math.cos(float(renormalized_angles[cluster_id])), 
                                R * math.sin(float(renormalized_angles[cluster_id])))
        G.add_node(cluster_id)

    pos_nodes.append(nx.spring_layout(G, pos=position, fixed=list(position.keys())))

    # Adding and drawing the links
    G.add_edges_from(renormalized_links)   

    membership = {}
    for node in renormalized_angles:
        membership[node] = node

    graphs.append(G)
    membership_list.append(membership)









    G = nx.Graph()
    N = len(theta)
    R = N/(2*math.pi) # On S1 this is constant for each coarsening step

    # Distributing the nodes
    #for i in range(N):
    G.add_nodes_from(index)

    # Distributing the links
    links = []
    links_file = open(infile + '.txt', 'r+')
    for row in links_file:
        first = int(row.split(" ")[0])
        second = int(row.split(" ")[1].split("\n")[0])
        links.append((first, second))
        
        
        
    G.add_edge(first, second)

    # Here we only consider non-directed, weightless networks
    links = list(set(map(tuple, map(sorted, links))))


    # Renormalization step:

    r = int(input('Enter the desired cluster size: '))
    nmbr_renorm_steps = int(input('How many renormalization steps do you want to perform? '))

    angles_indexed = dict(zip(index, theta))
    kappas_indexed = dict(zip(index, kappa))


    membership_list = []

    # for renorm_step_indx in range(nmbr_renorm_steps):


        
        ###########################################
        # Pre-renormalization:

        cluster_angles = {}
        cluster_kappas = {}
        diff_dict = {}

        angles_indexed_copy = angles_indexed.copy()
        kappas_indexed_copy = kappas_indexed.copy()


        # TODO make this giant loop simpler
        m = 0
        # TODO do we always want to start assigning the 
        # nodes from the 1st of them?
        for i in angles_indexed:
            if i in angles_indexed_copy:
                cluster_angles[int(m)] = {}
                cluster_kappas[m] = {}
                diff_dict[i] = math.inf

                for j in angles_indexed:
                    if j in angles_indexed_copy: # Creating a dict to find the closest neighbors
                        diff_dict[j] = abs(angles_indexed_copy[i] - angles_indexed_copy[j])

                # Ordering the dict to find the smallest angular distances
                diff_dict = dict(sorted(diff_dict.items(), key=lambda item: item[1]))

                cluster_size = 0
                for k in diff_dict.copy():
                    if cluster_size < r and k in diff_dict: # Including i itself
                        cluster_angles[int(m)][int(k)] = angles_indexed_copy[k]
                        cluster_kappas[int(m)][int(k)] = kappas_indexed_copy[k]
                        # Once assigned, remove the node from list of possibilities
                        angles_indexed_copy.pop(k) 
                        kappas_indexed_copy.pop(k)
                        diff_dict.pop(k)
                        cluster_size += 1

                # TODO check that this should be here and not inside the for loop        
                m += 1

        position = {}
        # Positioning the nodes
        for i in range(len(angles_indexed)):
            position[i] = (R*math.cos(angles_indexed[i]), R*math.sin(angles_indexed[i]))
        pos_nodes.append(nx.spring_layout(G, pos=position, fixed=list(position.keys())))

        # Coloring nodes according to their next cluster
        membership = {}
        for i in cluster_angles:
            for node in cluster_angles[i]:
                membership[node] = i


        print(membership)
        #if renorm_step_indx == 0:
        graphs.append(G)
        membership_list.append(membership)



    ###########################################
    # Post-renormalization:

        beta = 2 # TODO do not hardcode this

        # Perform the renormalization of the nodes and links
        renormalized_kappas, renormalized_angles = renormalize_nodes(cluster_kappas, cluster_angles, beta)
        renormalized_links = renormalize_links(cluster_kappas, cluster_angles, links)

        # N = len(renormalized_angles) # Updating the number of nodes
        # R = N/(2*math.pi)            # In S1, R is constant for each step

        # # Forming the new network
        # G = nx.Graph()

        # # Adding and drawing the nodes
        # position = {}
        # for cluster_id in renormalized_angles:
        #     position[cluster_id] = (R * math.cos(float(renormalized_angles[cluster_id])), 
        #                             R * math.sin(float(renormalized_angles[cluster_id])))
        #     G.add_node(cluster_id)

        # pos_nodes.append(nx.spring_layout(G, pos=position, fixed=list(position.keys())))

        # # Adding and drawing the links
        # G.add_edges_from(renormalized_links)   

        # membership = {}
        # for node in renormalized_angles:
        #     membership[node] = node

        # graphs.append(G)
        # membership_list.append(membership)

        # Preparing lists for the next iteration
        links = list(set(map(tuple, map(sorted, renormalized_links))))
        angles_indexed = renormalized_angles
        kappas_indexed = renormalized_kappas

    return graphs, pos_nodes, membership_list
