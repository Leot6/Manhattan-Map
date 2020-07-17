"""
match the osm node id in the uber movement traffic speed data, and add gps information to the data, then save them to
two files nodes-uber.csv, edges-uber.csv

needed data files: movement-speeds-quarterly-by-hod-new-york-2020-Q1.csv, manhattan.osm
"""

import time
import pickle
import xml.dom.minidom
import pandas as pd
from tqdm import tqdm
from network_generator import get_haversine_dist


def extract_node_list_from_osm_file(osm_file_path):
    print('parse file...')
    dom = xml.dom.minidom.parse(osm_file_path)
    print(f'    ...running time : {time.time() - stime:.5f} sec')
    print('root file...')
    root = dom.documentElement
    print(f'    ...running time : {time.time() - stime:.5f} sec')
    print('build list...')
    nodelist = root.getElementsByTagName('node')
    print(f'    ...running time : {time.time() - stime:.5f} sec')
    print('num of nodes', len(nodelist))
    node_dict = {}
    for node in tqdm(nodelist, desc='add node info to a dict'):
        node_id = node.getAttribute('id')
        node_lng = float(node.getAttribute('lon'))
        node_lat = float(node.getAttribute('lat'))
        node_dict[node_id] = (node_lng, node_lat)
    print('num of nodes in dict', len(node_dict))
    with open('osm_manhattan_node_dict.pickle', 'wb') as f:
        pickle.dump(node_dict, f)


def extract_node_list_from_osm_file(osm_file_path):
    print('parse file...')
    dom = xml.dom.minidom.parse(osm_file_path)
    print(f'    ...running time : {time.time() - stime:.5f} sec')
    print('root file...')
    root = dom.documentElement
    print(f'    ...running time : {time.time() - stime:.5f} sec')
    print('build list...')
    nodelist = root.getElementsByTagName('node')
    print(f'    ...running time : {time.time() - stime:.5f} sec')
    print('num of nodes', len(nodelist))
    node_dict = {}
    for node in tqdm(nodelist, desc='add node info to a dict'):
        node_id = node.getAttribute('id')
        node_lng = float(node.getAttribute('lon'))
        node_lat = float(node.getAttribute('lat'))
        node_dict[node_id] = (node_lng, node_lat)
    print('num of nodes in dict', len(node_dict))
    with open('osm_manhattan_node_dict.pickle', 'wb') as f:
        pickle.dump(node_dict, f)


def select_traffic_data_by_hour(csv_file_path, year=2020, quarter=1, hour=12):
    # labels' names
    col_year = 'year'
    col_quarter = 'quarter'
    col_hour = 'hour_of_day'
    col_osm_onid = 'osm_start_node_id'
    col_osm_dnid = 'osm_end_node_id'
    col_speed_mean = 'speed_mph_mean'
    col_speed_std = 'speed_mph_stddev'

    # filter out data on the selected day
    print('reading traffic data file ...')
    df = pd.read_csv(csv_file_path)
    print('number of traffic info:', df.shape[0])
    # check the data type
    print(df.head(2))
    print('data type', df.dtypes)
    print(f'filtering out traffic at the selected time {year}-{quarter}-{hour}...')

    # load osm_manhattan_node_dict and print the first 5 items to check if anything wrong
    with open('osm_manhattan_node_dict.pickle', 'rb') as f:
        osm_manhattan_node_dict = pickle.load(f)
    print(list(osm_manhattan_node_dict.items())[:5])

    # check out how many road segments received enough traffic and contained in the data by hours.
    # also check out how many node will be extracted from that data by hours
    for t_hour in range(0, 24):
        df0 = df[df[col_hour] == t_hour]
        print(f'  number of traffic info in NYC at the selected time {year}-{quarter}-{t_hour}: {df0.shape[0]}')
        col_nid = 'osm_node_id'
        col_lng = 'lng'
        col_lat = 'lat'
        # merge the onid col and dnid col to one col
        df1 = df0.loc[:, [col_osm_onid]]
        df1.columns = [col_nid]
        df2 = df0.loc[:, [col_osm_dnid]]
        df2.columns = [col_nid]
        frames = [df1, df2]
        df3 = pd.concat(frames, ignore_index=True)
        df3.sort_values(col_nid, inplace=True)
        assert df0.shape[0] == df1.shape[0] == df2.shape[0]
        assert df0.shape[0] * 2 == df3.shape[0]
        # delete duplicates, and we get the node list in NYC used in uber traffic data
        df3 = df3.drop_duplicates([col_nid]).reset_index(drop=True)
        # add new col for geo info
        col_name = [col_nid, col_lng, col_lat]
        df3 = df3.reindex(columns=col_name)
        # add geo info from osm_manhattan_node_dict
        df4 = df3
        col_nid_idx = col_name.index(col_nid)
        col_lng_idx = col_name.index(col_lng)
        col_lat_idx = col_name.index(col_lat)
        for node_idx in range(df4.shape[0]):
            osm_nid = int(df4.iloc[node_idx, col_nid_idx])
            osm_nid_geo = osm_manhattan_node_dict.get(str(osm_nid))
            if osm_nid_geo:
                (osm_nid_lng, osm_nid_lat) = osm_nid_geo
                df4.iloc[node_idx, col_lng_idx] = osm_nid_lng
                df4.iloc[node_idx, col_lat_idx] = osm_nid_lat
        df4.sort_values(by=[col_lng, col_lat], inplace=True)
        df4 = df4.dropna(how='any').reset_index(drop=True)
        df4.insert(0, 'id', range(1, 1 + len(df4)))
        print('     computed number of nodes in Manhattan:', df4.shape[0])

    # df1 = df[df[col_hour] == hour]
    # print(f'  number of traffic info in NYC at the selected time {year}-{quarter}-{hour}: {df1.shape[0]}')
    # # filter out useful parameters: time, lng & lat, passenger number...
    # print('filtering out useful parameters...')
    # df2 = df1.loc[:, [col_hour, col_osm_onid, col_osm_dnid, col_speed_mean, col_speed_std]]
    # df2.sort_values(col_osm_onid, inplace=True)
    # print(df2.head(2))  # check the format
    # df2.to_csv(f'nyc-traffic-{year}-{quarter}-{hour}.csv', index=False)


