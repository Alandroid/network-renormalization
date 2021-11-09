'''
To plot run python converter.py <filename>
This reads <filename>.inf_log and <filename>.inf_coord

Modified code from 
https://towardsdatascience.com/visualising-the-mercator-graph-layout-embeddings-using-a-real-world-complex-network-bf065c316b7a
'''

import sys,json
import pandas as pd


def convert_to_json(filename):
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

# convert_to_json(sys.argv[1])