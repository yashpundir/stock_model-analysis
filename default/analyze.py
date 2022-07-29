import pandas as pd
import numpy as np
import mysql.connector
import datetime as dt
import calendar
import configparser
import utils
import logging

# Reading Configs
config = configparser.ConfigParser()
config.read("D:/Yash/Python Projects/tgm_stk_tkr/default/config.ini")
logging.basicConfig(filename='log2.txt', format='\n%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO, datefmt='%d-%b-%y %H:%M:%S')

# Setting configuration values
host = config['SQL']['host']
user = config['SQL']['user']
pwd = config['SQL']['password']
db = config['SQL']['database']

# This month's date range
today = dt.date.today()
last_day = calendar.monthrange(today.year, today.month)[1]
first = dt.date(today.year, today.month, 1)
last = dt.date(today.year, today.month, last_day)

# Connect to MySQL DB
connection = mysql.connector.connect(host=host,
                             user=user,
                             password=pwd,
                             database=db)

cursor = connection.cursor()
query = ("SELECT alert_type, data_date, stock, trigger_price, stoploss, target FROM web_hook_details WHERE data_date BETWEEN %s AND %s ORDER BY data_date DESC")
cursor.execute(query, (dt.datetime.strftime(first, '%Y%m%d'), dt.datetime.strftime(last, '%Y%m%d')))

# Make primary df
df = pd.DataFrame(columns=['alert', 'Date', 'Stock', 'Price', 'SL1', 'T1'], data=cursor.fetchall())
df = df[~(df['alert'] == "")]
cursor.close()
connection.close()

# Data Formatting
disc = {'FO_Bearish':'FO', 'FO_Bullish':'FO', 'Cash_N500_Bullish':'Cash_N500', 'Cash_Other_N500_Bullish':'Cash_Other_N500', 'BO_Rising_Triangle':'BO_Rising_Triangle'}
df.insert(0, 'What', df.alert.map(disc))                                            # Insert Bullish/Bearish Column
df.insert(1, 'Type',df.alert.apply(lambda x: 'Bearish' if x=='FO_Bearish' else 'Bullish'))    # Insert Type of alert
df.drop('alert', axis=1, inplace=True)
df.loc[:, 'SL1'] = df.SL1.apply(lambda x: float([i for i in x.split() if i.replace('.','',1).isdigit()][0]))   # Extracting floating pt from string
df.loc[:, 'Stock'] = df['Stock'].str.replace('#', '') + '.NS'
df.insert(6, 'SL2', np.nan)
df.insert(8, 'T2', np.nan)
df.insert(9, 'T3', np.nan)
df.loc[: ,'Date'] = pd.to_datetime(df['Date'])
df.loc[: ,'Price'] = df['Price'].astype(float)
df.loc[: ,'T1'] = df['T1'].astype(float)

# Filter out
df_fo = df.query('What == "FO"').reset_index(drop=True)
df_co = df.query('What == "Cash_Other_N500"').reset_index(drop=True)
df_nc = df.query('What == "Cash_N500"').reset_index(drop=True)
df_rtp = df.query('What == "BO_Rising_Triangle"').reset_index(drop=True)
dfs = {'FnO':df_fo, 'NCASH':df_nc, 'NCASH_Other':df_co, 'RTP':df_rtp}

# MANAGE EXCEL
def Bob(excel, DF):

    backup = pd.read_excel(f"D:/Yash/Python Projects/tgm_stk_tkr/default/data/{excel}.xlsx")
    day15data = backup[backup.Date>=backup.Date.unique()[:15][-1]]        # Get previous month's last 15 day's data
    backup.drop(labels=range(day15data.shape[0]), axis=0, inplace=True)   # Drop previous month's last 15 day's data
    day15data.drop(labels=['Result', '15DayClose', 'NoD', 'result dummy'], axis=1, inplace=True)   # Drop the results column since they'll be updated again
    df_recent = pd.concat([DF, day15data])                                       # Merge this month's data on top of 15daydata

    df_recent_results = utils.master(df_recent)                            # Get results for this month's data &  15daydata
    result_dummy = ['Target achieved' if x in ['T1','T2','T3'] else x for x in df_recent_results.Result]
    df_recent_results.insert(df_recent_results.shape[1], 'result dummy', result_dummy)
    
    df_updated_results = pd.concat([df_recent_results, backup])            # merge recent & old results
    df_updated_results.to_excel(f"D:/Yash/Python Projects/tgm_stk_tkr/default/data/{excel}.xlsx", index=False)

try:
    Bob('FnO', dfs['FnO'])
    Bob('NCASH', dfs['NCASH'])
    Bob('NCASH_Other', dfs['NCASH_Other'])
    Bob('RTP', dfs['RTP'])
except Exception as e:
    logging.error(e, exc_info=True)