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
    :param olng: longitude of the origin.
    :param olat: latitude of the origin.
    :param dlng: longitude of the destination.
    :param dlat: latitude of the destination.
    :return: the distance in meter
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
    nodes = pd.read_csv(f'{MAP_DATA_PATH}/nodes.csv')
    edges = pd.read_csv(f'{MAP_DATA_PATH}/edges.csv')
    travel_time_edges = pd.read_csv(f'{MAP_DATA_PATH}/time-on-week.csv', index_col=0)
    # consider the travels times on different hours as samples, and compute the sample mean and standard deviation
    mean_travel_times = travel_time_edges.mean(1)
    std_travel_times = travel_time_edges.std(1)
    G = nx.DiGraph()
    num_edges = edges.shape[0]
    rng = tqdm(edges.iterrows(), total=num_edges, ncols=100, desc='Generating Manhattan network...')
    for idx, edge in rng:
        u = edge['source']
        v = edge['sink']
        u_pos = np.array([nodes.iloc[u - 1]['lng'], nodes.iloc[u - 1]['lat']])
        v_pos = np.array([nodes.iloc[v - 1]['lng'], nodes.iloc[v - 1]['lat']])

        mean_travel_time = round(mean_travel_times.iloc[idx], 2)
        std = round(std_travel_times.iloc[idx], 2)
        travel_dist = round(get_haversine_dist(u_pos[0], u_pos[1], v_pos[0], v_pos[1]), 2)

        # # artificial variance
        # unit_travel_time = round(mean_travel_time / travel_dist, 4)
        # variance = round(std * 2 * unit_travel_time, 2)
        # # variance = round(100 * unit_travel_time ** 2, 2)
        # std = round(np.sqrt(variance), 2)

        if mean_travel_time < 5:
            mean_travel_time += 5
        if std < 1:
            std += 1
        variance = round(std ** 2, )
        G.add_edge(u, v, dur=mean_travel_time, var=variance, std=std, dist=travel_dist)
        G.add_node(u, pos=u_pos)
        G.add_node(v, pos=v_pos)
        # print('debug', mean_travel_time, std)

    print(f'    G has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges')

    # store_map_as_pickle_file
    print('Saving the network as a pickle file...')
    with open(f'{PICKLE_PATH}/NYC_NET.pickle', 'wb') as f:
        pickle.dump(G, f)

    print(f'...running time: {time.time() - stime:.5f} sec')


def load_Manhattan_network_uber():
    """Build the Manhattan network using networkx
    """
    stime = time.time()
    print('Loading edges and nodes data...')
    nodes = pd.read_csv(f'{MAP_DATA_PATH}/uber/nodes.csv')
    edges = pd.read_csv(f'{MAP_DATA_PATH}/uber/edges.csv')
    G = nx.DiGraph()
    num_edges = edges.shape[0]
    rng = tqdm(edges.iterrows(), total=num_edges, ncols=100, desc='Generating Manhattan network...')
    for idx, edge in rng:
        u = int(edge['start_node_id'])
        v = int(edge['end_node_id'])
        u_pos = np.array([nodes.iloc[u - 1]['lng'], nodes.iloc[u - 1]['lat']])
        v_pos = np.array([nodes.iloc[v - 1]['lng'], nodes.iloc[v - 1]['lat']])
        travel_dist = round(edge['dist_meter'], 2)
        mean_travel_time = round(edge['time_sec_mean'], 2)
        std = round(edge['time_sec_stddev'], 2)
        variance = round(std ** 2, 2)
        G.add_edge(u, v, dur=mean_travel_time, var=variance, std=std, dist=travel_dist)
        G.add_node(u, pos=u_pos)
        G.add_node(v, pos=v_pos)
        # print('debug ', 'mean_travel_time:', mean_travel_time, ' std:', std)

    print(f'    G has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges')

    merging_incident_nodes(G)

    # store_map_as_pickle_file
    print('Saving the network as a pickle file...')
    with open(f'{PICKLE_PATH}/NYC_NET_UBER.pickle', 'wb') as f:
        pickle.dump(G, f)

    print(f'...running time: {time.time() - stime:.5f} sec')


