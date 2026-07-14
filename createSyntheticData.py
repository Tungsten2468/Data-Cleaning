import pandas as pd
import matplotlib.pyplot as plt
import numpy as nmp
import _sqlite3 as sql;
import os

tables = []
files = os.listdir("syn_input_data")
dataConnect = sql.connect("syn_output_data/syn_brazilian_data_db.sqlite")
curs = dataConnect.cursor()

#------------------PREP-------------------
for file in files:
    fileRead = pd.read_csv("syn_input_data/"+file)
    cols = ""
    for header in fileRead.columns: #only add commas if the header is not the last one
        if(fileRead.columns.get_loc(header) != len(fileRead.columns)-1):
            cols = cols+header+", "
        else:
            cols = cols+header
    tableName = file[:-4]
    tables.append(tableName)
        
    curs.execute(f" DROP TABLE IF EXISTS {tableName}")
    curs.execute(f"CREATE TABLE {tableName} ({cols})")
    fileRead.to_sql(tableName, dataConnect, if_exists="append", index=False)
