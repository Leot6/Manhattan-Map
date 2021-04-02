"""
filter out the trips starts/ends within Manhattan area
"""

import time
import pickle
import yaml
import csv
import pandas as pd
import numpy as np
import datetime
from dateutil.parser import parse
from tqdm import tqdm
from config import *

# the locations of nodes
NOD_LOC = pd.read_csv(f'{MAP_DATA_PATH}/nodes.csv').values.tolist()
# the travel time table, storing ETA among all node pairs
with open(f'{PICKLE_PATH}/NYC_TTT.pickle', 'rb') as f:
    NOD_TTT = pickle.load(f)


def is_point_in_poly(lng, lat):
    """Find out whether a geo point is in the Manhattan poly.

        Args:
            lng: longitude of the point.
            lat: latitude of the point.

        Returns:
            True/False
    """
    # coordinates around Manhattan
    point_list = [(-74.022, 40.697), (-73.972, 40.711), (-73.958, 40.749), (-73.938, 40.771), (-73.937, 40.786),
                  (-73.928, 40.794), (-73.926, 40.801), (-73.932, 40.808), (-73.933, 40.835), (-73.924, 40.851),
                  (-73.911, 40.866), (-73.909, 40.873), (-73.927, 40.879), (-74.011, 40.751)]

    iSum = 0
    iCount = len(point_list)
    if iCount < 3:
        return False
    for i in range(iCount):
        # vlng: vertex longtitude,  vlat: vertex latitude
        vlng1 = point_list[i][0]
        vlat1 = point_list[i][1]
        if i == iCount - 1:
            vlng2 = point_list[0][0]
            vlat2 = point_list[0][1]
        else:
            vlng2 = point_list[i + 1][0]
            vlat2 = point_list[i + 1][1]
        if ((lat >= vlat1) and (lat < vlat2)) or ((lat >= vlat2) and (lat < vlat1)):
            if abs(vlat1 - vlat2) > 0:
                pLon = vlng1 - ((vlng1 - vlng2) * (vlat1 - lat)) / (vlat1 - vlat2)
                if pLon < lng:
                    iSum += 1
    if iSum % 2 != 0:
        return True
    else:
        return False


def longer_than_3_min(onid, dnid):
    """Find out whether a trip is longer than 3 min, so that we can remove trips that are too short.

        Args:
            onid: the node id of the origin.
            dnid: the node id of the destination.

        Returns:
            True/False
    """
    if NOD_TTT[onid - 1, dnid - 1] > 180:
        return True
    else:
        return False


def map_nearest_node(lng, lat):
    """Find the nearest node in the network for a geo point.

        Args:
            lng: longitude of the point.
            lat: latitude of the point.

        Returns:
            id of the nearest node
    """
    nearest_node_id = None
    d = np.inf
    for nid, nlng, nlat in NOD_LOC:
        # d_ = get_haversine_distance(lng, lat, nlng, nlat)
        d_ = abs(lng-nlng) + abs(lat-nlat)
        if d_ < d:
            d = d_
            nearest_node_id = nid
    return int(nearest_node_id)


def print_num_of_trips_on_each_day(csv_file_path, year='2016', month='05'):
    """Find out the number of trips on each day.

        Args:
            csv_file_path: the path of the taxi trip file of the whole month
            year: the year of the taxi data
            month: the month of the taxi data

        Returns:
            printing the numbers in the terminal
    """
    # # for green taxi
    # pickup_time = 'lpep_pickup_datetime'
    # for yellow taxi
    pickup_time = 'tpep_pickup_datetime'
    print('reading taxi trip file ...')
    df = pd.read_csv(csv_file_path, usecols=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13], index_col=False)
    print('number of all trips:', df.shape[0])
    # find out the number of trips on everyday in the selected month
    for i in range(1, 31):
        if i < 10:
            day = '0' + str(i)
        else:
            day = '' + str(i)
        date = year + '-' + month + '-' + day
        df1 = df.loc[lambda x: x[pickup_time].str.startswith(date)]
        print('number of trips on selected day (%s): %d' % (date, df1.shape[0]))


