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
            while int(columnAffected) not in range(len(myColumns) - 1):
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
                print(f"{myColumns[int(columnAffected)]} average: {query.calculate(chosenColumn,'H')}\n")
            if calculation.upper().startswith('M'):
                print(f"{myColumns[int(columnAffected)]} median: {query.calculate(chosenColumn,'M')}\n")
            if calculation.upper().startswith('B'):
                action = input(f"What would you like to do with {len(query.columnNames)} column(s)?"
                            "(V)view, (C)calculations, (F)filter, (E)edit my selection, (S)save to .csv, (Q)quit: ")
                
            action =''
                
        if action.upper().startswith('E'):       
                while True:
                    newOptions = hf.getColumns(query.tableName)
                    hf.showOptions(newOptions)
                    print(f'Current Selection: {query.columnNames}, limit: {query.limit}')
                    edit = input("What edit would you like to perform?\n(A)Add, (R)Remove, (L)Change limit, (N)New Query or (B)Back:\n").upper()
                    
                    if edit.startswith('B'):
                        action = input(f"What would you like to do with {len(query.columnNames)} column(s)?\n" \
                        "(V)view, (C)calculations, (F)filter, (E)edit my selection, (S)save to .csv, (Q)quit")
                        break
                        
                    elif edit.startswith('R'):
                        print(query.columnNames)
                        removal = input("Enter column indices to remove (separated by commas):\n")
                        indices = sorted([int(i) for i in removal.split(',') if i.strip().isdigit()], reverse=True)
                        for idx in indices:
                            if 0 <= idx < len(query.columnNames):
                                query.columnNames.pop(idx)
                        newSelecton = ''
                        for i in query.columnNames:
                            newSelecton = newSelecton + str(newOptions.index(i))
                            if(query.columnNames.index(i) != len(query.columnNames) - 1):
                                newSelecton = newSelecton + ','
                        newSelecton = newSelecton + f'({query.columnNames})'
                        query.stringSelection = newSelecton

                    elif edit.startswith('L'):
                        newLimit = input('Enter your new limit (no formatting, just digits)\n:')
                        while newLimit.isalpha():
                            print("[!]Only enter valid digits and try again.[!]")
                            newLimit = input('Enter your new limit (no formatting, just digits)\n:')
                        query.limit = newLimit
                        edit =''
                    elif edit.startswith('N'):
                        edit =''
                        hf.newQuery()
                    elif edit.startswith('A'):
                        # Remove already-selected columns from the available list
                        available = [col for col in newOptions if col not in query.columnNames]

                        hf.showOptions(available)
                        print(f'Current Selection: {query.columnNames}, limit: {query.limit}')

                        new_col = input(
                            "Enter the indexes of the columns to add in the following format:\n"
                            "[column_id,column_id,column_id,...]\n"
                        )

                        ids = hf.parseTextToList(new_col, available)

                        for i in ids:
                            # Validate number
                            if i not in range(len(available)):
                                print("[!] Invalid column number. Try again. [!]")
                                continue

                            colName = available[i]

                            # Check for duplicates (shouldn't happen now)
                            if colName in query.columnNames:
                                print("[!] Column already selected. Choose another. [!]")
                                continue

                            # Add column
                            query.columnNames.append(colName)

                        # Rebuild selection string
                        '''selectionString = ",".join(str(newOptions.index(col)) for col in query.columnNames)
                        selectionString += f"({query.limit})"
                        query.stringSelection = selectionString'''

       
        if action.upper().startswith('S'):

                csvName = input('Please name your .CSV file:\n')
                print("Saving...")
                hf.csvMaker(csvName,query.columnNames, query.tableName)
                print(f"{csvName}.csv has been saved at {os.path.dirname("queryfolder/"+csvName+".csv")}\n")
                break
        
        if action.upper().startswith('F'):
            filterBy = input('What would you like to filter by?\n' \
            '(C)category, (R)range, (B)back')
            while filterBy.upper()[0] != 'B':
                if(filterBy.upper().startswith('C')):
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
                    print(f'Filtered your selection by {possibleFilters[int(chosenFilter)]}.\n')
                    filtered = pan.read_sql(query.stringQuery, dataConnect)
                    print(query.dataFrame)
                    break 
                
                while filterBy.upper().startswith('R'):
                    #dataSep()
                    validColumns = []
                    print("\n**The following columns cannot be calculated and will be skipped:**\n")
                    for col in query.columnNames:
                        if(hf.checkDataType(col, query.tableName) == hf.dataType.CATEGORICAL):
                            print(f" - {col}")
                        else:
                            validColumns.append(col)
                           
                    print()
                    print('Choose from the following columns:')
                    hf.showOptions(validColumns)
                    hf.whitespace()
                    affectedCol = int(input("What column do you want the range to affect?: \n"))
                    affectedCol = validColumns[affectedCol]
                    if affectedCol in validColumns:
                        cursor.execute(f'SELECT MIN("{affectedCol}"), MAX("{affectedCol}") FROM "{query.tableName}"')
                        db_min, db_max = cursor.fetchone()
                        print(f"\nCurrent bounds for '{affectedCol}': Min is {db_min}, Max is {db_max}")

                        try:
                            Startr = float(input('What range do you want to filter by?(For a specific number make the start and end the same)\nStart: '))
                            endr = float(input('End: '))
                            
                            
                            query.getRange(affectedCol, Startr, endr)
      
                            choi = input('Continue filtering?(Y/N):\n')
                            if choi.upper().startswith('Y'):
                             filterBy == 'R'
                            elif choi.upper().startswith('N'):
                                filterBy == ''

                                actionChoice(query)
                        except ValueError:
                            print("\nError: Please enter numbers only for the range bounds.\n")
                    else:
                        print(f"\nError: '{affectedCol}' is not a valid numeric column.\n")
                        filterBy = input('Continue filtering?(Y/N):\n')
                    
                        if filterBy.upper().startswith('Y'):
                            filterBy == 'R'
                        elif filterBy.upper().startswith('N'):
                            actionChoice(query)
        action = input(f"What would you like to do with {len(query.columnNames)} column(s)?\n" \
                                "(V)view, (C)calculations, (F)find range, (E)edit my selection, (Q)quit")

    #newQuery()
    print("You have quit.")
    sys.exit()