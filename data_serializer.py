"""
serialize data to pickle file to save time on initialization
"""

import pickle
import time
import os
import pandas as pd

path1 = './pickle-files-gitignore/'
if not os.path.exists(path1):
    os.mkdir(path1)
path2 = './precomputed-tables-gitignore/'
if not os.path.exists(path2):
    os.mkdir(path2)


def store_graph_to_pickle():
    # store node locations as pickle file
    print('store node locations')
    NOD_LOC = pd.read_csv('./map-data/nodes.csv').values.tolist()
    with open(path1 + 'NYC_NOD_LOC.pickle', 'wb') as f:
        pickle.dump(NOD_LOC, f)

    # store station locations as pickle file
    print('store station locations')
    STN_LOC = pd.read_csv('./map-data/stations-630.csv').values.tolist()
    with open(path1 + 'NYC_STN_LOC.pickle', 'wb') as f:
        pickle.dump(STN_LOC, f)


def store_path_table_to_pickle():
    # store mean travel time table as pickle file, the table name might be different and needs manual modification
    print('store travel time table')
    NOD_TTT = pd.read_csv(path2 + 'mean_table.csv', index_col=0).values
    with open(path1 + 'NYC_TTT_WEEK.pickle', 'wb') as f:
        pickle.dump(NOD_TTT, f)

    # store travel time variance table as pickle file, the table name might be different and needs manual modification
    print('store travel time table')
    NOD_TTV = pd.read_csv(path2 + 'mean_table.csv', index_col=0).values
    with open(path1 + 'NYC_TTV_WEEK.pickle', 'wb') as f:
        pickle.dump(NOD_TTV, f)

    # store shortest path table as pickle file, the table name might be different and needs manual modification
    print('store shortest path table')
    NOD_SPT = pd.read_csv(path2 + 'path_table.csv', index_col=0).values
    with open(path1 + 'NYC_SPT_WEEK.pickle', 'wb') as f:
        pickle.dump(NOD_SPT, f)


def store_taxi_trips_to_pickle():
    # store taxi trips as pickle file
    print('store taxi trips')
    date = '20160501'
    REQ_DATA = pd.read_csv('./taxi-trips/manhattan-taxi-' + date + '.csv')
    with open(path1 + 'NYC_REQ_DATA_' + date + '.pickle', 'wb') as f:
        pickle.dump(REQ_DATA, f)


if __name__ == '__main__':
    store_graph_to_pickle()
    store_path_table_to_pickle()
