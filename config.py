"""
constants are found here
"""
import os

PICKLE_PATH = './pickle-files-gitignore'
if not os.path.exists(PICKLE_PATH):
    os.mkdir(PICKLE_PATH)

TABLE_PATH = './precomputed-tables-gitignore'
if not os.path.exists(TABLE_PATH):
    os.mkdir(TABLE_PATH)

MAP_DATA_PATH = './map-data-gitignore'
if not os.path.exists(TABLE_PATH):
    os.mkdir(TABLE_PATH)

TAXI_DATA_PATH = './taxi-data-gitignore'
if not os.path.exists(TABLE_PATH):
    os.mkdir(TABLE_PATH)