def select_trips_on_a_day(csv_file_path, year='2016', month='05', day='25'):
    """Filter out the trips in Manhattan on the selected day

        Args:
            csv_file_path: the path of the taxi trip file of the whole month
            year: the year of the taxi data
            month: the month of the taxi data
            day: the day of the taxi data

        Returns:
            saving the taxi trip data in a csv file, named 'manhattan-taxi-{year}{month}{day}.csv'
    """
    # the selected day
    date = year + '-' + month + '-' + day
    # proposed saving file name
    manhattan_taxi_file_on_selected_day = f'{TAXI_DATA_PATH}/manhattan-taxi-{year}{month}{day}.csv'

    # labels' names
    # # for green taxi
    # pickup_time = 'lpep_pickup_datetime'
    # dropoff_time = 'Lpep_dropoff_datetime'
    # olng = 'Pickup_longitude'
    # olat = 'Pickup_latitude'
    # dlng = 'Dropoff_longitude'
    # dlat = 'Dropoff_latitude'
    # passenger_count = 'Passenger_count'
    # trip_dist = 'Trip_distance'

    # for yellow taxi
    pickup_time = 'tpep_pickup_datetime'
    dropoff_time = 'tpep_dropoff_datetime'
    olng = 'pickup_longitude'
    olat = 'pickup_latitude'
    dlng = 'dropoff_longitude'
    dlat = 'dropoff_latitude'
    passenger_count = 'passenger_count'
    trip_dist = 'trip_distance'

    # get the labels' names in csv file, especially for pickup time, and update the names above
    print('reading taxi trip file ...')
    df = pd.read_csv(csv_file_path, usecols=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13], index_col=False)
    print('number of all trips:', df.shape[0])
    print(df.head(2))
    print('get the labels names in csv file...')
    print(df.columns.values)

    # # find out the number of trips on everyday in the selected month
    # for i in range(1, 31):
    #     if i < 10:
    #         day = '0' + str(i)
    #     else:
    #         day = '' + str(i)
    #     date = year + '-' + month + '-' + day
    #     df1 = df.loc[lambda x: x[pickup_time].str.startswith(date)]
    #     print('number of trips on selected day (%s): %d' % (date, df1.shape[0]))

    # filter out trips on the selected day
    print('filtering out trips on the selected day...')
    df1 = df.loc[lambda x: x[pickup_time].str.startswith(date)]
    df1[pickup_time] = pd.to_datetime(df1[pickup_time])
    df1.sort_values(pickup_time, inplace=True)
    print(f'  number of trips in NYC on selected day {date}: {df1.shape[0]}')

    # filter out useful parameters: time, lng & lat, passenger number...
    print('filtering out useful parameters...')
    df2 = df1.loc[:, [pickup_time, passenger_count, olng, olat, dlng, dlat, trip_dist, dropoff_time]]
    print(df2.head(2))  # check the format
    # rename the column index
    print('renaming the column index...')
    df2 = df2.loc[:, [pickup_time, passenger_count, olng, olat, dlng, dlat, trip_dist, dropoff_time]]
    df2.columns = ['ptime', 'npass', 'olng', 'olat', 'dlng', 'dlat', 'dist', 'dtime']

    # roughly filter out the trips in a square area
    print('filtering out the trips in Manhattan...')
    print(' roughly filtering out the trips in a square area...')
    df3 = df2[(df2['olng'] > -74.0300) & (df2['olng'] < -73.9030)
              & (df2['olat'] > 40.6950) & (df2['olat'] < 40.8825)
              & (df2['dlng'] > -74.0300) & (df2['dlng'] < -73.9030)
              & (df2['dlat'] > 40.6950) & (df2['dlat'] < 40.8825)]
    print('  number of trips after rough area filter:', df3.shape[0])
    # filter out the trips starting within Manhattan
    print(' filtering out the trips starting within Manhattan...')
    df4 = df3[df3.apply(lambda x: is_point_in_poly(x['olng'], x['olat']), axis=1)]
    # filter out the trips ending within Manhattan
    print(' filtering out the trips ending within Manhattan...')
    df5 = df4[df4.apply(lambda x: is_point_in_poly(x['dlng'], x['dlat']), axis=1)]
    print('  number of trips in Manhattan:', df5.shape[0])
    df5.to_csv(manhattan_taxi_file_on_selected_day, index=False)


