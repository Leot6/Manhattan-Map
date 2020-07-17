"""
plotting paths and nodes.
"""

import pickle
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from tqdm import tqdm
from config import PICKLE_PATH

with open(f'{PICKLE_PATH}NYC_NET_WEEK.pickle', 'rb') as f:
    NETWORK = pickle.load(f)


# # parameters for Manhattan map
# map width and height (km)
MAP_WIDTH = 10.71
MAP_HEIGHT = 20.85
# coordinates
# (Olng, Olat) lower left corner
Olng = -74.0300
Olat = 40.6950
# (Olng, Olat) upper right corner
Dlng = -73.9030
Dlat = 40.8825


def plot_path(onid, dnid, paths):
    """Plot paths on the Manhattan map and save the fig to a file.

        Args:
            onid: the node id of the origin.
            dnid: the node id of the destination.
            paths: the path set to be plotted, each one is a list of nodes

        Returns:
            show the plotted fig and save it to 'plotted_graph.jpg'.
    """
    fig = plt.figure(figsize=(MAP_WIDTH, MAP_HEIGHT))
    plt.xlim((Olng, Dlng))
    plt.ylim((Olat, Dlat))
    img = mpimg.imread('./map-data/map.png')
    plt.imshow(img, extent=[Olng, Dlng, Olat, Dlat], aspect=(Dlng - Olng) / (Dlat - Olat) * MAP_HEIGHT / MAP_WIDTH)
    fig.subplots_adjust(left=0.00, bottom=0.00, right=1.00, top=1.00)
    [olng, olat] = NETWORK.nodes[onid]['pos']
    [dlng, dlat] = NETWORK.nodes[dnid]['pos']
    plt.scatter(olng, olat, s=70, color='r', marker='^')
    plt.scatter(dlng, dlat, s=70, color='r', marker='s')
    for index, path in zip(range(len(paths)), paths):
        x = []
        y = []
        for node in path:
            [lng, lat] = NETWORK.nodes[node]['pos']
            x.append(lng)
            y.append(lat)
        if index == 0 or index == 1:
            plt.plot(x, y, marker='.')
        else:
            plt.plot(x, y, '--')

    plt.savefig('plotted_graph.jpg', dpi=300)
    plt.show()


def plot_node(nodes):
    """Plot paths on the Manhattan map and save the fig to a file.

        Args:
            nodes: a list of (lng, lat)
        Returns:
            show the plotted fig and save it to 'plotted_graph.jpg'.
    """
    fig = plt.figure(figsize=(MAP_WIDTH, MAP_HEIGHT))
    plt.xlim((Olng, Dlng))
    plt.ylim((Olat, Dlat))
    img = mpimg.imread('./map-data/map.png')
    plt.imshow(img, extent=[Olng, Dlng, Olat, Dlat], aspect=(Dlng - Olng) / (Dlat - Olat) * MAP_HEIGHT / MAP_WIDTH)
    fig.subplots_adjust(left=0.00, bottom=0.00, right=1.00, top=1.00)

    for (lng, lat) in nodes:
        plt.scatter(lng, lat, s=35, color='0.5')

    # plt.savefig('plotted_graph.jpg', dpi=300)
    plt.show()


if __name__ == "__main__":

    # path1 = [100, 102, 106, 113, 117, 120, 164, 199, 247, 299, 398, 484, 502, 515, 525, 543, 569, 596, 612, 633, 653,
    #          671, 691, 705, 725, 745, 768, 791, 811, 833, 855, 873, 892, 915, 938, 963, 980, 1004, 1166, 1188, 1247,
    #          1336, 1417, 1502, 1527, 1563, 1600, 1631, 1657, 1681, 1703, 1723, 1746, 1768, 1792, 1820, 1841, 1863,
    #          1890, 1910, 1940, 1966, 2000, 2026, 2048, 2069, 2087, 2110, 2128, 2152, 2170, 2187, 2206, 2225, 2244]
    # path2 = [100, 102, 106, 113, 117, 120, 130, 122, 111, 108, 90, 88, 78, 65, 61, 54, 47, 33, 29, 21, 18, 159, 192,
    #          566, 1612, 1915, 1988, 2130, 1974, 2001, 2067, 2094, 2101, 2108, 2047, 2070, 2088, 2111, 2127, 2151,
    #          2171, 2178, 2208, 2219, 2248, 2269, 2290, 2298, 2312, 2337, 2346, 2348, 2352, 2363, 2376, 2389, 2404,
    #          2324, 2225, 2244]
    # path3 = [100, 102, 106, 113, 117, 120, 130, 132, 135, 138, 140, 141, 146, 150, 153, 160, 161, 168, 170, 163, 167,
    #          235, 244, 315, 338, 367, 388, 411, 438, 460, 481, 617, 738, 865, 1004, 1166, 1188, 1247, 1336, 1417,
    #          1502, 1527, 1563, 1600, 1631, 1657, 1681, 1703, 1723, 1746, 1768, 1792, 1820, 1841, 1863, 1890, 1910,
    #          1940, 1966, 2000, 2026, 2048, 2069, 2087, 2110, 2128, 2152, 2170, 2187, 2206, 2225, 2244]
    # plot_path(100, 2244, [path1, path3, path2])

    node_list_1 = []
    node_list_2 = []
    df1 = pd.read_csv('./map-data/nodes.csv')
    df2 = pd.read_csv('./map-data/nodes-uber.csv')

    print(df1.head(5))
    print(df2.head(5))

    for idx, node in tqdm(df2.iterrows(), total=df2.shape[0], ncols=100, desc='iterrows'):
        node_list_1.append((node['lng'], node['lat']))
    plot_node(node_list_1)

    # with open('./map-data/osm_manhattan_node_dict.pickle', 'rb') as f:
    #     osm_manhattan_node_dict = pickle.load(f)
    # print(list(osm_manhattan_node_dict.items())[:5])
    # osm_manhattan_node_ = sorted(osm_manhattan_node_dict.items(), key=lambda x: (x[1][0], x[1][1]))
    # print(osm_manhattan_node_[100:110])
