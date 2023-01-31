from itertools import count
import pandas as pd
import sys
import os
import expanded_delete
from os.path import exists
from time import sleep
count = 0

rows_to_delete = []

def find_match_in_list(string_to_search, string_list):
    found = False
    for sub_string in string_list:
        if sub_string in string_to_search:
            found = True
            break
    return found

def append_records(read_df, header, output_file, col, arg_list, rows_to_delete, old_df,x_df,treatment):
    print("----------------------------------------------------------------------------------")
    args_search = list()
    args_avoid = list()
    # print(old_df)
    #Separate args_list into args_search & args_avoid
    for arg in arg_list:
        if arg != "NULL":
            if arg.startswith("!"):
                args_avoid.append(arg[1:].lower())
            else:
                args_search.append(arg.lower())
    if DEBUG_MODE:
        print("arg list", args_search)
    # in this block of code I check if there is a column with the name specified in the data_config_file.txt
    column = 0
    if DEBUG_DEEP:
        print(read_df.columns)
    
    for i in range(read_df.columns.size):
        c = read_df.columns[i]
        if str(c.replace(" ", "")).lower() == str(col.replace(" ", "")).lower():
            column = i
            break
    if column == 0:
        print("No column named " + col)
        return []
    out_df = pd.DataFrame(columns=header)
    writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
    

    # here starts the iteration through every row of example_expanded.xlsx - same procedure for the other two
    for j in range(0, len(read_df)):
        column_from_expanded_excel = str(read_df.iloc[j][read_df.columns[column]]).lower()
        if len(args_search) > 0:

            flag = find_match_in_list(column_from_expanded_excel, args_search)
            if flag and not find_match_in_list(column_from_expanded_excel, args_avoid):
                # if arg1 is in row j and selected column, I store every value from this row in a list
                row = {}
                if treatment == "or":
                    if j in rows_to_delete:
                        continue
                for k in range(len(read_df.columns)):
                    row.update({f"{read_df.columns[k]}":read_df.iloc[j][read_df.columns[k]]})
                update_df = pd.DataFrame(row, index=[0])
                out_df = pd.concat([out_df, update_df], ignore_index=True)

                if j not in rows_to_delete and isinstance(x_df,str):
                    rows_to_delete.append(j)
        else:
            
            if not find_match_in_list(column_from_expanded_excel, args_avoid):
                # if arg1 is in row j and selected column, I store every value from this row in a list
                row = {}
                for k in range(len(read_df.columns)):
                    row.update({f"{read_df.columns[k]}":read_df.iloc[j][read_df.columns[k]]})
                update_df = pd.DataFrame(row, index=[0])    
                out_df = pd.concat([out_df, update_df], ignore_index=True)

                if j not in rows_to_delete and isinstance(x_df,str):
                    rows_to_delete.append(j)
    if not isinstance(old_df,str):
        out_df = pd.concat([out_df, old_df], ignore_index=True)
    if not isinstance(x_df,str):
        for j in range(0, len(x_df)):
            column_from_expanded_excel = str(x_df.iloc[j][x_df.columns[column]]).lower()
            if treatment == "not":
                if find_match_in_list(column_from_expanded_excel, args_avoid):
                    if j in rows_to_delete:
                        rows_to_delete.remove(j)
            if treatment == "and":
                if not find_match_in_list(column_from_expanded_excel, args_search):
                    if j in rows_to_delete:
                        rows_to_delete.remove(j)



    # when the output dataframe is complete, I save it using the writer I created before
    out_df.to_excel(writer, index=False, header=True, engine='xlsxwriter')
    writer.close()
    #print(len(rows_to_delete))
    return rows_to_delete

