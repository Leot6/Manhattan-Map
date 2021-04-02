# `Manhattan Map`
<img src="https://github.com/Leot6/Manhattan-Map/blob/master/node_distribution.jpg" width="1000">

Built on [this repository](https://github.com/wallarelvo/nyc-taxi-analysis). This network of Manhattan consists of 4,091 nodes and 9,452 edges. The travel times on each edge (road segment) during each hour of the day are provided. Taxi trip data on several days is also provided. 

To run the code, download data files from [this onedrive link](https://1drv.ms/f/s!AsqflzzqZj9qg-8nGeUMw8BgM6O-4w) or [this google drive link](https://drive.google.com/drive/folders/1p9QZACjjBDog3KzvoAtkNgcrvjHMj6TG?usp=sharing), and put the downloaded folders in the root directory.

```
|-- Manhattan-Map
   |-- map-data-gitignore
   |-- pickle-files-gitignore
   |-- precomputed-tables-gitignore
   |-- taxi-data-gitignore
```


Put the taxi trip data file (e.g. yellow_tripdata_2015-05.csv) in the root folder, and run `run.py`, which will do the following things.
1. Run `network_generator.py` to load map data, build the Manhattan network using [networkx](https://networkx.github.io/) and save it as a pickle file. 
2. Use `path_table_generator.py` to precompute the shortest paths among all node pairs, store the paths and the means (and variances) of the paths in tables. 
3. Use the function `store_network_to_pickle()` and `store_path_table_to_pickle()` in `data_serializer.py` to save these files to picklefiles, so that we can save time on loading them. 
4. Run `trip_filter` to filter out the trip data on selected day.

More taxi trip data can be download from [TLC Trip Record Data](https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page). Travel speed (consisting of mean and std speed values on each road segment) can be download form [Uber Movement](https://movement.uber.com/explore/new_york/speeds/query?dt[tpb]=ALL_DAY&dt[wd;]=1,2,3,4,5,6,7&dt[dr][sd]=2019-11-30&dt[dr][ed]=2019-12-30&ff=&lat.=40.7264408&lng.=-73.9924725&z.=13.17&lang=en-US)
