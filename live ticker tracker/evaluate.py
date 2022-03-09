import datetime as dt
from fyers_api import fyersModel
import configparser
import time
import numpy as np

# FYERS API AUTHENTICATION
# Reading Configs
config = configparser.ConfigParser()
config.read("config.ini")
client_id = config['Fyers']['client_id']
access_token = config['Fyers']['access_token']

fyers = fyersModel.FyersModel(client_id=client_id, token=access_token, log_path="apiV2")         # Authorize

def get_active_data(df):
    return df[df.Status.isin(['ACTIVE','T1 Hit','SL Hit','SL Zone'])]

def update_status(df):
    for i, row in df.iterrows():
        if dt.date.today() == dt.datetime.strptime(row['Expiry'], '%d%b%Y').date():
            if row['Status'] in ['T1 Hit', 'SL Hit']:
                df.loc[i, 'Status'] = f"Expired-{row['Status']}"
            else:
                df.loc[i, 'Status'] = f"Expired-Stagnant"

def fetch_candles(row, today):
    now = dt.datetime.today()
    if now.time() < dt.time(4, 20):
        reso = 30
    else:
        reso = 15

    hs_data = {"symbol": f"NSE:{row['Stock']}-EQ", "resolution":reso, "date_format":"1", "range_from":today, "range_to":today, "cont_flag":"1"}
    hs1_data = {"symbol": f"NSE:{row['Ticker Name OPT']}", "resolution":reso, "date_format":"1", "range_from":today, "range_to":today, "cont_flag":"1"}
    hs2_data = {"symbol": f"NSE:{row['Ticker Name FUT']}", "resolution":reso, "date_format":"1", "range_from":today, "range_to":today, "cont_flag":"1"}
    hs = fyers.history(hs_data)
    time.sleep(0.25)
    hs1 = fyers.history(hs1_data)
    time.sleep(0.25)
    hs2 = fyers.history(hs2_data)

    # Calculate the required epoch/candle
    mins = (now.minute - (now.minute % 15) - reso) % 60
    hr = now.hour if mins < now.minute else now.hour - 1
    epoch = dt.datetime(now.year, now.month, now.day, hr, mins).timestamp()

    try:            # index the required candle
        sres = hs[np.where(np.array(hs) == epoch)[0][0]]
        s1res = hs1[np.where(np.array(hs1) == epoch)[0][0]]
        s2res = hs2[np.where(np.array(hs2) == epoch)[0][0]]
    except:
        print(f"Candle index not found for trade ID{row['Trade ID']}. Check logs!")

    return sres, s1res, s2res

def check_bull_SL(row, sres, ind, df):
    extended_SL = row['SL'] - row['SL']*0.01                               # in 1% range of SL

    if (dt.datetime.fromtimestamp(sres[0]).time() == dt.time(9, 45)) and row['Status']=='ACTIVE':     # UTC time zone
        if sres[4] <= extended_SL:                      # [4] => close
            df.loc[ind, 'Status'] = 'SL Hit'

        elif extended_SL <= sres[4] <= row['SL']:
            df.loc[ind, 'Status'] = 'SL Zone'

    elif (dt.datetime.fromtimestamp(sres[0]).time() == dt.time(9, 45)) and row['Status']=='SL Zone':
        if sres[4] <= row['SL']:
            df.loc[ind, 'Status'] = 'SL Hit'
        else:
            df.loc[ind, 'Status'] = 'ACTIVE'

    elif (dt.datetime.fromtimestamp(sres[0]).time() == dt.time(3, 45)) and row['Status']=='SL Zone':
        if sres[4] <= extended_SL:
            df.loc[ind, 'Status'] = 'SL Hit'

