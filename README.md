# `Manhattan Map`
<img src="https://github.com/Leot6/Manhattan-Map/blob/master/data/nodes.png" width="300">

Built on [this repository](https://github.com/wallarelvo/nyc-taxi-analysis). This network of Manhattan consists of 4,092 nodes and 9,453 edges. The travel times on each edge (road segment) during each hour of the day are provided. Taxi trip data on several days is also provided. 

The function in `generate_graph.py` will load data, build the Manhattan network using [networkx](https://networkx.github.io/) and save it as a pickle file. 

More taxi trip data can be download from [TLC Trip Record Data](https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page). Travel speed (consisting of mean and std speed values on each road segment) can be download form [Uber Movement](https://movement.uber.com/explore/new_york/speeds/query?dt[tpb]=ALL_DAY&dt[wd;]=1,2,3,4,5,6,7&dt[dr][sd]=2019-11-30&dt[dr][ed]=2019-12-30&ff=&lat.=40.7264408&lng.=-73.9924725&z.=13.17&lang=en-US)
