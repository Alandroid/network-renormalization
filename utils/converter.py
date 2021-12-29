"""
Utils script to convert input files between types
"""

import sys,json
import pandas as pd
import numpy as np
from itertools import takewhile


def convert_to_json(filename):
    """
    To plot, please run python converter.py <filename>
    This reads <filename>.inf_log and <filename>.inf_coord

    Modified code from 
    https://towardsdatascience.com/visualising-the-mercator-graph-layout-embeddings-using-a-real-world-complex-network-bf065c316b7a
    """
    edge = pd.read_csv(filename + '.txt', comment='#', header=None, sep='\s+', index_col= None)[[0,1]]
    edge.columns = ['source',  'target']

    df = pd.read_csv(filename + '.inf_coord', comment='#', header=None, sep='\s+', index_col=None)
    df.columns = ['index', 'kappa', 'theta', 'r']

    # Adjusting node indices to start in 0 - DEPRECATED (TODO: check if all networks will be this way)
    #df['index'] = df['index'] - 1

    save = {}
    save['nodes'] = df.T.to_dict()
    save['edges'] = edge.T.to_dict()

    with open(filename + '.json', 'w') as outfile:
        json.dump(save, outfile,indent=2)

    return save


def get_beta(filename):
    """
    Extracts the beta value from the .inf_coord file
    produced by the mercator algorithm
    """

    df = pd.read_csv(filename + '.inf_coord', header=None)
    df_beta = df[df[0].str.contains('beta')]
    beta  = float(df_beta.iloc[0].to_string().split("beta:")[1])
    
    return beta


def convert_adj_to_edgefile(filename):
    """
    Takes as input the name of a txt containing the adjacency matrix
    of a network and saves (+ returns) the file of the edges of the network
    """
    edge_matrix = pd.read_csv(filename + '.txt', comment='#', header=None, sep='\s+', index_col= None)
    edge_matrix = np.array(edge_matrix)

    edge_list = []
    for i in range(len(edge_matrix)):
        for j in range(len(edge_matrix[i])):
            if edge_matrix[i][j] != 0:
                edge_list.append((i, j))

    with open(filename + '_edges.txt', 'w') as outfile:
        for t in edge_list:
            line = " ".join(str(node) for node in t)
            outfile.write(line + "\n")

    return edge_list


def convert_edgefile_to_adj(graph, filename, index):
    """
    Takes as input a list of ordered pairs containing the edgelist
    of a network and saves (+ returns) the adjacency matrix txt file
    """
    edge_array = np.array(list(graph.edges))

    # Getting the dimension of the matrix
    dim = 1 + max(list(graph.nodes))

    adj_matrix = np.zeros((dim, dim))
    for edge in edge_array:
        adj_matrix[edge[0]][edge[1]] = 1.00
        adj_matrix[edge[1]][edge[0]] = 1.00

    with open(filename + '_adj_matrix_' + str(index) + '.txt', 'w') as outfile:
        for i in adj_matrix:
            line = " ".join(str(node) for node in i)
            outfile.write(line + "\n")
