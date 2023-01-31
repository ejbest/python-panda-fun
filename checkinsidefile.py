import os
import pandas as pd
import sys

def main():
    if len(sys.argv) < 4:
        print("Please provide valid arguments: path col value")
        print("python3 checkinside.py file column value")
        sys.exit(0)
    if not os.path.isfile(sys.argv[1]):
        print("Please provide existing file")
        sys.exit(0)
    col = sys.argv[2]
    searchValue = sys.argv[3]
    filename = sys.argv[1]
    if filename.endswith(".xlsx"):
        column = ""
        counter = 0
        print(filename)
        df = pd.read_excel(filename)
        for i in range(df.columns.size):
            c = df.columns[i]
            if str(c.replace(" ", "")).lower() == str(col.replace(" ", "")).lower():
                column = i
                break

        if column != "":
            for j in range(0, len(df)):
                column_from_expanded_excel = str(df.iloc[j][df.columns[column]]).lower()
                if searchValue in column_from_expanded_excel:
                    counter += 1
            print("File: " + filename + " has " + str(counter) + " records of " + searchValue)
        else:
            print("No column named: " + col)
    else:
        print("The provided file is not an regular excel")
if __name__ == '__main__':
    main()