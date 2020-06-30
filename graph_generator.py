"""
generate the graph of Manhattan using networkx.
    input:  edges.csv
            nodes.csv
            time-on-week.csv
    output: ./pickle-files/NYC_NET.pickle
"""

import time
import pickle
import math
import os
import numpy as np
import pandas as pd
import networkx as nx
from tqdm import tqdm


# get the distance based on haversine formula
def get_haversine_distance(olng, olat, dlng, dlat):
    dist = (6371000 * 2 * math.pi / 360 * np.sqrt((math.cos((olat + dlat) * math.pi / 360)
                                                   * (olng - dlng)) ** 2 + (olat - dlat) ** 2))
    return dist


def load_Manhattan_graph():
    aa = time.time()
    print('Loading edges and nodes data...')
    edges = pd.read_csv('./map-data/edges.csv')
    nodes = pd.read_csv('./map-data/nodes.csv')
    travel_time_edges = pd.read_csv('./map-data/time-on-week.csv', index_col=0)
    # consider the travels times on different hours as samples, and compute the sample mean and standard deviation
    mean_travel_times = travel_time_edges.mean(1)
    std_travel_times = travel_time_edges.std(1)
    G = nx.DiGraph()
    num_edges = edges.shape[0]
    rng = tqdm(edges.iterrows(), total=num_edges, ncols=100, desc='Generating Manhattan graph...')
    for i, edge in rng:
        u = edge['source']
        v = edge['sink']
        u_pos = np.array([nodes.iloc[u - 1]['lng'], nodes.iloc[u - 1]['lat']])
        v_pos = np.array([nodes.iloc[v - 1]['lng'], nodes.iloc[v - 1]['lat']])

        mean_travel_time = round(mean_travel_times.iloc[i], 2)
        std = round(std_travel_times.iloc[i], 2)
        travel_dist = round(get_haversine_distance(u_pos[0], u_pos[1], v_pos[0], v_pos[1]), 2)

        unit_travel_time = round(mean_travel_time / travel_dist, 4)
        # print(mean_travel_time, travel_dist, coe)

        # artificial variance
        variance1 = round(std * 2 * unit_travel_time, 2)
        variance = round(100 * unit_travel_time ** 2, 2)
        # print(u, v, 'mean_travel_time', mean_travel_time, 'std', std, 'travel_dist', travel_dist, 'var', variance, variance1)

        if mean_travel_time < 5:
            mean_travel_time += 5
        if variance < 1:
            variance += 1
        G.add_edge(u, v, dur=mean_travel_time, var=variance, dist=travel_dist)
        G.add_node(u, pos=u_pos)
        G.add_node(v, pos=v_pos)

    # store_map_as_pickle_file
    path = './pickle-files/'
    if not os.path.exists(path):
        os.mkdir(path)
    with open('./pickle-files/NYC_NET_WEEK.pickle', 'wb') as f:
        pickle.dump(G, f)
    print('Saving the graph as a pickle file...')

    print('...running time : %.05f seconds' % (time.time() - aa))


if __name__ == '__main__':
    load_Manhattan_graph()
