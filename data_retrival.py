import requests
import re
import pandas as pd
from conversion import klass_conversion


import datetime
from datetime import datetime, timedelta


def get_data():
    request = requests.get('http://seis-bykl.ru/index.php?ma=1')
    return re.findall(r'title=\"(\d+-\d+-\d+)\s+(\d+\:\d+\:\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)', request.text)

new_ls = []

def conversion(list_of_tuples):
    for event in list_of_tuples:
        #Convert to list because we need to operate on this data
        temp_list = list(event)
        
        #convert from GMT+1 to GMT+8
        gmt1_time = datetime.fromisoformat(f'{temp_list[0]} {temp_list[1]}')  + timedelta(hours=8)
        #split date and time
        gmt8_time = gmt1_time.strftime("%Y-%m-%d %H:%M:%S").split()

        #Update to converted date
        temp_list[0] = gmt8_time[0]
        #Update to converted time
        temp_list[1] = gmt8_time[1]
        #Convert longitude to float()
        temp_list[2] = float(temp_list[2])
        #Convert lantitude to float()
        temp_list[3] = float(temp_list[3])
        #Convert klass to float()
        temp_list[4] = float(temp_list[4])
        #Append magnitudes to temp list
        temp_list.append(klass_conversion(temp_list[4])) 
        #Remove klass value
        del temp_list[4]
        
        #Convert back to tuple()
        new_ls.append(tuple(temp_list))


def fetch_data():
    raw_data = get_data()
    conversion(raw_data)
    df = pd.DataFrame(new_ls, columns =['Дата', 'Время', 'Широта', 'Долгота',  'Магнитуда'])
    df.drop_duplicates(keep="first", inplace=True)
    return df

if __name__ == "__main__":
    raw_data = get_data()
    conversion(raw_data)
    df = pd.DataFrame(new_ls, columns =['Дата', 'Время', 'Широта', 'Долгота',  'Магнитуда'])
    df.drop_duplicates(keep="first", inplace=True)
    pd.set_option("display.max_rows", None, "display.max_columns", None)
    print(df)   
    