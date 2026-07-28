import _sqlite3 as SQ
import sys
import pandas as pan
import csv
import os
from enum import Enum
import helpfulFunctions as hf


from main import dataConnect
from main import cursor
from main import fileName

def actionChoice(query):
    print(f"\nYou are querying {query.tableName} in {fileName}")
    #Remember that selection handler returns the following in the exact order: [columns selected, limit, original selection]
    hf.whitespace()
    optionList = hf.getColumns(query.tableName)
    action = input(f"What would you like to do with {len(query.columnNames)} column(s)?\n" \
        "(V)view, (C)calculations, (F)filter, (E)edit my selection, (S)save to .CSV, (Q)quit\n")
    while action.upper() != 'Q':
        #colSelection = query.columnNames
        print("\n")
        
        '''if action.upper()[0] == 'A':
            
            cursor.execute(query.stringQuery)
            data = cursor.fetchall()
            for row in data:
                print(row) 
            
            newQuery()
            break'''
            
        if action.upper()[0] == 'V':
            print(query.dataFrame)
            action = input(f"What would you like to do with {len(query.columnNames)} column(s)?\n" \
        "(V)view, (C)calculations, (F)filter, (E)edit my selection, (S)save to .CSV, (Q)quit\n")

        if action.upper().startswith('C'):
            print("\nNote that non-numerical columns cannot have most calculations performed on them.\n")
            myColumns = query.columnNames
            hf.showOptions(myColumns)
            hf.whitespace()
            columnAffected = input ("Which of your column do you want to perform calcs on(enter by number)?")
            while not columnAffected.isdigit() or int(columnAffected) not in range(len(myColumns)):
                print("[!]That number is invalid. Please choose a valid number from the table[!]")
                columnAffected = input ("Which of your column do you want to perform calcs on(enter by number)?")
            chosenColumn = myColumns[int(columnAffected)]
            calculation = input('What would you like to Calculate?:\n'
                                "(T)Total, (H)Highest, (L)Lowest, (A)Average, (M)Median, (B)Back:\n")
            
            if calculation.upper().startswith('T'):
                if(hf.checkDataType(chosenColumn, query.tableName) == hf.dataType.CATEGORICAL):
                    possibleVals = list(set([d[0] for d in cursor.execute(f"SELECT {myColumns[int(columnAffected)]} FROM {query.tableName}")]))
                    possibleVals = list(set(possibleVals))
                    hf.showOptions(possibleVals)
                    hf.whitespace()
                    chosenVal = input("The column you chose does not contain numerical data. Please select a specific value of your column to use for calculations:")
                    print(f"{possibleVals[int(chosenVal)]} total: {query.totalCategorical(chosenColumn, possibleVals[int(chosenVal)])}")
                else:
                    print(f"{myColumns[int(columnAffected)]} total: {query.calculate(chosenColumn,'T')}")
            if calculation.upper().startswith('H'):
                print(f"{myColumns[int(columnAffected)]} highest: {query.calculate(chosenColumn,'H')}\n")
            if calculation.upper().startswith('L'):
                print(f"{myColumns[int(columnAffected)]} lowest: {query.calculate(chosenColumn,'L')}\n")
            if calculation.upper().startswith('A'):
                print(f"{myColumns[int(columnAffected)]} average: {query.calculate(chosenColumn,'A')}\n")
            if calculation.upper().startswith('M'):
                print(f"{myColumns[int(columnAffected)]} median: {query.calculate(chosenColumn,'M')}\n")
            if calculation.upper().startswith('B'):
                action = input(f"What would you like to do with {len(query.columnNames)} column(s)?"
                            "(V)view, (C)calculations, (F)filter, (E)edit my selection, (S)save to .csv, (Q)quit: ")
                
            action =''
                
        if action.upper().startswith('E'):
            while True:
                newOptions = hf.getColumns(query.tableName)
                index_map = {col: idx for idx, col in enumerate(newOptions)}

                hf.showOptions(newOptions)

                columnIndexes = [index_map[col] for col in query.columnNames]
                print(f"Current Selection: {columnIndexes}, ({query.limit})")

                edit = input("(A)Add, (R)Remove, (L)Limit, (N)New Query, (B)Back:\n").upper()

                if edit.startswith('B'):
                    action = input("(V)view, (C)calc, (F)filter, (E)edit, (S)save, (Q)quit")
                    break

                elif edit.startswith('R'):
                    print(query.columnNames)
                    removal = input("Enter column indices to remove:\n")
                    indices = sorted([int(i) for i in removal.split(',') if i.strip().isdigit()], reverse=True)

                    for idx in indices:
                        if 0 <= idx < len(query.columnNames):
                            query.columnNames.pop(idx)

                    # rebuild selection string
                    selection_indexes = sorted([index_map[col] for col in query.columnNames])
                    query.stringSelection = "[" + ",".join(map(str, selection_indexes)) + f"({query.limit})]"

                elif edit.startswith('L'):
                    newLimit = input("Enter new limit:\n")
                    while not newLimit.isdigit():
                        print("Digits only.")
                        newLimit = input("Enter new limit:\n")
                    query.limit = int(newLimit)
                    selection_indexes = sorted([index_map[col] for col in query.columnNames])
                    query.stringSelection = "[" + ",".join(map(str, selection_indexes)) + f"({query.limit})]"

                elif edit.startswith('N'):
                    hf.newQuery()
                    break

                elif edit.startswith('A'):
                    hf.showOptions(newOptions)

                    new_col = input("Enter indexes to add:\n")
                    try:
                        ids = hf.parseTextToList(new_col, newOptions)
                    except:
                        print("[!]Invalid column number.[!]")
                        continue
                    for i in ids:
                        if i in query.columnNames:
                            print(f"[!]You already have {i} in your selection. It will be skipped.[!]")
                            continue
                        # Add column
                        query.columnNames.append(i)

                    selection_indexes = sorted([index_map[col] for col in query.columnNames])
                    query.stringSelection = "[" + ",".join(map(str, selection_indexes)) + "]"
                    print(f"Updated selection: {query.columnNames}")
       
        if action.upper().startswith('S'):

                csvName = input('Please name your .CSV file:\n')
                print("Saving...")
                hf.csvMaker(csvName,query.columnNames, query.tableName)
                print(f"{csvName}.csv has been saved at {os.path.dirname('queryfolder/'+csvName+'.csv')}\n")
                break
        
        if action.upper().startswith('F'):
            filterBy = input('What would you like to filter by?\n' \
            '(C)category, (R)range, (B)back\n').upper()
            while filterBy[0] != 'B':
                if filterBy.startswith('C'):
                    print(f"Here are the categories you can sort by (based on your selected columns):\n")
                    possibleCategories = []
                    for i in query.columnNames:
                        if(hf.checkDataType(i, query.tableName) == hf.dataType.CATEGORICAL):
                            possibleCategories.append(i)
                    hf.showOptions(possibleCategories)
                    category = input('Select your category by number:\n')
                    possibleFilters = list(set([d[0] for d in cursor.execute(f"SELECT {possibleCategories[int(category)]} FROM {query.tableName}")]))
                    hf.showOptions(possibleFilters)
                    chosenFilter = input('Choose what to filter by with number:\n')
                    query.filterCategorical(possibleCategories[int(category)], possibleFilters[int(chosenFilter)])
                    query.stringQuery = f'SELECT * FROM {query.tableName} WHERE {possibleCategories[int(category)]}= "{possibleFilters[int(chosenFilter)]}"'
                    print(query.dataFrame)
                    
                    choi = input('Continue filtering?(Y/N):\n').upper()
                    if choi.startswith('Y'):
                        filterBy = 'C'
                        continue
                    else:
                        actionChoice(query)


                elif filterBy.startswith('R'):
                    validColumns = []
                    print("\n**The following columns cannot be calculated and will be skipped:**\n")
                    for col in query.columnNames:
                        if hf.checkDataType(col, query.tableName) == hf.dataType.CATEGORICAL:
                            print(f" - {col}")
                        else:
                            validColumns.append(col)
                           
                    print()
                    print('Choose from the following columns:')
                    hf.showOptions(validColumns)
                    hf.whitespace()
                    
                    try:
                        affectedColIdx = input("What column do you want the range to affect?: \n").strip()
                        if affectedColIdx.isdigit() and 0 <= int(affectedColIdx) < len(validColumns):
                            affectedCol = validColumns[int(affectedColIdx)]
                        else:
                            print(f"\nError: Invalid column selection index.\n")
                            choi = input('Continue filtering?(Y/N):\n').upper()
                            if choi.startswith('Y'):
                                continue
                            else:
                                actionChoice(query)
                                break
                    except ValueError:
                        print("\nError: Please enter a valid column index number.\n")
                        continue

                    cursor.execute(f'SELECT MIN("{affectedCol}"), MAX("{affectedCol}") FROM "{query.tableName}"')
                    db_min, db_max = cursor.fetchone()
                    print(f"\nCurrent bounds for '{affectedCol}': Min is {db_min}, Max is {db_max}")

                    try:
                        Startr = float(input('What range do you want to filter by?(For a specific number make the start and end the same)\nStart: '))
                        endr = float(input('End: '))
                        
                        query.getRange(affectedCol, Startr, endr)
                        print(query.dataFrame)
  
                        if query.dataFrame.empty:
                            print("[!]No rows left after filtering. Resetting data to original table layout.[!]")
                            cols_str = ", ".join([f'"{c}"' for c in query.columnNames]) if query.columnNames else "*"
                            if query.limit != 0:
                                query.stringQuery = f'SELECT {cols_str} FROM "{query.tableName}" LIMIT {query.limit}'
                            else:
                                query.stringQuery = f'SELECT {cols_str} FROM "{query.tableName}"'
                            query.dataFrame = pan.read_sql_query(query.stringQuery, query.SQLconnection)
                            
                            choi = input('Retry filtering? (Y/N):\n').upper()
                            if choi.startswith('Y'):
                                continue
                            else:
                                actionChoice(query)


                        choi = input('Continue filtering?(Y/N):\n').upper()
                        if choi.startswith('Y'):
                            continue
                        else:
                            actionChoice(query)

                    except ValueError:
                        print("\nError: Please enter numbers only for the range bounds.\n")
                        choi = input('Continue filtering?(Y/N):\n').upper()
                        if choi.startswith('Y'):
                            continue
                        else:
                            actionChoice(query)

                            break

                        
   
    #newQuery()
    print("You have quit.")
    sys.exit()