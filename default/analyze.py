import pandas as pd
import numpy as np
import datetime as dt
import gspread
import configparser
import logging

# Reading Configs
config = configparser.ConfigParser()
config.read("config.ini")
logging.basicConfig(filename='logs.txt', format='\n%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO, datefmt='%d-%b-%y %H:%M:%S')

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',
                    "https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

gc = gspread.service_account(filename='creds.json',scopes=scope)

sheets = {'Strategy1':'', 'Strategy2':'', 'Illiquid':'', 'NCASH':'', 'Other':'', 'RTP':''}
for sheet in sheets:
    sheet1 = gc.open('FnO_Tracker').worksheet(sheet)                           # Get Sheet
    sheets[sheet] = pd.DataFrame(sheet1.get_all_records())

# Data formatting for FO
df1 = sheets['Strategy1']
df2 = sheets['Strategy2']
df3 = sheets['Illiquid']

df1 = df1[['Type', 'Trigger Date', 'Stock', 'Trigger Price', 'SL', 'T1', 'Status', 'Trade Closed at', 'Closing day']]
df2 = df2[['Type', 'Trigger Date', 'Stock', 'Trigger Price', 'SL', 'T1', 'Status', 'Trade Closed at', 'Closing day']]
df3 = df3[['Type', 'Trigger Date', 'Stock', 'Trigger Price', 'SL', 'T1', 'Status', 'Trade Closed at', 'Closing day']]

df = pd.concat([df1,df2,df3], axis=0)
df['Trigger Date'] = pd.to_datetime(df['Trigger Date'], format='%d/%m/%Y')
df.drop_duplicates(inplace=True)
df.sort_values(by='Trigger Date', axis=0, inplace=True, ascending=False)         # maybe not needed
df.insert(0, 'What', 'FO')
df.reset_index(drop=True, inplace=True)
NoD = [((dt.datetime.strptime(row['Closing day'], '%d/%m/%Y')).date() - row['Trigger Date'].date()).days+1 if row['Closing day']!='' else 0 for i,row in df.iterrows()] # If trade closed, calculate NoD, else if trade is active, NoD=0
df['Closing day'] = NoD
df.rename(columns={'Status':'Result','Trigger Date':'Date','Trigger Price':'Price','SL':'SL1', 'Closing day':'NoD'}, inplace=True)
result_dummy = df.Result.map({'T1 Hit':'Target achieved', 'SL Hit':'SL Hit', 'SL Zone':'ON', 'ACTIVE':'ON', 'Expired-T1 Hit':'Target achieved', 'Expired-SL Hit':'SL Hit', 'Expired-Stagnant':'STAGNANT'})
df.insert(df.shape[-1], 'result dummy', result_dummy)
df = df[['What','Type', 'Date', 'Stock', 'Price', 'SL1', 'T1', 'Result', 'Trade Closed at', 'NoD', 'result dummy']]

# Data formatting for NCASH, Other, RTP
df4 = sheets['NCASH']
df5 = sheets['Other']
df6 = sheets['RTP']

df4 = df4[['Type', 'Trigger Date', 'Stock', 'Trigger Price', 'SL', 'T1', 'Status', 'Closing day', 'Trade Closed at']]
df5 = df5[['Type', 'Trigger Date', 'Stock', 'Trigger Price', 'SL', 'T1', 'Status', 'Closing day', 'Trade Closed at']]
df6 = df6[['Type', 'Trigger Date', 'Stock', 'Trigger Price', 'SL', 'T1', 'Status', 'Closing day', 'Trade Closed at']]

for dff,what in list(zip([df4, df5, df6],['Cash_N500','Cash_Other_N500','BO_Rising_Triangle'])):
    dff.loc[:, 'Trigger Date'] = pd.to_datetime(dff['Trigger Date'], format='%d/%m/%Y')
    dff.insert(0, 'What', what)
    NoD = [((dt.datetime.strptime(row['Closing day'], '%d/%m/%Y')).date() - row['Trigger Date'].date()).days+1 if row['Closing day']!='' else 0 for i,row in dff.iterrows()]
    dff.loc[:, 'Closing day'] = NoD
    dff.rename(columns={'Status':'Result','Trigger Date':'Date','Trigger Price':'Price','SL':'SL1', 'Closing day':'NoD'}, inplace=True)
    result_dummy = dff.Result.map({'T1 Hit':'Target achieved', 'SL Hit':'SL Hit', 'SL Zone':'ON', 'ACTIVE':'ON', 'Expired-T1 Hit':'Target achieved', 'Expired-SL Hit':'SL Hit', 'Expired-Stagnant':'STAGNANT'})
    dff.insert(dff.shape[-1], 'result dummy', result_dummy)
    dff = dff[['What','Type', 'Date', 'Stock', 'Price', 'SL1', 'T1', 'Result', 'Trade Closed at', 'NoD', 'result dummy']]

df.to_excel('data/FnO.xlsx', index=False)
df4.to_excel('data/NCASH.xlsx', index=False)
df5.to_excel('data/NCASH_Other.xlsx', index=False)
df6.to_excel('data/RTP.xlsx', index=False)