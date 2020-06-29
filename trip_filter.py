"""
filter out the trips starts/ends within Manhattan area
"""

import time
import pickle
import pandas as pd
import numpy as np
import sys
from dateutil.parser import parse
import datetime

with open('NYC_NOD_LOC.pickle', 'rb') as f:
    NOD_LOC = pickle.load(f)
with open('NYC_TTT_WEEK.pickle', 'rb') as f:
    NOD_TTT = pickle.load(f)


def IsPtInPoly(lng, lat):
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


def LongerThan2Min(olng, olat, dlng, dlat):
    onid = find_nearest_node(olng, olat)
    dnid = find_nearest_node(dlng, dlat)
    if NOD_TTT[onid - 1, dnid - 1] > 120:
        return True
    else:
        return False


def find_nearest_node(lng, lat):
    nearest_node_id = None
    d = np.inf
    for nid, nlng, nlat in NOD_LOC:
        # d_ = get_haversine_distance(lng, lat, nlng, nlat)
        d_ = abs(lng-nlng) + abs(lat-nlat)
        if d_ < d:
            d = d_
            nearest_node_id = nid
    return int(nearest_node_id)


if __name__ == '__main__':
    stime = time.time()

    # # labels' names
    # # for green taxi
    # pickup_time = 'lpep_pickup_datetime'
    # dropoff_time = 'Lpep_dropoff_datetime'
    # olng = 'Pickup_longitude'
    # olat = 'Pickup_latitude'
    # dlng = 'Dropoff_longitude'
    # dlat = 'Dropoff_latitude'
    # passenger_count = 'Passenger_count'
    # trip_dist = 'Trip_distance'

    # # for yellow taxi in 2015
    # file_name = 'yellow_tripdata_2015-05.csv'
    # pickup_time = 'tpep_pickup_datetime'
    # dropoff_time = 'tpep_dropoff_datetime'
    # olng = 'pickup_longitude'
    # olat = 'pickup_latitude'
    # dlng = 'dropoff_longitude'
    # dlat = 'dropoff_latitude'
    # passenger_count = 'passenger_count'
    # trip_dist = 'trip_distance'

    # for taxi trip in 2013
    file_name = 'trip_data_5.csv'
    pickup_time = ' pickup_datetime'
    dropoff_time = ' dropoff_datetime'
    olng = ' pickup_longitude'
    olat = ' pickup_latitude'
    dlng = ' dropoff_longitude'
    dlat = ' dropoff_latitude'
    passenger_count = ' passenger_count'
    trip_dist = ' trip_distance'

    # # read all trips
    # CSV_FILE_PATH = '/Users/leot/Downloads/' + file_name
    # df = pd.read_csv(CSV_FILE_PATH, usecols=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13], index_col=False)
    # print('number of all trips:', df.shape[0])
    # print(df.head(2))
    # print(df.columns.values)  # get the label for pickup time in csv file

    # the selected day
    year = '2013'
    month = '05'
    day = '05'
    date = year + '-' + month + '-' + day

    # # find out the number of trips on everyday in the selected month
    # for i in range(1, 31):
    #     if i < 10:
    #         day = '0' + str(i)
    #     else:
    #         day = '' + str(i)
    #     date = year + '-' + month + '-' + day
    #     df1 = df.loc[lambda x: x[pickup_time].str.startswith(date)]
    #     print('number of trips on selected day (%s): %d' % (date, df1.shape[0]))

    # proposed saving file name
    nyc_taxi_file_on_selected_day = 'NYC-taxi-' + year + month + day + '.csv'
    Manhattan_taxi_file_on_selected_day = 'Manhattan-taxi-' + year + month + day + '.csv'

    # # filter out trips in one day
    # df1 = df.loc[lambda x: x[pickup_time].str.startswith(date)]
    # df1[pickup_time] = pd.to_datetime(df1[pickup_time])
    # df1.sort_values(pickup_time, inplace=True)
    # print('number of trips on selected day (%s): %d' % (date, df1.shape[0]))
    # df1.to_csv(nyc_taxi_file_on_selected_day, index=False)
    #
    # # filter out useful parameters: time, lng & lat, passenger number...
    # df1 = pd.read_csv(nyc_taxi_file_on_selected_day)
    # df2 = df1.loc[:, [pickup_time, passenger_count, olng, olat, dlng, dlat, trip_dist, dropoff_time]]
    # print(df2.head(2))  # check the format
    # # roughly filter out the trips in a square area
    # df3 = df2[(df2[olng] > -74.0300) & (df2[olng] < -73.9030)
    #           & (df2[olat] > 40.6950) & (df2[olat] < 40.8825)
    #           & (df2[dlng] > -74.0300) & (df2[dlng] < -73.9030)
    #           & (df2[dlat] > 40.6950) & (df2[dlat] < 40.8825)]
    # print('number of trips after rough filter:', df3.shape[0])
    # # filter out the trips starting within Manhattan
    # df4 = df3[df3.apply(lambda x: IsPtInPoly(x[olng], x[olat]), axis=1)]
    # # filter out the trips ending in Manhattan
    # df5 = df4[df4.apply(lambda x: IsPtInPoly(x[dlng], x[dlat]), axis=1)]
    # print('number of trips in Manhattan:', df5.shape[0])
    # df5.to_csv(Manhattan_taxi_file_on_selected_day, index=False)
    #
    # filter out the trips longer than 2 min
    df6 = pd.read_csv(Manhattan_taxi_file_on_selected_day)
    print('number of trips on selected day (%s): %d' % (date, df6.shape[0]))
    # df6 = df6[df6.apply(lambda x: LongerThan2Min(x[olng], x[olat], x[dlng], x[dlat]), axis=1)]
    df6 = df6[df6.apply(lambda x: LongerThan2Min(x['olng'], x['olat'], x['dlng'], x['dlat']), axis=1)]
    print('number of trips longer than 2 min :', df6.shape[0])
    df6.to_csv('Manhattan-taxi-' + year + month + day + '111.csv', index=False)
    #
    # # rename the column index
    # df7 = pd.read_csv(Manhattan_taxi_file_on_selected_day)
    # df7 = df7.loc[:, [pickup_time, passenger_count, olng, olat, dlng, dlat, trip_dist, dropoff_time]]
    # df7.columns = ['ptime', 'npass', 'olng', 'olat', 'dlng', 'dlat', 'dist', 'dtime']
    # df7.to_csv(Manhattan_taxi_file_on_selected_day, index=False)

    # # merge green taxi and yellow taxi together
    # df8 = pd.read_csv('Manhattan-green-taxi-20150502.csv')
    # df8['taxi'] = 'green'
    # print('number of green taxi trips:', df8.shape[0])
    # df9 = pd.read_csv('Manhattan-yellow-taxi-20150502.csv')
    # df9['taxi'] = 'yellow'
    # print('number of green taxi trips:', df9.shape[0])
    # frames = [df8, df9]
    # df10 = pd.concat(frames, ignore_index=True)
    # df10.sort_values('ptime', inplace=True)
    # print('number of all taxi trips:', df10.shape[0])
    # df10.to_csv('Manhattan-taxi-20150502.csv', index=False)

    # # merge two different days' trip to together
    # df11 = pd.read_csv('Manhattan-taxi-20160501.csv')
    # print('number of all taxi trips in 20160501:', df11.shape[0])
    # df11['ptime'] = df11['ptime'].map(lambda x: str(parse(x) + datetime.timedelta(days=6)))
    # df11['dtime'] = df11['dtime'].map(lambda x: str(parse(x) + datetime.timedelta(days=6)))
    # df11 = df11.iloc[1::5]  # [start：end：step]
    # df12 = pd.read_csv('Manhattan-taxi-20160507.csv')
    # frames = [df11, df12]
    # df13 = pd.concat(frames, ignore_index=True)
    # df13.sort_values('ptime', inplace=True)
    # print('number of all taxi trips:', df13.shape[0])
    # df13.to_csv('Manhattan-taxi-20130507.csv', index=False)

    # df11 = pd.read_csv(Manhattan_taxi_file_on_selected_day)
    # print('number of trips on selected day (%s): %d' % (date, df11.shape[0]))

    for i in range(3, 12):
        if i < 10:
            day = '0' + str(i)
        else:
            day = '' + str(i)
        date = year + '-' + month + '-' + day
        Manhattan_taxi_file_on_selected_day = 'Manhattan-taxi-' + year + month + day + '.csv'

        df11 = pd.read_csv(Manhattan_taxi_file_on_selected_day)
        print('number of trips on selected day (%s): %d' % (date, df11.shape[0]))

    runtime = time.time() - stime
    print('...running time : %.05f seconds' % runtime)

