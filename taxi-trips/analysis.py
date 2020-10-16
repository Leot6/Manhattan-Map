"""

"""

import time
import h3
import pickle
import json
import numpy as np
import scipy.stats as st
import pandas as pd
import branca.colormap as cm
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from tqdm import tqdm
from geojson import Feature, FeatureCollection
from folium import Map, GeoJson, map
from dateutil.parser import parse


# find out the distribution of pick up locations of trips
def plot_trip_pick_up_distribution(pickup_samples):
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(8, 8))
    ax1, ax2 = axes.ravel()
    num_of_samples = pickup_samples.shape[0]
    title1 = f'Taxi Pickup Locations - {num_of_samples}'
    title2 = f'Taxi dropoff Locations - {num_of_samples}'
    pickup_samples.plot(x='olng', y='olat', style='.', alpha=0.2, legend=False, ax=ax1, title=title1)
    pickup_samples.plot(x='dlng', y='dlat', style='.', alpha=0.2, legend=False, ax=ax2, title=title2)
    plt.tight_layout()
    plt.show()


def counts_by_hexagon(df, resolution):
    """
    Use h3.geo_to_h3 to index each data point into the spatial index of the specified resolution.
    Use h3.h3_to_geo_boundary to obtain the geometries of these hexagons
    Ex counts_by_hexagon(data, 9)
    """
    df['hex_id'] = df.apply(lambda row: h3.geo_to_h3(row['olat'], row['olng'], resolution), axis=1)
    df_aggreg = df.groupby(by='hex_id').size().reset_index()
    df_aggreg.columns = ['hex_id', 'value']
    df_aggreg['geometry'] = df_aggreg['hex_id'].apply(lambda x: {'type': 'Polygon', 'coordinates':
        [h3.h3_to_geo_boundary(x, geo_json=True)]})
    return df_aggreg


def hexagons_dataframe_to_geojson(df_hex, file_output = None):
    """
    Produce the GeoJSON for a dataframe that has a geometry column in geojson
    format already, along with the columns hex_id and value
    Ex counts_by_hexagon(data)
    """
    list_features = []
    for i, row in df_hex.iterrows():
        feature = Feature(geometry=row["geometry"], id=row["hex_id"], properties={"value": row["value"]})
        list_features.append(feature)
    feat_collection = FeatureCollection(list_features)
    geojson_result = json.dumps(feat_collection)
    # optionally write to file
    if file_output is not None:
        with open(file_output, "w") as f:
            json.dump(feat_collection, f)
    return geojson_result


def choropleth_map(df_aggreg, border_color='black', fill_opacity=0.7, initial_map=None, with_legend=False,
                   kind="linear"):
    """
    Creates choropleth maps given the aggregated data.
    """
    # colormap
    min_value = df_aggreg["value"].min()
    max_value = df_aggreg["value"].max()
    m = round((min_value + max_value) / 2, 0)

    # take resolution from the first row
    res = h3.h3_get_resolution(df_aggreg.loc[0, 'hex_id'])

    if initial_map is None:
        initial_map = Map(location=[40.718728, -73.943802], zoom_start=12, tiles="cartodbpositron",
                          attr='© <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors © <a href="http://cartodb.com/attributions#basemaps">CartoDB</a>'
                          )

    # the colormap
    # color names accepted https://github.com/python-visualization/branca/blob/master/branca/_cnames.json
    if kind == "linear":
        custom_cm = cm.LinearColormap(['green', 'yellow', 'red'], vmin=min_value, vmax=max_value)
    elif kind == "outlier":
        # for outliers, values would be -11,0,1
        custom_cm = cm.LinearColormap(['blue', 'white', 'red'], vmin=min_value, vmax=max_value)
    elif kind == "filled_nulls":
        custom_cm = cm.LinearColormap(['sienna', 'green', 'yellow', 'red'],
                                      index=[0, min_value, m, max_value], vmin=min_value, vmax=max_value)

    # create geojson data from dataframe
    geojson_data = hexagons_dataframe_to_geojson(df_hex=df_aggreg)

    # plot on map
    name_layer = 'Choropleth ' + str(res)
    if kind != "linear":
        name_layer = name_layer + kind
    GeoJson(
        geojson_data,
        style_function=lambda feature: {
            'fillColor': custom_cm(feature['properties']['value']),
            'color': border_color,
            'weight': 1,
            'fillOpacity': fill_opacity
        },
        name=name_layer
    ).add_to(initial_map)
    # add legend (not recommended if multiple layers)
    if with_legend:
        custom_cm.add_to(initial_map)

    return initial_map


def plot_scatter(df, metric_col, x='lng', y='lat', marker='.', alpha=1, figsize=(16, 12), colormap='viridis'):
    """
    Scatter plot function for h3 indexed objects
    """
    df.plot.scatter(x=x, y=y, c=metric_col, title=metric_col, edgecolors='none', colormap=colormap, marker=marker, alpha=alpha, figsize=figsize)


