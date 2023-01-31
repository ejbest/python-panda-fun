import sys
import os
sys.path.append("/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/site-packages")
import pandas as pd
from datetime import datetime
from datetime import timedelta
def main():
    if len(sys.argv) < 2:
        print("Please provide directory")
        sys.exit(0)
    if not os.path.isdir(sys.argv[1]):
        print("Please provide existing directory")
        sys.exit(0)
    labels = []
    max_length = 0 
    currentTime = datetime.now()
    checkTime = currentTime - timedelta(days = 90)
    for filename in os.listdir(sys.argv[1]):
        if filename.endswith('.xlsx'):
            file_path = os.path.join(sys.argv[1], filename)
            df = pd.read_excel(file_path)
            counterExpired = 0
            for entry in df[['Due_Date']].values:
                try:
                    if not isinstance(entry[0], datetime):
                        datetime_object = datetime.strptime(entry[0], ' %m/%d/%Y %H:%M:%S %p ')
                        if checkTime < datetime_object:
                            counterExpired += 1
                except:
                    pass
            records = str(len(df.index))
            labels.append([file_path,records,str(counterExpired)])
            max_length = len(file_path+records) if len(file_path+records) > max_length else max_length 
    
    for file_path,length,expiredLength in labels:
        line_length = len(file_path+length+expiredLength)
        dots = max_length + 10 - line_length 
        print(file_path + "."*dots + length + " records.")
        if not file_path.endswith("expired.xlsx"):
            if not file_path.endswith("records.xlsx"):
                os.rename( file_path,  file_path[0:-5] + "_" + length + "_" + "records_" + expiredLength + "_expired.xlsx")
            else:
                os.rename( file_path,  file_path[0:-5] + "_" + expiredLength + "_expired.xlsx")

if __name__ == '__main__':
    main()
