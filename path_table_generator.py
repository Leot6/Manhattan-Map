"""
compute the shortest path table for all node pairs in Manhattan.
    input:  NYC_NET.pickle
    output: path_table.csv
            mean_table.csv
            var_table.csv
"""

import time
import pickle
import copy
import numpy as np
import pandas as pd
import networkx as nx
from tqdm import tqdm

from config import *

with open(f'{PICKLE_PATH}/NYC_NET.pickle', 'rb') as f:
    NYC_NET = pickle.load(f)
G = copy.deepcopy(NYC_NET)


# quickly load the path from origin to destination from the precomputed path table
def get_path_from_path_table(path_table, onid, dnid):
    """Quickly recover the path from the path-table for a given origin-destination pair.
        Args:
            path_table: a table that store all shortest paths.
            onid: the node id of the origin
            dnid: the node id of the destination
        Returns:
            path: the shortest path from the origin to the destination
    """
    path = [dnid]
    pre_node = path_table[onid - 1, dnid - 1]
    while pre_node > 0:
        path.append(pre_node)
        pre_node = path_table[onid - 1, pre_node - 1]
    path.reverse()
    return path


def get_path_mean_var_and_dist(path):
    """Get the mean and variance of a given path.

        Args:
            path: the path from a origin to a destination, e.g. [1, 3, 4, 7].

        Returns:
            mean, var, dist
    """
    mean = 0.0
    var = 0.0
    dist = 0.0
    for i in range(len(path) - 1):
        u = path[i]
        v = path[i + 1]
        mean += NYC_NET.get_edge_data(u, v, default={'dur': None})['dur']
        var += NYC_NET.get_edge_data(u, v, default={'var': None})['var']
        dist += NYC_NET.get_edge_data(u, v, default={'dist': None})['dist']
    return round(mean, 2), round(var, 2), round(dist, 2)


def compute_tables(network=NYC_NET):
    """Compute the shortest paths among all nodes pairs and store the paths, along with means and variances, in tables.

        Args:
            network: the map.
            label: marking different tables when computing a set of parametric shortest paths

        Returns:
            saving the tables as csv files, named 'path-table.csv', 'mean-table.csv' and 'var-table.csv'
    """
    stime = time.time()
    print(f'Using data with {network.number_of_nodes()} nodes and {network.number_of_edges()} edges')
    print(f' computing all_pairs_dijkstra...')
    len_paths = dict(nx.all_pairs_dijkstra(network, cutoff=None, weight='dur'))
    print(f'all_pairs_dijkstra running time: {time.time() - stime:.5f} sec')
    print(' writing table value...')
    nodes_id = list(range(1, network.number_of_nodes() + 1))
    num_nodes = len(nodes_id)
    path_table = pd.DataFrame(-np.ones((num_nodes, num_nodes), dtype=int), index=nodes_id, columns=nodes_id)
    mean_table = pd.DataFrame(-np.ones((num_nodes, num_nodes)), index=nodes_id, columns=nodes_id)
    var_table = pd.DataFrame(-np.ones((num_nodes, num_nodes)), index=nodes_id, columns=nodes_id)
    dist_table = pd.DataFrame(-np.ones((num_nodes, num_nodes)), index=nodes_id, columns=nodes_id)
    for o in tqdm(nodes_id, desc='path-table row'):
        for d in tqdm(nodes_id, desc='path-table column', leave=False):
            try:
                path = len_paths[o][1][d]
                # # if var table is not needed, using the following line to get mean is faster
                # mean = round(len_paths[o][0][d], 2)
                mean, var, dist = get_path_mean_var_and_dist(path)
                # print(f'debug: path:{(o, d)}, mean:{mean}, std:{var ** 0.5}, dist:{dist}')
                mean_table.iloc[o - 1, d - 1] = mean
                var_table.iloc[o - 1, d - 1] = var
                dist_table.iloc[o - 1, d - 1] = dist
                if len(path) == 1:
                    continue
                else:
                    pre_node = path[-2]
                    path_table.iloc[o - 1, d - 1] = pre_node
            except KeyError:
                print('no path between', o, d)
    path_table.to_csv(f'{TABLE_PATH}/path-table.csv')
    mean_table.to_csv(f'{TABLE_PATH}/mean-table.csv')
    var_table.to_csv(f'{TABLE_PATH}/var-table.csv')
    dist_table.to_csv(f'{TABLE_PATH}/dist-table.csv')


def compute_a_set_of_lambda_path_tables(lambda_set):
    """Compute a set of parametric shortest paths (m+λ*v) table.
        Args:
            lambda_set: the value set of different lambda parameters.

        Returns:
            saving the tables as csv files, named 'path-table-0.csv', 'mean-table-0.csv' and 'var-table-0.csv'
    """
    for i in tqdm(range(0, len(lambda_set)), desc='computing a set of lambda path tables:'):
        lam = lambda_set[i]
        print(' updating lemada network')
        for u, v in G.edges():
            dur = NYC_NET.get_edge_data(u, v, default={'dur': None})['dur']
            var = NYC_NET.get_edge_data(u, v, default={'var': None})['var']
            if dur is np.inf:
                print('error: dur is np.inf !!!')
                quit()
            if lam == np.inf:
                weight = var
            else:
                weight = dur + lam * var
            G.edges[u, v]['dur'] = weight
        compute_tables(G, str(i))


if __name__ == '__main__':
    compute_tables()

    # K = [0, 0.2, 0.3155, 0.4976, 0.7849, 1.2381, 1.9529, 3.0803, 4.8588, 7.664, 12.0888, 19.0683, 30.0774, 47.4425,
    #      74.8335, 118.0386, 186.1882, 293.684, 463.2426, 705, np.inf]
    # compute_a_set_of_lambda_path_tables(K)

