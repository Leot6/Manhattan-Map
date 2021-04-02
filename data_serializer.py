"""
serialize data to pickle file to save time on initialization
"""

import pickle
import time
import pandas as pd
from config import *


def store_network_to_pickle():
    # store station locations as pickle file
    print('store station locations')
    STN_LOC_1 = pd.read_csv('./map-data/stations-101.csv')
    with open(f'{PICKLE_PATH}NYC_STN_LOC_101.pickle', 'wb') as f:
        pickle.dump(STN_LOC_1, f)

    # store station locations as pickle file
    print('store station locations')
    STN_LOC_2 = pd.read_csv('./map-data/stations-630.csv')
    with open(f'{PICKLE_PATH}NYC_STN_LOC_630.pickle', 'wb') as f:
        pickle.dump(STN_LOC_2, f)


def store_path_table_to_pickle(label='mit'):
    # store mean travel time table as pickle file, the table name might be different and needs manual modification
    print('store mean travel time table', label)
    NOD_TTT = pd.read_csv(f'{TABLE_PATH}/{label}/mean-table.csv', index_col=0).values
    with open(f'{PICKLE_PATH}/{label}/NYC_TTT.pickle', 'wb') as f:
        pickle.dump(NOD_TTT, f)

    # store travel time variance table as pickle file, the table name might be different and needs manual modification
    print('store travel time variance table', label)
    NOD_TTV = pd.read_csv(f'{TABLE_PATH}/{label}/var-table.csv', index_col=0).values
    with open(f'{PICKLE_PATH}/{label}/NYC_TVT.pickle', 'wb') as f:
        pickle.dump(NOD_TTV, f)

    # store travel distance table as pickle file, the table name might be different and needs manual modification
    print('store travel distance table', label)
    NOD_TDT = pd.read_csv(f'{TABLE_PATH}/{label}/dist-table.csv', index_col=0).values
    with open(f'{PICKLE_PATH}/{label}/NYC_TDT.pickle', 'wb') as f:
        pickle.dump(NOD_TDT, f)

    # store shortest path table as pickle file, the table name might be different and needs manual modification
    print('store shortest path table', label)
    NOD_SPT = pd.read_csv(f'{TABLE_PATH}/{label}/path-table.csv', index_col=0).values
    with open(f'{PICKLE_PATH}/{label}/NYC_SPT.pickle', 'wb') as f:
        pickle.dump(NOD_SPT, f)
    print('table store done!')


def store_taxi_trips_to_pickle(date='20150505'):
    # store taxi trips as pickle file
    print('store taxi trips', date)
    REQ_DATA = pd.read_csv(f'./taxi-trips/manhattan-taxi-{date}.csv')
    with open(f'{PICKLE_PATH}NYC_REQ_DATA_{date}.pickle', 'wb') as f:
        pickle.dump(REQ_DATA, f)


if __name__ == '__main__':
    # store_network_to_pickle()
    # store_path_table_to_pickle('mit')

    # for i in range(21):
    #     store_path_table_to_pickle(str(i))

    # store_taxi_trips_to_pickle('20160525-1005517')
    start_time = time.time()
    date = '20150505'
    label = 'mit'
    print('store taxi trips', date)
    REQ_DATA = pd.read_csv(f'./taxi-trips/manhattan-taxi-{date}.csv')
    NOD_TTT = pd.read_csv(f'{TABLE_PATH}/{label}/mean-table.csv', index_col=0).values
    print('...running time : %.05f seconds' % (time.time() - start_time))