def run_counts_by_hexagon():
    year = '2015'
    month = '05'
    day = '05'
    # columns = ['ptime', 'npass', 'onid'，'olng', 'olat', 'dnid', 'dlng', 'dlat', 'dist', 'dtime']
    taxi_trips = pd.read_csv(f'manhattan-taxi-{year}{month}{day}.csv').loc[:, ['ptime', 'olat', 'dlng', 'dlat']]
    trip_samples = taxi_trips.sample(frac=0.05, replace=False, random_state=1)
    print('trip_samples')
    print(trip_samples.head(2))

    # # plot the pick up and drop off location distributions
    # plot_trip_pick_up_distribution(trip_samples)

    # # Counts how many points are within the hex
    # df_aggreg = counts_by_hexagon(trip_samples, 9)
    # df_aggreg.sort_values(by='value', ascending=True, inplace=True)
    # print('count_by_hex')
    # print(df_aggreg.head(2))
    # # Creates a map using Folium
    # hexmap = choropleth_map(df_aggreg=df_aggreg, with_legend=True)
    # hexmap.save('choropleth_map.html')

    #  plot multiple aperture sizes with legend allowing to toggle them on/off
    df_aggreg_10 = counts_by_hexagon(df=trip_samples, resolution=10)
    df_aggreg_9 = counts_by_hexagon(df=trip_samples, resolution=9)
    df_aggreg_8 = counts_by_hexagon(df=trip_samples, resolution=8)
    df_aggreg_7 = counts_by_hexagon(df=trip_samples, resolution=7)
    df_aggreg_6 = counts_by_hexagon(df=trip_samples, resolution=6)
    hexmap10 = choropleth_map(df_aggreg=df_aggreg_10, with_legend=False)
    hexmap9 = choropleth_map(df_aggreg=df_aggreg_9, initial_map=hexmap10, with_legend=False)
    hexmap8 = choropleth_map(df_aggreg=df_aggreg_8, initial_map=hexmap9, with_legend=False)
    hexmap7 = choropleth_map(df_aggreg=df_aggreg_7, initial_map=hexmap8, with_legend=False)
    hexmap6 = choropleth_map(df_aggreg=df_aggreg_6, initial_map=hexmap7, with_legend=False)
    map.LayerControl('bottomright', collapsed=False).add_to(hexmap6)
    hexmap6.save('choropleth_multiple_res.html')


def print_num_of_request_on_different_time_of_the_day(year='2016', month='05', day='25'):
    # year = '2015'
    # month = '05'
    # day = '06'
    # # columns = ['ptime', 'npass', 'onid'，'olng', 'olat', 'dnid', 'dlng', 'dlat', 'dist', 'dtime']
    # taxi_trips = pd.read_csv(f'manhattan-taxi-{year}{month}{day}.csv').loc[:, ['ptime']]
    # print('trip_samples')
    # print(taxi_trips.head(2))

    TRIP_NUM = '800k'  # 400k(404310), 500k(504985), 600k(605660), 700k(703260), 800k(800752)
    with open(f'NYC_REQ_DATA_{TRIP_NUM}.pickle', 'rb') as f:
        taxi_trips = pickle.load(f)

    DATE = year + month + day
    start_time_of_day = parse(DATE + ' 00:00:00')
    DMD_STA = (parse(DATE + ' 00:00:00') - start_time_of_day).seconds
    DMD_END = (parse(DATE + ' 23:59:59') - start_time_of_day).seconds
    DMD_BIN = (parse(DATE + ' 00:30:00') - start_time_of_day).seconds
    time_bins = list(range(DMD_STA, DMD_END + DMD_BIN, DMD_BIN))
    print(DMD_STA, DMD_END, DMD_BIN)
    print(time_bins)

    taxi_trips['ptime'] = taxi_trips['ptime'].map(lambda t: (parse(t) - start_time_of_day).seconds)
    taxi_trips['time_bin'] = pd.cut(taxi_trips['ptime'], time_bins)
    agg1_col = f'all trips'
    agg1 = taxi_trips.groupby(by=['time_bin'])['ptime'].agg(['count']).rename(columns={'count': agg1_col})
    print(agg1.head(2))

    ax_num = agg1.plot(kind='bar', figsize=(16, 6))
    ax_num.set_xlabel('time bins (s)')
    ax_num.set_ylabel('number')
    # ax_num.legend(loc=9)
    plt.tight_layout()
    # plt.savefig('./analysis/analysis-for-different-times.png', dpi=300)
    plt.show()


if __name__ == '__main__':
    start_time = time.time()
    # run_counts_by_hexagon()
    # print_num_of_request_on_different_time_of_the_day()

    year = '2016'
    month = '05'
    day = '25'
    # columns = ['ptime', 'npass', 'onid'，'olng', 'olat', 'dnid', 'dlng', 'dlat', 'dist', 'dtime']
    taxi_trips = pd.read_csv(f'manhattan-taxi-{year}{month}{day}.csv').loc[:, ['ptime', 'olat', 'dlng', 'dlat']]
    print('num of reqs', len(taxi_trips))
    print('...running time : %.05f seconds' % (time.time() - start_time))
