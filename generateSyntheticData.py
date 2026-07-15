import os
import matplotlib.pyplot as plt
import pandas as pan
import _sqlite3 as SQ
import numpy
import csv

files = os.listdir("b_input_data")
dataConnect = SQ.connect("b_output_data/brazilian_data_db.sqlite")
curs = dataConnect.cursor()