def check_bear_SL(row, sres, ind, df):
    extended_SL = row['SL'] + row['SL']*0.01

    if (dt.datetime.fromtimestamp(sres[0]).time() == dt.time(9, 45)) and row['Status']=='ACTIVE':     # UTC time zone
        if sres[4] >= extended_SL:                      # [4] => close
            df.loc[ind, 'Status'] = 'SL Hit'

        elif row['SL'] <= sres[4] <= extended_SL:
            df.loc[ind, 'Status'] = 'SL Zone'

    elif (dt.datetime.fromtimestamp(sres[0]).time() == dt.time(9, 45)) and row['Status']=='SL Zone':
        if sres[4] >= row['SL']:
            df.loc[ind, 'Status'] = 'SL Hit'
        else:
            df.loc[ind, 'Status'] = 'ACTIVE'

    elif (dt.datetime.fromtimestamp(sres[0]).time() == dt.time(3, 45)) and row['Status']=='SL Zone':
        if sres[4] >= extended_SL:
            df.loc[ind, 'Status'] = 'SL Hit'

#--------------------------------------------------#
# STRATEGY 1                                       #
#--------------------------------------------------#
# updates data inplace (not good coding practice)

def master(df):
    today = dt.datetime.strftime(dt.datetime.today(), format="%Y-%m-%d")
    
    for ind, row in df.iterrows():
        if row["Status"][:7]!='Expired':
        
            if row['Type']=='Bullish':
                get_bull(df, ind, row, today)

            else:
                get_bear(df, ind, row, today)

# candles = [tstmp O H L C V]
                
def get_bull(df, ind, row, today):
    # Get data 
    sres, ores, fres = fetch_candles(row, today)

    # update common columns
    df.loc[ind, 'Stock CMP'] = sres[4]
    df.loc[ind, 'Current Price OPT'] = ores[4]
    df.loc[ind, 'Current Price FUT'] = fres[4]
    df.loc[ind, 'P&L OPT (UE)'] = (ores[4] - row['Entry Price OPT']) * row['Lot Size']
    df.loc[ind, 'P&L FUT (UE)'] = (fres[4] - row['Entry Price FUT']) * row['Lot Size']
    df.loc[ind, 'Total P&L (UE)'] = df.loc[ind, 'P&L OPT (UE)'] + df.loc[ind, 'P&L FUT (UE)']
    
    # update if alert is active
    if row['Status']=='ACTIVE' or row['Status']=='SL Zone':
        evaluate_active_bull(df, ind, row, sres, ores, fres)
        
def evaluate_active_bull(df, ind, row, sres, ores, fres):
    # check/update status
    if sres[2] >= row['T1']:                                                       # [2] => high
        df.loc[ind, 'Status'] = 'T1 Hit'                                           # [3] => low
        df.loc[ind, 'Exit Price OPT'] = ores[3]                                    
        df.loc[ind, 'Exit Price FUT'] = fres[2]                                    

    else:                                                                         # check SL Hit or not
        check_bull_SL(row, sres, ind, df)
        if df.loc[ind, 'Status'] == 'SL Hit':
            df.loc[ind, 'Exit Price OPT'] = ores[2]
            df.loc[ind, 'Exit Price FUT'] = fres[3]

    
    # Calculate P&L
    if df.loc[ind, 'Status']=='ACTIVE' or df.loc[ind, 'Status']=='SL Zone':       # If T1/SL is still not hit
        df.loc[ind, 'P&L OPT'] = df.loc[ind, 'P&L OPT (UE)']
        df.loc[ind, 'P&L FUT'] = df.loc[ind, 'P&L FUT (UE)']                  

    else:                                                                          # If T1/SL hit, calculate P&L based on exit price
        df.loc[ind, 'P&L OPT'] = (df.loc[ind, 'Exit Price OPT'] - row['Entry Price OPT']) * row['Lot Size']                 
        df.loc[ind, 'P&L FUT'] = (df.loc[ind, 'Exit Price FUT'] - row['Entry Price FUT']) * row['Lot Size']

    df.loc[ind, 'Total P&L'] = df.loc[ind, 'P&L OPT'] + df.loc[ind, 'P&L FUT']     # Update Total P&L
    