def main():
    # reading excel name from command line arguments
    print("----------------------------------------------------------------------------------")
    
    # excel_name    = /Users/ej/pandas-output/example.xlsx 
    # config_file   = data-config.txt
    # file_location =  /Users/ej/pandas-output/
    # expanded_df   = pd.read_excel(excel_name, engine='openpyxl')
      
    if len(sys.argv) < 4:
        print("Please provide correct arguments")
        print("usage python process.py <input file absolute path> <config file absolute path> <output directory absolute path>")
        sys.exit(0)
    excel_name = sys.argv[1]
    if not exists(excel_name):
        print("Missing input file")
        sys.exit(0)
    config_file = sys.argv[2]
    if not exists(config_file):
        print("Missing config file")
        sys.exit(0)
    if not os.path.isdir(sys.argv[3]):
        print("Please provide existing directory")
        sys.exit(0)

    # reading the excel
    expanded_df = pd.read_excel(excel_name, engine='openpyxl')
    file_location = sys.argv[3]

    # getting column names to add to the new files that will be created
    header = expanded_df.columns.values.tolist()

    # creating an array to store all the row indexes I will be deleting from example_expanded.xlsx
    rows_to_delete = [-1]

    filenames = list()

    # reading data_config_file.txt:
    with open(config_file, 'r') as f:
        # Set debug mode
        global DEBUG_MODE
        DEBUG_MODE = "DEBUG_MODE ON" in f.read()
        global DEBUG_DEEP
        DEBUG_DEEP = "DEBUG_DEEP ON" in f.read()

        # Reset file pointer to initial position
        f.seek(0)

        # iterating through all the lines in data_config_file.txt
        for line in f:
            if not line.startswith("#") and line.strip():
                special_treatment = False
                and_treament = False
                print(line.replace("\n",""))
                # separating each argument of the line in different variables
                arg_list = line.split("|")

                # get output file & column_to_search from args list and remove spaces from the end and the start of the strings
                output_file = arg_list.pop(0).strip()
                column_to_search = arg_list.pop(0).strip()
                if column_to_search.startswith("&"):
                    and_treament = True
                    column_to_search = column_to_search[1:]
                #remove spaces from the end and the start of the keys to search strings
                arg_list = [arg.strip() for arg in arg_list]
                arg_list[-1] = arg_list[-1].replace("\n","") 
                for entry in arg_list:
                    if entry.startswith("!"):
                        special_treatment = True
                
                output_file_path = os.path.join(file_location, output_file)

                print("Saving on file |" + output_file_path + "|")
                if DEBUG_MODE:
                    print("Searching on column |" + column_to_search + "| for |" + "|".join(arg_list) + "|")

                # checking if file already exists, if it does, the dataframe I will use will be from the already existing xlsx file
                # if not, create a new dataframe
                if output_file_path in filenames:
                    if special_treatment == True:
                        read_df = pd.read_excel(output_file_path, engine='openpyxl')
                        rows_to_delete = append_records(read_df, header, output_file_path, column_to_search, arg_list, rows_to_delete,"",expanded_df,"not")
                        print(rows_to_delete)
                    elif and_treament == True:
                        read_df = pd.read_excel(output_file_path, engine='openpyxl')
                        rows_to_delete = append_records(read_df, header, output_file_path, column_to_search, arg_list, rows_to_delete,"",expanded_df,"and")
                        print(rows_to_delete)
                    else:
                        read_df = pd.read_excel(output_file_path, engine='openpyxl')
                        rows_to_delete = append_records(expanded_df, header, output_file_path, column_to_search, arg_list, rows_to_delete, read_df,"","or")
                        print(rows_to_delete)

                        
                            # filenames_column.append(output_file_path + column_to_search)
                else:
                    expanded_delete.delete_rows(excel_name, rows_to_delete)
                    expanded_df = pd.read_excel(excel_name, engine='openpyxl')
                    rows_to_delete = [-1]
                    rows_to_delete = append_records(expanded_df, header, output_file_path, column_to_search, arg_list, rows_to_delete,"","","")
                    if rows_to_delete != []:
                        filenames.append(output_file_path)
                        print(rows_to_delete)

                        # filenames_column.append(output_file_path + column_to_search)


    # delete the rows (goes to expanded_delete.py file)
    expanded_delete.delete_rows(excel_name, rows_to_delete)
    



if __name__ == '__main__':
    main()