def map_geo_to_node_id(csv_file_path):
    """Add the nearest node id of the origin and destination locations in the csv file,
    and remove trips that are shorter than 3 min.

        Args:
            csv_file_path: the path of the taxi trip file on the selected day

        Returns:
            saving the processed taxi trip data in a csv file, named 'manhattan-taxi-{year}{month}{day}.csv'
    """
    print('mapping geo location to node id...')
    df = pd.read_csv(csv_file_path)
    col_name = df.columns.tolist()
    col_name.insert(col_name.index('olng'), 'onid')
    col_name.insert(col_name.index('dlng'), 'dnid')
    df = df.reindex(columns=col_name)
    col_onid_idx = col_name.index('onid')
    col_dnid_idx = col_name.index('dnid')
    col_olng_idx = col_name.index('olng')
    col_olat_idx = col_name.index('olat')
    col_dlng_idx = col_name.index('dlng')
    col_dlat_idx = col_name.index('dlat')
    for req_idx in tqdm(range(df.shape[0]), desc='trips row'):
        olng = df.iloc[req_idx, col_olng_idx]
        olat = df.iloc[req_idx, col_olat_idx]
        dlng = df.iloc[req_idx, col_dlng_idx]
        dlat = df.iloc[req_idx, col_dlat_idx]
        df.iloc[req_idx, col_onid_idx] = map_nearest_node(olng, olat)
        df.iloc[req_idx, col_dnid_idx] = map_nearest_node(dlng, dlat)
    df[['onid']] = df[['onid']].astype(int)
    df[['dnid']] = df[['dnid']].astype(int)

    # filter out the trips longer than 3 min
    print('filtering out the trips longer than 3 min...')
    df1 = df[df.apply(lambda x: longer_than_3_min(x['onid'], x['dnid']), axis=1)]
    print('  number of trips longer than 3 min :', df1.shape[0])
    df1.to_csv(csv_file_path, index=False)


def merge_two_days_trips(year, month, day1, day2, expected_num_trip=0):
    """Merge some trips on day 2 to day 1, and save them to a new csv file
    """
    df_day1 = pd.read_csv(f'{TAXI_DATA_PATH}/manhattan-taxi-{year}{month}{day1}.csv')
    print('number of all taxi trips on day 1:', df_day1.shape[0])
    df_day2 = pd.read_csv(f'{TAXI_DATA_PATH}/manhattan-taxi-{year}{month}{day2}.csv')
    print('number of all taxi trips on day 2:', df_day2.shape[0])

    print('merging...')
    day_difference = int(day1) - int(day2)
    df_day2['ptime'] = df_day2['ptime'].map(lambda x: str(parse(x) + datetime.timedelta(days=day_difference)))
    df_day2['dtime'] = df_day2['dtime'].map(lambda x: str(parse(x) + datetime.timedelta(days=day_difference)))

    if expected_num_trip:
        fraction = (expected_num_trip - df_day1.shape[0]) / df_day2.shape[0]
    else:
        fraction = 1
    step = int(1/fraction)
    df_day2 = df_day2.iloc[1::step]  # [start：end：step]

    # # some time we can not use uniform step to sample the num of trips we need,
    # # then we could uniformly sample the num of trips droped
    # step = 3
    # df_day2 = df_day2.drop(df_day2.index[list(range(0, df_day2.shape[0], step))])  # range(start, step, end]

    merged_trips = [df_day1, df_day2]
    df13 = pd.concat(merged_trips, ignore_index=True)
    df13.sort_values('ptime', inplace=True)
    print('number of all taxi trips:', df13.shape[0])
    print('saving to file...')
    df13.to_csv(f'{TAXI_DATA_PATH}/manhattan-taxi-{year}{month}{day1}-{df13.shape[0]}.csv', index=False)