# bugs to fix, after remove incident nodes, we need to reindex node id
def merging_incident_nodes(G):
    dist_threshold = 50

    def get_edge_attributes(u, v):
        dur = G.get_edge_data(u, v, default={'dur': None})['dur']
        var = G.get_edge_data(u, v, default={'var': None})['var']
        std = G.get_edge_data(u, v, default={'std': None})['std']
        dist = G.get_edge_data(u, v, default={'dist': None})['dist']
        return dur, var, std, dist

    def remove_incident_edges(u, n, v):
        dur1, var1, std1, dist1 = get_edge_attributes(u, n)
        dur2, var2, std2, dist2 = get_edge_attributes(n, v)
        dur = dur1 + dur2
        var = var1 + var2
        std = round(var ** 0.5, 2)
        dist = dist1 + dist2
        G.add_edge(u, v, dur=dur, var=var, std=std, dist=dist)
        G.remove_edge(u, n)
        G.remove_edge(n, v)

    # remove one-way incident nodes
    incident_nodes = []
    for node in G.nodes:
        sources = list(G.predecessors(node))
        sinks = list(G.successors(node))
        if len(sources) == len(sinks) == 1 and sources != sinks:
            dist1 = G.get_edge_data(sources[0], node, default={'dist': None})['dist']
            dist2 = G.get_edge_data(node, sinks[0], default={'dist': None})['dist']
            if dist1 < dist_threshold or dist2 < dist_threshold:
                remove_incident_edges(sources[0], node, sinks[0])
                incident_nodes.append(node)
    G.remove_nodes_from(incident_nodes)
    print(f'remove {len(incident_nodes)} one-way incident nodes')
    print(f'    G has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges')

    # remove two-way incident nodes
    incident_nodes = []
    for node in G.nodes:
        sources = list(G.predecessors(node))
        sinks = list(G.successors(node))
        if len(sources) == len(sinks) == 2 and set(sources) == set(sinks):
            dist1 = G.get_edge_data(sources[0], node, default={'dist': None})['dist']
            dist2 = G.get_edge_data(node, sources[1], default={'dist': None})['dist']
            if dist1 < dist_threshold or dist2 < dist_threshold:
                remove_incident_edges(sources[0], node, sources[1])
                remove_incident_edges(sources[1], node, sources[0])
                incident_nodes.append(node)
    G.remove_nodes_from(incident_nodes)
    print(f'remove {len(incident_nodes)} two-way incident nodes')
    print(f'    G has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges')

    #  reindex node id
    node_list = sorted(list(G.nodes))
    assert_data = [G.number_of_nodes(), G.number_of_edges()]
    for (idx, node) in zip(range(1, G.number_of_nodes()+1), node_list):
        if idx != node:
            G.add_node(idx, pos=G.nodes[node]['pos'])
            sources = list(G.predecessors(node))
            for u in sources:
                dur, var, std, dist = get_edge_attributes(u, node)
                G.add_edge(u, idx, dur=dur, var=var, std=std, dist=dist)
            sinks = list(G.successors(node))
            for v in sinks:
                dur, var, std, dist = get_edge_attributes(node, v)
                G.add_edge(idx, v, dur=dur, var=var, std=std, dist=dist)
            G.remove_node(node)
    assert assert_data == [G.number_of_nodes(), G.number_of_edges()]


if __name__ == '__main__':
    # load_Manhattan_network()
    # load_Manhattan_network_uber()

    with open(f'{PICKLE_PATH}NYC_NET_UBER.pickle', 'rb') as f:
        G = pickle.load(f)
    print(G.has_node(45))
    path = nx.bidirectional_dijkstra(G, 1, 45, weight='dur')
    print(path)