def extract_node_list_from_traffic_data_and_add_geo(traffic_csv_file_path):
    col_nid = 'node_id'
    col_lng = 'lng'
    col_lat = 'lat'
    col_osm_nid = 'osm_node_id'
    col_osm_onid = 'osm_start_node_id'
    col_osm_dnid = 'osm_end_node_id'
    df = pd.read_csv(traffic_csv_file_path)
    # merge the onid col and dnid col to one col
    df1 = df.loc[:, [col_osm_onid]]
    df1.columns = [col_osm_nid]
    df2 = df.loc[:, [col_osm_dnid]]
    df2.columns = [col_osm_nid]
    frames = [df1, df2]
    df3 = pd.concat(frames, ignore_index=True)
    df3.sort_values(col_osm_nid, inplace=True)
    assert df.shape[0] == df1.shape[0] == df2.shape[0]
    assert df.shape[0] * 2 == df3.shape[0]
    # delete duplicates, and we get the node list in NYC used in uber traffic data
    df3 = df3.drop_duplicates([col_osm_nid]).reset_index(drop=True)
    # add new col for geo info
    col_name = [col_osm_nid, col_lng, col_lat]
    df3 = df3.reindex(columns=col_name)
    print(df3.head(2))
    print(df3.dtypes)
    print('number of nodes in NYC:', df3.shape[0])
    # load osm_manhattan_node_dict and print the first 5 items to check if anything wrong
    with open('osm_manhattan_node_dict.pickle', 'rb') as f:
        osm_manhattan_node_dict = pickle.load(f)
    print(list(osm_manhattan_node_dict.items())[:5])
    # add geo info from osm_manhattan_node_dict
    df4 = df3
    col_osm_nid_idx = col_name.index(col_osm_nid)
    col_lng_idx = col_name.index(col_lng)
    col_lat_idx = col_name.index(col_lat)
    for node_idx in tqdm(range(df4.shape[0]), desc='node table:'):
        osm_nid = int(df4.iloc[node_idx, col_osm_nid_idx])
        osm_nid_geo = osm_manhattan_node_dict.get(str(osm_nid))
        if osm_nid_geo:
            (osm_nid_lng, osm_nid_lat) = osm_nid_geo
            df4.iloc[node_idx, col_lng_idx] = osm_nid_lng
            df4.iloc[node_idx, col_lat_idx] = osm_nid_lat
    df4.sort_values(by=[col_lng, col_lat], inplace=True)
    df4 = df4.dropna(how='any').reset_index(drop=True)
    df4.insert(0, col_nid, range(1, 1 + len(df4)))
    print(df4.head(2))
    print(df4.tail(2))
    print(df4.dtypes)
    print('number of nodes in Manhattan:', df4.shape[0])
    df4.to_csv('nodes-uber.csv', index=False)