def merge_green_taxi_and_yellow_taxi_together(year='2016', month='05', day='25'):
    df8 = pd.read_csv(f'{TAXI_DATA_PATH}/manhattan-green-taxi-{year}{month}{day}.csv')
    df8['taxi'] = 'green'
    print('number of green taxi trips:', df8.shape[0])
    df9 = pd.read_csv(f'{TAXI_DATA_PATH}/manhattan-yellow-taxi-{year}{month}{day}.csv')
    df9['taxi'] = 'yellow'
    print('number of yellow taxi trips:', df9.shape[0])
    frames = [df8, df9]
    df10 = pd.concat(frames, ignore_index=True)
    df10.sort_values('ptime', inplace=True)
    print('number of all taxi trips:', df10.shape[0])
    df10.to_csv(f'manhattan-taxi-{year}{month}{day}.csv', index=False)


def filter_out_needed_trips(unprocessed_trip_file, year='2016', month='05', day='25'):
    """The main function, running the above functions and process the trip data file

        Args:
            unprocessed_trip_file: the path of the taxi trip file of the whole month
            year: the year of the taxi data
            month: the month of the taxi data
            day: the day of the taxi data

        Returns:
            saving the processed taxi trip data in a csv file, named 'manhattan-taxi-{year}{month}{day}.csv',
            and storing that trip data as a pickle file, named 'NYC_REQ_DATA_{year}{month}{day}.pickle'
    """
    stime = time.time()

    # select the taxi trips on the day needed
    select_trips_on_a_day(unprocessed_trip_file, year, month, day)

    # add node id information to the trip data
    csv_file_path = f'{TAXI_DATA_PATH}/manhattan-taxi-{year}{month}{day}.csv'
    map_geo_to_node_id(csv_file_path)

    # store taxi trips as pickle file
    print('store taxi trips to pickle file')
    REQ_DATA = pd.read_csv(csv_file_path)
    with open(f'{PICKLE_PATH}/NYC_REQ_DATA_{year}{month}{day}.pickle', 'wb') as f:
        pickle.dump(REQ_DATA, f)
    print(f'...running time : {time.time() - stime:.5f} sec')


def filter_out_trips_during_pick_hour(year, month, day):
    df = pd.read_csv(f'./taxi-trips/manhattan-taxi-{year}{month}{day}.csv')
    print(f'total num of trips on {year}{month}{day}: {df.shape[0]}')

    df1 = df.loc[lambda x: x['ptime'].str.startswith(f'{year}-{month}-{day} 18')]
    df2 = df.loc[lambda x: x['ptime'].str.startswith(f'{year}-{month}-{day} 19')]
    df3 = pd.concat([df1, df2], ignore_index=True)
    print(df3.head(2))
    print()
    print(f'num of requests during peak hours: {df3.shape[0]}')
    print('saving to file...')
    df3.to_csv(f'manhattan-taxi-{year}{month}{day}-peak.csv', index=False)
    with open(f'{PICKLE_PATH}/NYC_REQ_DATA_{year}{month}{day}_peak.pickle', 'wb') as f:
        pickle.dump(df3, f)


def convert_ptime_to_seconds(year, month, day):
    df = pd.read_csv(f'{TAXI_DATA_PATH}/manhattan-taxi-{year}{month}{day}.csv')
    print(f'total num of trips on {year}{month}{day}: {df.shape[0]}')
    df['ptime'] = df['ptime'].map(lambda x: (parse(x) - parse(f'{year}-{month}-{day} 00:00:00')).seconds)
    df[['ptime']] = df[['ptime']].astype(int)
    df.to_csv(f'manhattan-taxi-{year}{month}{day}.csv', index=False)


if __name__ == '__main__':
    year = '2016'
    month = '05'
    day = '25'
    unprocessed_trip_file = f'yellow_tripdata_{year}-{month}.csv'

    # print_num_of_trips_on_each_day(unprocessed_trip_file, year, month)
    # filter_out_needed_trips(unprocessed_trip_file, year, month, day)
    # day2 = '04'
    # merge_two_days_trips(year, month, day, day2, 1000000)

    # filter_out_trips_during_pick_hour(year, month, day)

    convert_ptime_to_seconds(year, month, day)