def get_bear(df, ind, row, today):
    # Get data 
    sres, ores, fres = fetch_candles(row, today)
    
    # update common columns
    df.loc[ind, 'Stock CMP'] = sres[4] 
    df.loc[ind, 'Current Price OPT'] = ores[4]
    df.loc[ind, 'Current Price FUT'] = fres[4]
    df.loc[ind, 'P&L OPT (UE)'] = (ores[4] - row['Entry Price OPT']) * row['Lot Size']
    df.loc[ind, 'P&L FUT (UE)'] = (row['Entry Price FUT'] - fres[4]) * row['Lot Size']
    df.loc[ind, 'Total P&L (UE)'] = df.loc[ind, 'P&L OPT (UE)'] + df.loc[ind, 'P&L FUT (UE)']
    
    # update if alert is active
    if row['Status']=='ACTIVE' or row['Status']=='SL Zone':
        evaluate_active_bear(df, ind, row, sres, ores, fres)
        
def evaluate_active_bear(df, ind, row, sres, ores, fres):
    # check/update status
    if sres[3] <= row['T1']:                                       # [3] => low 
        df.loc[ind, 'Status'] = 'T1 Hit'                           # [2] => high
        df.loc[ind, 'Exit Price OPT'] = ores[3]                    
        df.loc[ind, 'Exit Price FUT'] = fres[3]                    

    else:
        check_bear_SL(row, sres, ind, df)
        if df.loc[ind, 'Status'] == 'SL Hit':
            df.loc[ind, 'Exit Price OPT'] = ores[2]
            df.loc[ind, 'Exit Price FUT'] = fres[2]                     
    
    # Calculate P&L
    if df.loc[ind, 'Status']=='ACTIVE' or df.loc[ind, 'Status']=='SL Zone':       # If T1/SL is still not hit
        df.loc[ind, 'P&L OPT'] = df.loc[ind, 'P&L OPT (UE)']
        df.loc[ind, 'P&L FUT'] = df.loc[ind, 'P&L FUT (UE)']                

    else:                                                                          # If T1/SL hit, calculate P&L based on exit price
        df.loc[ind, 'P&L OPT'] = (df.loc[ind, 'Exit Price OPT'] - row['Entry Price OPT']) * row['Lot Size']                   
        df.loc[ind, 'P&L FUT'] = (row['Entry Price FUT'] - df.loc[ind, 'Exit Price FUT']) * row['Lot Size']

    df.loc[ind, 'Total P&L'] = df.loc[ind, 'P&L OPT'] + df.loc[ind, 'P&L FUT']     # Update Total P&L
    
#--------------------------------------------------#
# STRATEGY 2                                       #
#--------------------------------------------------#
    
def Master(df):
    today = dt.datetime.strftime(dt.datetime.today(), format="%Y-%m-%d")
    
    for ind, row in df.iterrows():
        if row["Status"][:7]!='Expired':
        
            if row['Type']=='Bullish':
                Get_bull(df, ind, row, today)

            else:
                Get_bear(df, ind, row, today)
                
def Get_bull(df, ind, row, today):
    # Get data 
    sres, ores, o2res = fetch_candles(row, today)
    
    # update common columns
    df.loc[ind, 'Stock CMP'] = sres[4]
    df.loc[ind, 'Current Price OPT1'] = ores[4]
    df.loc[ind, 'Current Price OPT2'] = o2res[4]
    df.loc[ind, 'P&L OPT1 (UE)'] = (ores[4] - row['Entry Price OPT1']) * row['Lot Size']
    df.loc[ind, 'P&L OPT2 (UE)'] = (row['Entry Price OPT2'] - o2res[4]) * row['Lot Size']
    df.loc[ind, 'Total P&L (UE)'] = df.loc[ind, 'P&L OPT1 (UE)'] + df.loc[ind, 'P&L OPT2 (UE)']
    
    # update if alert is active
    if row['Status']=='ACTIVE' or row['Status']=='SL Zone':
        Evaluate_active_bull(df, ind, row, sres, ores, o2res)
        
