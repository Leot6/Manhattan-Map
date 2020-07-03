"""
generate the network of Manhattan using networkx.
    input:  edges.csv
            nodes.csv
            time-on-week.csv
    output: ./pickle-files-gitignore/NYC_NET_WEEK.pickle
"""

import time
import pickle
import math
import numpy as np
import pandas as pd
import networkx as nx
from tqdm import tqdm
from config import *


def get_haversine_dist(olng, olat, dlng, dlat):
    """Compute the distance between two points.

        Args:
            olng: longitude of the origin.
            olat: latitude of the origin.
            dlng: longitude of the destination.
            dlat: latitude of the destination.

        Returns:
            dist: the distance in meter
    """
    dist = (6371000 * 2 * math.pi / 360 * np.sqrt((math.cos((olat + dlat) * math.pi / 360)
                                                   * (olng - dlng)) ** 2 + (olat - dlat) ** 2))
    return dist


def load_Manhattan_network():
    """Build the Manhattan network using networkx

        Args:
            nodes.csv, each row: (node_id, lng, lat).
            edges.csv, each row: (edge_id, source_node, sink_node).
            time-on-week.csv, the travel times on edges, each row: (edge_id, travel_time).

        Returns:
            saving the network as a pickle file, named 'NYC_NET_WEEK.pickle'.
    """
    stime = time.time()
    print('Loading edges and nodes data...')
    nodes = pd.read_csv('./map-data/nodes.csv')
    edges = pd.read_csv('./map-data/edges.csv')
    travel_time_edges = pd.read_csv('./map-data/time-on-week.csv', index_col=0)
    # consider the travels times on different hours as samples, and compute the sample mean and standard deviation
    mean_travel_times = travel_time_edges.mean(1)
    std_travel_times = travel_time_edges.std(1)
    G = nx.DiGraph()
    num_edges = edges.shape[0]
    rng = tqdm(edges.iterrows(), total=num_edges, ncols=100, desc='Generating Manhattan network...')
    for i, edge in rng:
        u = edge['source']
        v = edge['sink']
        u_pos = np.array([nodes.iloc[u - 1]['lng'], nodes.iloc[u - 1]['lat']])
        v_pos = np.array([nodes.iloc[v - 1]['lng'], nodes.iloc[v - 1]['lat']])

        mean_travel_time = round(mean_travel_times.iloc[i], 2)
        std = round(std_travel_times.iloc[i], 2)
        travel_dist = round(get_haversine_dist(u_pos[0], u_pos[1], v_pos[0], v_pos[1]), 2)
        unit_travel_time = round(mean_travel_time / travel_dist, 4)

        # artificial variance
        variance = round(std * 2 * unit_travel_time, 2)
        # variance = round(100 * unit_travel_time ** 2, 2)

        if mean_travel_time < 5:
            mean_travel_time += 5
        if variance < 1:
            variance += 1
        std_artificial = round(np.sqrt(variance), 2)
        G.add_edge(u, v, dur=mean_travel_time, var=variance, std=std_artificial, dist=travel_dist)
        G.add_node(u, pos=u_pos)
        G.add_node(v, pos=v_pos)

    # store_map_as_pickle_file
    with open(f'{PICKLE_PATH}NYC_NET_WEEK.pickle', 'wb') as f:
        pickle.dump(G, f)
    print('Saving the network as a pickle file...')
    print(f'...running time: {time.time() - stime:.5f} sec')


if __name__ == '__main__':
    load_Manhattan_network()
