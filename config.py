"""
constants are found here
"""
import os

PICKLE_PATH = './pickle-files-gitignore/'
if not os.path.exists(PICKLE_PATH):
    os.mkdir(PICKLE_PATH)
TABLE_PATH = './precomputed-tables-gitignore/'
if not os.path.exists(TABLE_PATH):
    os.mkdir(TABLE_PATH)
