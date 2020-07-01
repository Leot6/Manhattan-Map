"""
serialize data to pickle file to save time on initialization
"""

import pickle
import pandas as pd
from config import *


def store_graph_to_pickle():
    # store node locations as pickle file
    print('store node locations')
    NOD_LOC = pd.read_csv('./map-data/nodes.csv').values.tolist()
    with open(f'{PICKLE_PATH}NYC_NOD_LOC.pickle', 'wb') as f:
        pickle.dump(NOD_LOC, f)

    # store station locations as pickle file
    print('store station locations')
    STN_LOC = pd.read_csv('./map-data/stations-630.csv').values.tolist()
    with open(f'{PICKLE_PATH}NYC_STN_LOC.pickle', 'wb') as f:
        pickle.dump(STN_LOC, f)


def store_path_table_to_pickle():
    # store mean travel time table as pickle file, the table name might be different and needs manual modification
    print('store mean travel time table')
    NOD_TTT = pd.read_csv(f'{TABLE_PATH}mean-table.csv', index_col=0).values
    with open(f'{PICKLE_PATH}NYC_TTT_WEEK.pickle', 'wb') as f:
        pickle.dump(NOD_TTT, f)

    # store travel time variance table as pickle file, the table name might be different and needs manual modification
    print('store travel time variance table')
    NOD_TTV = pd.read_csv(f'{TABLE_PATH}var-table.csv', index_col=0).values
    with open(f'{PICKLE_PATH}NYC_TTV_WEEK.pickle', 'wb') as f:
        pickle.dump(NOD_TTV, f)

    # store shortest path table as pickle file, the table name might be different and needs manual modification
    print('store shortest path table')
    NOD_SPT = pd.read_csv(f'{TABLE_PATH}path-table.csv', index_col=0).values
    with open(f'{PICKLE_PATH}NYC_SPT_WEEK.pickle', 'wb') as f:
        pickle.dump(NOD_SPT, f)
    print('table store done!')


def store_taxi_trips_to_pickle():
    # store taxi trips as pickle file
    print('store taxi trips')
    date = '20160501'
    REQ_DATA = pd.read_csv(f'./taxi-trips/manhattan-taxi-{date}.csv')
    with open(f'{PICKLE_PATH}NYC_REQ_DATA_{date}.pickle', 'wb') as f:
        pickle.dump(REQ_DATA, f)


if __name__ == '__main__':
    store_graph_to_pickle()
    store_path_table_to_pickle()
