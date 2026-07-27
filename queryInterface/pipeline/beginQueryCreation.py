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
    selection = input("\nSelect the column(s) and limit you want to work with (using the # on the left side) in the following format:\n"
    "[column_number,column_number,...,(limit)]\n"
    "Input column number as 'A' to view all columns and () as 0 for no limit\n")
    while not hf.contains(selection, '(') or not hf.contains(selection, ')'):
        print("[!]You didn't specify a limit! Please specify a limit by enclosing it in parenthesis()[!].\n")
        selection = input("\nSelect the column(s) and limit you want to work with (using the # on the left side) in the following format:\n"
            "[column_number,column_number,...,(limit)]\n"
            "Input column number as 'A' to view all columns and () as 0 for no limit\n")
    charIndex = 0
    originalSelection = selection #Keep record of the selection made for later editing purposes
    selection = list(selection)
    limit = '' #keep as string initially so numbers can be concactenated
    for char in selection: #first loop extracts the limit, wherever it was specified in the string
        if(char == '('):
            start = selection.index('(') + 1
            end = selection.index(')', start)
            limit = ''.join(selection[start:end])
            selection = selection[:start-1] + selection[end+1:]
            break 
    if 'A' in originalSelection.upper():
        colSelection = optionList
    else:
        try:
            colSelection = hf.parseTextToList(selection, optionList)
        except:
            print("\n[!]Your selection was structured incorrectly. Try again.[!]\n")
            return selectionHandler(queryTable)
    for char in selection:
        if char.isdigit():
            idx = int(char)
            if idx < 0 or idx >= len(optionList):
                print("\n[!]Your selection does not exist. Please enter only available numbers.[!]")
                return selectionHandler(queryTable)
    restultingInfo.append(colSelection)
    restultingInfo.append(limit)
    restultingInfo.append(originalSelection)
    return restultingInfo 

#-----PROCESS-----
begin()