def extract_edge_list_from_traffic_data_and_add_travel_time(traffic_csv_file_path):
    col_eid = 'edge_id'
    col_onid = 'start_node_id'
    col_dnid = 'end_node_id'
    col_osm_onid = 'osm_start_node_id'
    col_osm_dnid = 'osm_end_node_id'
    col_speed_mean = 'speed_mph_mean'
    col_speed_std = 'speed_mph_stddev'
    col_dist = 'dist_meter'
    col_time_mean = 'time_sec_mean'
    col_time_std = 'time_sec_stddev'
    df = pd.read_csv(traffic_csv_file_path)
    df = df.loc[:, [col_osm_onid, col_osm_dnid, col_speed_mean, col_speed_std]]
    col_name = [col_onid, col_dnid, col_osm_onid, col_osm_dnid, col_speed_mean, col_speed_std, col_dist, col_time_mean, col_time_std]
    df = df.reindex(columns=col_name)
    print(df.head(2))
    print(df.dtypes)
    print('number of edges in NYC:', df.shape[0])
    # load node table and convert it to a dictionary
    node_table = pd.read_csv('nodes-uber.csv')
    print(node_table.head(2))
    node_dict = dict(zip(node_table['osm_node_id'], zip(node_table['node_id'], node_table['lng'], node_table['lat'])))
    print(list(node_dict.items())[:5])

    # add node id to the edge table
    df1 = df
    col_onid_idx = col_name.index(col_onid)
    col_dnid_idx = col_name.index(col_dnid)
    col_osm_onid_idx = col_name.index(col_osm_onid)
    col_osm_dnid_idx = col_name.index(col_osm_dnid)
    col_speed_mean_idx = col_name.index(col_speed_mean)
    col_speed_std_idx = col_name.index(col_speed_std)
    col_dist_idx = col_name.index(col_dist)
    col_time_mean_idx = col_name.index(col_time_mean)
    col_time_std_idx = col_name.index(col_time_std)
    for edge_idx in tqdm(range(df1.shape[0]), desc='edge table:'):
        osm_onid = int(df1.iloc[edge_idx, col_osm_onid_idx])
        osm_dnid = int(df1.iloc[edge_idx, col_osm_dnid_idx])
        onid_info = node_dict.get(osm_onid)
        dnid_info = node_dict.get(osm_dnid)
        if onid_info and dnid_info:
            (onid, olng, olat) = onid_info
            (dnid, dlng, dlat) = dnid_info
            speed_mean = df1.iloc[edge_idx, col_speed_mean_idx]
            speed_std = df1.iloc[edge_idx, col_speed_std_idx]
            dist = get_haversine_dist(olng, olat, dlng, dlat)
            time_mean = dist / (0.44704 * speed_mean)
            time_std = time_mean * (speed_std / speed_mean)
            df1.iloc[edge_idx, col_onid_idx] = onid
            df1.iloc[edge_idx, col_dnid_idx] = dnid
            df1.iloc[edge_idx, col_dist_idx] = dist
            df1.iloc[edge_idx, col_time_mean_idx] = time_mean
            df1.iloc[edge_idx, col_time_std_idx] = time_std
    df1.sort_values(by=[col_onid, col_dnid], inplace=True)
    df1 = df1.dropna(how='any').reset_index(drop=True)
    df1.insert(0, col_eid, range(1, 1 + len(df1)))
    df1[[col_onid]] = df1[[col_onid]].astype(int)
    df1[[col_dnid]] = df1[[col_dnid]].astype(int)
    print(df1.head(2))
    print(df1.tail(2))
    print(df1.dtypes)
    print('number of edges in Manhattan:', df1.shape[0])
    df1.to_csv('edges-uber.csv', index=False, float_format='%.2f')


if __name__ == "__main__":
    stime = time.time()
    year = 2019
    quarter = 3
    hour = 17

    # # generate the node dict form OpenStreetMap
    # osm_file_path = 'manhattan.osm'
    # extract_node_list_from_osm_file(osm_file_path)

    # # extract traffic data by hour
    # traffic_data_file_path = f'/Users/leot/Downloads/movement-speeds-quarterly-by-hod-new-york-{year}-Q{quarter}.csv'
    # select_traffic_data_by_hour(traffic_data_file_path, year, quarter, hour)

    # generate the node list and edge list from the above two data info
    traffic_data_by_hour = f'nyc-traffic-{year}-{quarter}-{hour}.csv'
    # extract_node_list_from_traffic_data_and_add_geo(traffic_data_by_hour)
    extract_edge_list_from_traffic_data_and_add_travel_time(traffic_data_by_hour)

    print(f'    ...running time : {time.time() - stime:.5f} sec')


