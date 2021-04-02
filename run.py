#!/usr/bin/python3


if __name__ == '__main__':
    from network_generator import load_Manhattan_network
    load_Manhattan_network()
    from path_table_generator import compute_tables
    compute_tables()
    from data_serializer import store_network_to_pickle, store_path_table_to_pickle
    store_network_to_pickle()
    store_path_table_to_pickle()
    from trip_filter import filter_out_needed_trips
    filter_out_needed_trips('yellow_tripdata_2016-05.csv', '2016', '05', '05')
