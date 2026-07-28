import _sqlite3 as SQ
import sys
import pandas as pan
import csv
import os
from enum import Enum

from main import dataConnect
from main import cursor
from main import fileName

import helpfulFunctions as hf

class userQuery():
    def __init__(self, tableName, columnNames, limit, stringSelection, SQLconnection):
        self.tableName = tableName
        self.columnNames = columnNames
        self.limit = limit
        self.SQLconnection = SQLconnection
        self.stringSelection = stringSelection #the format in which the user enters the initial query (0,2,4(90))
        
        if(self.limit != 0):
            self.stringQuery = f"SELECT * FROM {self.tableName} LIMIT {limit}"
        else:
            self.stringQuery = f"SELECT * FROM {self.tableName}"
        self.dataFrame = pan.read_sql_query(self.stringQuery, self.SQLconnection)
    def runQuery(self, cursor):
        result = cursor.execute(self.stringQuery, self.SQLconnection).fetchall()

    def calculate(self, column, calc):
        df = self.dataFrame
        if(calc == 'A'): #Average
            return df[column].mean()
        if(calc == 'M'): #Median
            return df[column].median()
        if(calc == 'T'): #Total
            return df[column].sum()
        if(calc == 'H'): #Highest(max)
            return df[column].max()
        if(calc == 'L'): #Lowest(min)
            return df[column].min()

    def totalCategorical(self, column, targetVal):
        df = self.dataFrame
        return (df[column] == targetVal).sum()

    def filterCategorical(self, column, targetValue):
        df = self.dataFrame
        #change the actual dataframe itself
        self.dataFrame = df[df[column] == targetValue]
    
    def getRange(self, column, start, end):
        df = self.dataFrame
        self.dataFrame = df[(df[column] < end) & (df[column] > start)]

        
def parseTextToList(selection_list, options):
    cleaned = "".join(selection_list).replace('[', '').replace(']', '').strip()
    if not cleaned:
        return []
    parts = cleaned.split(',')
    selected = []
    for part in parts:
        part = part.strip()
        if part.isdigit():
            idx = int(part)
            if 0 <= idx < len(options):
                selected.append(options[idx])
        elif part in options:
            selected.append(part)
    return selected

def contains(container, targetElement):
    return targetElement in container

def begin():
    optionList = hf.getTables()
    hf.showOptions(optionList)
    hf.whitespace()
    queryTable = input("What table would you like to query? (type 'exit' to exit)\n")
    hf.whitespace()
    while queryTable != "exit" and (not queryTable.isdigit() or int(queryTable) not in range(len(optionList))):
        print("[!]That table doesn't exist! Try again, available numbers only please[!]\n")
        queryTable = input("What table would you like to query? (type 'exit' to exit)\n")
    if queryTable == "exit":
        sys.exit()
    queryTable = optionList[int(queryTable)]

    hf.checkActive(queryTable)
    infos = selectionHandler(queryTable)
    query = userQuery(queryTable, infos[0], int(infos[1]), infos[2], dataConnect)

    import pipeline.queryActions as actions
    actions.actionChoice(query)

def selectionHandler(queryTable):
    restultingInfo = []
    optionList = hf.getColumns(queryTable)
    colSelection = []
    hf.showOptions(optionList)
    
    prompt = ("\nSelect the column(s) and limit you want to work with (using the # on the left side) in the following format:\n"
              "[column_number,column_number,...,(limit)]\n"
              "Input column number as 'A' to view all columns and () as 0 for no limit\n")
    
    selection = input(prompt)
    while not (contains(selection, '(') and contains(selection, ')')):
        print("You didn't specify a limit! Please specify a limit by enclosing it in commas.\n")
        selection = input(prompt)
        
    originalSelection = selection
    
    start = selection.index('(')
    end = selection.index(')')
    limit_str = selection[start+1:end].strip()
    limit = int(limit_str) if limit_str.isdigit() else 0
    
    clean_selection = selection[:start] + selection[end+1:]
    clean_selection = clean_selection.replace('[', '').replace(']', '').strip()
    
    is_all = False
    for part in clean_selection.split(','):
        if part.strip().upper() == 'A':
            is_all = True
            break
            
    if is_all:
        colSelection = optionList   
    else:
        colSelection = parseTextToList(list(clean_selection), optionList)
    restultingInfo.append(colSelection)
    restultingInfo.append(limit)
    restultingInfo.append(originalSelection)
    return restultingInfo 

#-----PROCESS-----
begin()
