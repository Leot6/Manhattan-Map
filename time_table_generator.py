"""
compute the shortest path table for all node pairs in Manhattan.
    input:  nodes.csv
            NYC_NET.pickle
    output: path_table.csv
            mean_table.csv
            var_table.csv
"""

import time
import os
import pickle
import numpy as np
import pandas as pd
import networkx as nx
from tqdm import tqdm


NYC_NOD = pd.read_csv('./map-data/nodes.csv')
with open('NYC_NET_WEEK.pickle', 'rb') as f:
    NYC_NET = pickle.load(f)


def get_path_mean_and_var(path):
    mean = 0.0
    var = 0.0
    for i in range(len(path) - 1):
        u = path[i]
        v = path[i + 1]
        mean += NYC_NET.get_edge_data(u, v, default={'dur': None})['dur']
        var += NYC_NET.get_edge_data(u, v, default={'var': None})['var']
    return round(mean, 2), round(var, 2)


def compute_tables(graph=NYC_NET, nodes=NYC_NOD, label=''):
    aa = time.time()
    print(' computing all_pairs_dijkstra...')
    len_paths = dict(nx.all_pairs_dijkstra(graph, cutoff=None, weight='dur'))
    print('all_pairs_dijkstra running time : %.05f seconds' % (time.time() - aa))
    print(' writing table value...')
    nodes_id = list(range(1, nodes.shape[0] + 1))
    num_nodes = len(nodes_id)
    path_table = pd.DataFrame(-np.ones((num_nodes, num_nodes), dtype=int), index=nodes_id, columns=nodes_id)
    mean_table = pd.DataFrame(-np.ones((num_nodes, num_nodes)), index=nodes_id, columns=nodes_id)
    var_table = pd.DataFrame(-np.ones((num_nodes, num_nodes)), index=nodes_id, columns=nodes_id)
    for o in tqdm(nodes_id, desc='path-table row'):
        for d in tqdm(nodes_id, desc='path-table column'):
            try:
                # the shortest path table
                path = len_paths[o][1][d]
                if len(path) == 1:
                    continue
                else:
                    pre_node = path[-2]
                    path_table.iloc[o - 1, d - 1] = pre_node
                # the shortest mean table
                # mean = round(len_paths[o][0][d], 2)
                mean, var = get_path_mean_and_var(path)
                mean_table.iloc[o - 1, d - 1] = mean
                var_table.iloc[o - 1, d - 1] = var
            except nx.NetworkXNoPath:
                print('no path between', o, d)

    path = './precomputed-tables/'
    if not os.path.exists(path):
        os.mkdir(path)
    if label != '':
        label = '_' + label
    path_table.to_csv('./precomputed-tables/path-table' + label + '.csv')
    mean_table.to_csv('./precomputed-tables/mean_table' + label + '.csv')
    var_table.to_csv('./precomputed-tables/var_table' + label + '.csv')


# quickly load the path from origin to destination from the precomputed path table
def get_path_from_path_table(path_table, onid, dnid):
    path = [dnid]
    pre_node = path_table[onid - 1, dnid - 1]
    while pre_node > 0:
        path.append(pre_node)
        pre_node = path_table[onid - 1, pre_node - 1]
    path.reverse()
    return path


if __name__ == '__main__':
    compute_tables()