def Evaluate_active_bull(df, ind, row, sres, ores, o2res):
    # check/update status
    if sres[2] >= row['T1']:                                                       # [2] => high
        df.loc[ind, 'Status'] = 'T1 Hit'                                           # [3] => low
        df.loc[ind, 'Exit Price OPT1'] = ores[2]                                    
        df.loc[ind, 'Exit Price OPT2'] = o2res[2]                                    

    else:
        check_bull_SL(row, sres, ind, df)
        if df.loc[ind, 'Status'] == 'SL Hit':
            df.loc[ind, 'Exit Price OPT1'] = ores[3]
            df.loc[ind, 'Exit Price OPT2'] = o2res[3]                                    
    
    # Calculate P&L
    if df.loc[ind, 'Status']=='ACTIVE' or df.loc[ind, 'Status']=='SL Zone':      # If T1/SL is still not hit
        df.loc[ind, 'P&L OPT1'] = df.loc[ind, 'P&L OPT1 (UE)']
        df.loc[ind, 'P&L OPT2'] = df.loc[ind, 'P&L OPT2 (UE)']                  

    else:                                                                          # If T1/SL hit
        df.loc[ind, 'P&L OPT1'] = (df.loc[ind, 'Exit Price OPT1'] - row['Entry Price OPT1']) * row['Lot Size']                 
        df.loc[ind, 'P&L OPT2'] = (row['Entry Price OPT2'] - df.loc[ind, 'Exit Price OPT2']) * row['Lot Size']

    df.loc[ind, 'Total P&L'] = df.loc[ind, 'P&L OPT1'] + df.loc[ind, 'P&L OPT2']        
        
def Get_bear(df, ind, row, today):
    # Get data 
    sres, ores, o2res = fetch_candles(row, today)
    
    # update common columns
    df.loc[ind, 'Stock CMP'] = sres[4] 
    df.loc[ind, 'Current Price OPT1'] = ores[4]
    df.loc[ind, 'Current Price OPT2'] = o2res[4]
    df.loc[ind, 'P&L OPT1 (UE)'] = (ores[4] - row['Entry Price OPT1']) * row['Lot Size']
    df.loc[ind, 'P&L OPT2 (UE)'] = (row['Entry Price OPT2'] - o2res[4]) * row['Lot Size']
    df.loc[ind, 'Total P&L (UE)'] = df.loc[ind, 'P&L OPT1 (UE)'] + df.loc[ind, 'P&L OPT2 (UE)']
    
    # update if alert is active
    if row['Status']=='ACTIVE' or row['Status']=='SL Zone':
        Evaluate_active_bear(df, ind, row, sres, ores, o2res)
        
def Evaluate_active_bear(df, ind, row, sres, ores, o2res):
    
    # check/update status
    if sres[3] <= row['T1']:                                       # [3] => low
        df.loc[ind, 'Status'] = 'T1 Hit'                           # [2] => high
        df.loc[ind, 'Exit Price OPT1'] = ores[2]                     
        df.loc[ind, 'Exit Price OPT2'] = o2res[2]                    

    else:
        check_bear_SL(row, sres, ind, df)
        if df.loc[ind, 'Status'] == 'SL Hit':
            df.loc[ind, 'Exit Price OPT1'] = ores[3]
            df.loc[ind, 'Exit Price OPT2'] = o2res[3]                     
    
    # Calculate P&L
    if df.loc[ind, 'Status']=='ACTIVE' or df.loc[ind, 'Status']=='SL Zone':      # If T1/SL is still not hit
        df.loc[ind, 'P&L OPT1'] = df.loc[ind, 'P&L OPT1 (UE)']
        df.loc[ind, 'P&L OPT2'] = df.loc[ind, 'P&L OPT2 (UE)']                 

    else:                                                                          # If T1/SL hit
        df.loc[ind, 'P&L OPT1'] = (df.loc[ind, 'Exit Price OPT1'] - row['Entry Price OPT1']) * row['Lot Size']                   
        df.loc[ind, 'P&L OPT2'] = (row['Entry Price OPT2'] - df.loc[ind, 'Exit Price OPT2']) * row['Lot Size']

    df.loc[ind, 'Total P&L'] = df.loc[ind, 'P&L OPT1'] + df.loc[ind, 'P&L OPT2']        
        
# Push updated data back to google sheets
def push_changes(sheet, data):
    values = data.values.tolist()
    for value in values:
        cell = sheet.find(str(value[0]), in_column=0)
        a1 = cell.address
        r = cell.row
        sheet.update(f"{a1}:AA{r}", [value])