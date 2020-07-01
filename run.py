#!/usr/bin/python3


if __name__ == '__main__':
    from graph_generator import load_Manhattan_graph
    load_Manhattan_graph()
    from time_table_generator import compute_tables
    compute_tables()
    from data_serializer import store_graph_to_pickle, store_path_table_to_pickle
    store_graph_to_pickle()
    store_path_table_to_pickle()
    from trip_filter import filter_out_needed_trips
    filter_out_needed_trips('yellow_tripdata_2015-05.csv', '2016', '05', '05')
