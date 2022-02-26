import datetime as dt
from fyers_api import fyersModel
import configparser

# FYERS API AUTHENTICATION
# Reading Configs
config = configparser.ConfigParser()
config.read("config.ini")
client_id = config['Fyers']['client_id']
access_token = config['Fyers']['access_token']

fyers = fyersModel.FyersModel(client_id=client_id, token=access_token, log_path="apiV2")         # Authorize

def get_active_data(df):
    return df[df.Status.isin(['ACTIVE','T1 Hit','SL Hit','Strike 1'])]

def update_status(df):
    for i, row in df.iterrows():
        if dt.date.today() == dt.datetime.strptime(row['Expiry'], '%d%b%Y').date():
            df.loc[i, 'Status'] = 'Expired'

#--------------------------------------------------#
# FOR STRATEGY 1                                   #
#--------------------------------------------------#
# updates data inplace (not good coding practice)

def master(df):
    today = dt.datetime.strftime(dt.datetime.today(), format="%Y-%m-%d")
    
    for ind, row in df.iterrows():
        if row["Status"]!='Expired':
        
            if row['Type']=='Bullish':
                get_bull(df, ind, row, today)

            else:
                get_bear(df, ind, row, today)

# candles = [tstmp O H L C V]
                
def get_bull(df, ind, row, today):
    # Get data 
    hs_data = {"symbol": f"NSE:{row['Stock']}-EQ", "resolution":"15", "date_format":"1", "range_from":today, "range_to":today,                              "cont_flag":"1"}
    ho_data = {"symbol": f"NSE:{row['Ticker Name OPT']}", "resolution":"15", "date_format":"1", "range_from":today, "range_to":today,                      "cont_flag":"1"}
    hf_data = {"symbol": f"NSE:{row['Ticker Name FUT']}", "resolution":"15", "date_format":"1", "range_from":today, "range_to":today,                      "cont_flag":"1"}
    hs = fyers.history(hs_data)
    ho = fyers.history(ho_data)
    hf = fyers.history(hf_data)

#     try:
    sres = hs['candles'][-1]
    ores = ho['candles'][-1]
    fres = hf['candles'][-1]
#     except:
#         print(f"api response not ok for Trade ID {row['Trade ID']}")
    
    # update common columns
    df.loc[ind, 'Stock CMP'] = sres[4]
    df.loc[ind, 'Current Price OPT'] = ores[4]
    df.loc[ind, 'Current Price FUT'] = fres[4]
    df.loc[ind, 'P&L OPT (UE)'] = (ores[4] - row['Entry Price OPT']) * row['Lot Size']
    df.loc[ind, 'P&L FUT (UE)'] = (fres[4] - row['Entry Price FUT']) * row['Lot Size']
    df.loc[ind, 'Total P&L (UE)'] = df.loc[ind, 'P&L OPT (UE)'] + df.loc[ind, 'P&L FUT (UE)']
    
    # update if alert is active
    if row['Status']=='ACTIVE' or row['Status']=='Strike 1':
        evaluate_active_bull(df, ind, row, sres, ores, fres)
        
def evaluate_active_bull(df, ind, row, sres, ores, fres):
    
    # check/update status
    if sres[2] >= row['T1']:                                                       # [2] => high
        df.loc[ind, 'Status'] = 'T1 Hit'                                           # [3] => low
        df.loc[ind, 'Exit Price OPT'] = ores[3]                                    
        df.loc[ind, 'Exit Price FUT'] = fres[2]                                    

    elif (dt.datetime.fromtimestamp(sres[0]).time() == dt.time(9, 45)) and (sres[4] <= row['SL']):    # UTC time zone
        if row['Status'] == 'ACTIVE':                                             # [4] => close
            df.loc[ind, 'Status'] = 'Strike 1'                   
        else:
            df.loc[ind, 'Status'] = 'SL Hit'
            df.loc[ind, 'Exit Price OPT'] = ores[2]
            df.loc[ind, 'Exit Price FUT'] = fres[3]                                     
    
    # Calculate P&L
    if df.loc[ind, 'Status']=='ACTIVE' or df.loc[ind, 'Status']=='Strike 1':       # If T1/SL is still not hit
        df.loc[ind, 'P&L OPT'] = df.loc[ind, 'P&L OPT (UE)']
        df.loc[ind, 'P&L FUT'] = df.loc[ind, 'P&L FUT (UE)']                  

    else:                                                                          # If T1/SL hit, calculate P&L based on exit price
        df.loc[ind, 'P&L OPT'] = (df.loc[ind, 'Exit Price OPT'] - row['Entry Price OPT']) * row['Lot Size']                 
        df.loc[ind, 'P&L FUT'] = (df.loc[ind, 'Exit Price FUT'] - row['Entry Price FUT']) * row['Lot Size']

    df.loc[ind, 'Total P&L'] = df.loc[ind, 'P&L OPT'] + df.loc[ind, 'P&L FUT']     # Update Total P&L
    
def get_bear(df, ind, row, today):
    # Get data 
    hs_data = {"symbol": f"NSE:{row['Stock']}-EQ", "resolution":"15", "date_format":"1", "range_from":today, "range_to":today,                              "cont_flag":"1"}
    ho_data = {"symbol": f"NSE:{row['Ticker Name OPT']}", "resolution":"15", "date_format":"1", "range_from":today, "range_to":today,                      "cont_flag":"1"}
    hf_data = {"symbol": f"NSE:{row['Ticker Name FUT']}", "resolution":"15", "date_format":"1", "range_from":today, "range_to":today,                      "cont_flag":"1"}
    hs = fyers.history(hs_data)
    ho = fyers.history(ho_data)
    hf = fyers.history(hf_data)

#     try:
    sres = hs['candles'][-1]
    ores = ho['candles'][-1]
    fres = hf['candles'][-1]
#     except:
#         print(f"api response not ok for Trade ID {row['Trade ID']}")
    
    # update common columns
    df.loc[ind, 'Stock CMP'] = sres[4] 
    df.loc[ind, 'Current Price OPT'] = ores[4]
    df.loc[ind, 'Current Price FUT'] = fres[4]
    df.loc[ind, 'P&L OPT (UE)'] = (ores[4] - row['Entry Price OPT']) * row['Lot Size']
    df.loc[ind, 'P&L FUT (UE)'] = (row['Entry Price FUT'] - fres[4]) * row['Lot Size']
    df.loc[ind, 'Total P&L (UE)'] = df.loc[ind, 'P&L OPT (UE)'] + df.loc[ind, 'P&L FUT (UE)']
    
    # update if alert is active
    if row['Status']=='ACTIVE' or row['Status']=='Strike 1':
        evaluate_active_bear(df, ind, row, sres, ores, fres)
        
def evaluate_active_bear(df, ind, row, sres, ores, fres):
    
    # check/update status
    if sres[3] <= row['T1']:                                       # [3] => low 
        df.loc[ind, 'Status'] = 'T1 Hit'                           # [2] => high
        df.loc[ind, 'Exit Price OPT'] = ores[3]                    
        df.loc[ind, 'Exit Price FUT'] = fres[3]                    

    elif (dt.datetime.fromtimestamp(sres[0]).time() == dt.time(9, 45)) and (sres[4] >= row['SL']):    # UTC time zone
        if row['Status'] == 'ACTIVE':                                             # [4] => close
            df.loc[ind, 'Status'] = 'Strike 1'                   
        else:
            df.loc[ind, 'Status'] = 'SL Hit'
            df.loc[ind, 'Exit Price OPT'] = ores[2]
            df.loc[ind, 'Exit Price FUT'] = fres[2]                     
    
    # Calculate P&L
    if df.loc[ind, 'Status']=='ACTIVE' or df.loc[ind, 'Status']=='Strike 1':       # If T1/SL is still not hit
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
        if row["Status"]!='Expired':
        
            if row['Type']=='Bullish':
                Get_bull(df, ind, row, today)

            else:
                Get_bear(df, ind, row, today)
                
def Get_bull(df, ind, row, today):
    # Get data 
    hs_data = {"symbol": f"NSE:{row['Stock']}-EQ", "resolution":"15", "date_format":"1", "range_from":today, "range_to":today,                              "cont_flag":"1"}
    ho_data = {"symbol": f"NSE:{row['Ticker Name OPT1']}", "resolution":"15", "date_format":"1", "range_from":today, "range_to":today,                      "cont_flag":"1"}
    hf_data = {"symbol": f"NSE:{row['Ticker Name OPT2']}", "resolution":"15", "date_format":"1", "range_from":today, "range_to":today,                      "cont_flag":"1"}
    hs = fyers.history(hs_data)
    ho = fyers.history(ho_data)
    hf = fyers.history(hf_data)

#     try:
    sres = hs['candles'][-1]
    ores = ho['candles'][-1]
    o2res = hf['candles'][-1]
#     except:
#         print(f"api response not ok for Trade ID {row['Trade ID']}")
    
    # update common columns
    df.loc[ind, 'Stock CMP'] = sres[4]
    df.loc[ind, 'Current Price OPT1'] = ores[4]
    df.loc[ind, 'Current Price OPT2'] = o2res[4]
    df.loc[ind, 'P&L OPT1 (UE)'] = (ores[4] - row['Entry Price OPT1']) * row['Lot Size']
    df.loc[ind, 'P&L OPT2 (UE)'] = (row['Entry Price OPT2'] - o2res[4]) * row['Lot Size']
    df.loc[ind, 'Total P&L (UE)'] = df.loc[ind, 'P&L OPT1 (UE)'] + df.loc[ind, 'P&L OPT2 (UE)']
    
    # update if alert is active
    if row['Status']=='ACTIVE' or row['Status']=='Strike 1':
        Evaluate_active_bull(df, ind, row, sres, ores, o2res)
        
def Evaluate_active_bull(df, ind, row, sres, ores, o2res):
    
    # check/update status
    if sres[2] >= row['T1']:                                                       # [2] => high
        df.loc[ind, 'Status'] = 'T1 Hit'                                           # [3] => low
        df.loc[ind, 'Exit Price OPT1'] = ores[2]                                    
        df.loc[ind, 'Exit Price OPT2'] = o2res[2]                                    

    elif (dt.datetime.fromtimestamp(sres[0]).time() == dt.time(9, 45)) and (sres[4] <= row['SL']):    # UTC time zone
        if row['Status'] == 'ACTIVE':                                             # [4] => close
            df.loc[ind, 'Status'] = 'Strike 1'                   
        else:
            df.loc[ind, 'Status'] = 'SL Hit'
            df.loc[ind, 'Exit Price OPT1'] = ores[3]
            df.loc[ind, 'Exit Price OPT2'] = o2res[3]                                    
    
    # Calculate P&L
    if df.loc[ind, 'Status']=='ACTIVE' or df.loc[ind, 'Status']=='Strike 1':      # If T1/SL is still not hit
        df.loc[ind, 'P&L OPT1'] = df.loc[ind, 'P&L OPT1 (UE)']
        df.loc[ind, 'P&L OPT2'] = df.loc[ind, 'P&L OPT2 (UE)']                  

    else:                                                                          # If T1/SL hit
        df.loc[ind, 'P&L OPT1'] = (df.loc[ind, 'Exit Price OPT1'] - row['Entry Price OPT1']) * row['Lot Size']                 
        df.loc[ind, 'P&L OPT2'] = (row['Entry Price OPT2'] - df.loc[ind, 'Exit Price OPT2']) * row['Lot Size']

    df.loc[ind, 'Total P&L'] = df.loc[ind, 'P&L OPT1'] + df.loc[ind, 'P&L OPT2']        
        
def Get_bear(df, ind, row, today):
    # Get data 
    hs_data = {"symbol": f"NSE:{row['Stock']}-EQ", "resolution":"15", "date_format":"1", "range_from":today, "range_to":today,                              "cont_flag":"1"}
    ho_data = {"symbol": f"NSE:{row['Ticker Name OPT1']}", "resolution":"15", "date_format":"1", "range_from":today, "range_to":today,                      "cont_flag":"1"}
    hf_data = {"symbol": f"NSE:{row['Ticker Name OPT2']}", "resolution":"15", "date_format":"1", "range_from":today, "range_to":today,                      "cont_flag":"1"}
    hs = fyers.history(hs_data)
    ho = fyers.history(ho_data)
    hf = fyers.history(hf_data)

#     try:
    sres = hs['candles'][-1]
    ores = ho['candles'][-1]
    o2res = hf['candles'][-1]
#     except:
#         print(f"api response not ok for Trade ID {row['Trade ID']}")
    
    # update common columns
    df.loc[ind, 'Stock CMP'] = sres[4] 
    df.loc[ind, 'Current Price OPT1'] = ores[4]
    df.loc[ind, 'Current Price OPT2'] = o2res[4]
    df.loc[ind, 'P&L OPT1 (UE)'] = (ores[4] - row['Entry Price OPT1']) * row['Lot Size']
    df.loc[ind, 'P&L OPT2 (UE)'] = (row['Entry Price OPT2'] - o2res[4]) * row['Lot Size']
    df.loc[ind, 'Total P&L (UE)'] = df.loc[ind, 'P&L OPT1 (UE)'] + df.loc[ind, 'P&L OPT2 (UE)']
    
    # update if alert is active
    if row['Status']=='ACTIVE' or row['Status']=='Strike 1':
        Evaluate_active_bear(df, ind, row, sres, ores, o2res)
        
def Evaluate_active_bear(df, ind, row, sres, ores, o2res):
    
    # check/update status
    if sres[3] <= row['T1']:                                       # [3] => low
        df.loc[ind, 'Status'] = 'T1 Hit'                           # [2] => high
        df.loc[ind, 'Exit Price OPT1'] = ores[2]                     
        df.loc[ind, 'Exit Price OPT2'] = o2res[2]                    

    elif (dt.datetime.fromtimestamp(sres[0]).time() == dt.time(9, 45)) and (sres[4] >= row['SL']):    # UTC time zone
        if row['Status'] == 'ACTIVE':                                             # [4] => close
            df.loc[ind, 'Status'] = 'Strike 1'                   
        else:
            df.loc[ind, 'Status'] = 'SL Hit'
            df.loc[ind, 'Exit Price OPT1'] = ores[3]
            df.loc[ind, 'Exit Price OPT2'] = o2res[3]                     
    
    # Calculate P&L
    if df.loc[ind, 'Status']=='ACTIVE' or df.loc[ind, 'Status']=='Strike 1':      # If T1/SL is still not hit
        df.loc[ind, 'P&L OPT1'] = df.loc[ind, 'P&L OPT1(UE)']
        df.loc[ind, 'P&L OPT2'] = df.loc[ind, 'P&L OPT2 (UE)']                 

    else:                                                                          # If T1/SL hit
        df.loc[ind, 'P&L OPT1'] = (df.loc[ind, 'Exit Price OPT1'] - row['Entry Price OPT1']) * row['Lot Size']                   
        df.loc[ind, 'P&L OPT2'] = (row['Entry Price OPT2'] - df.loc[ind, 'Exit Price OPT2']) * row['Lot Size']

    df.loc[ind, 'Total P&L'] = df.loc[ind, 'P&L OPT1'] + df.loc[ind, 'P&L OPT2']        
        
    
# Push updated data back to google sheets
def push_changes(sheet, df):
    values = df.values.tolist()
    for value in values:
        cell = sheet.find(str(value[0]), in_column=0)
        a1 = cell.address
        r = cell.row
        sheet.update(f"{a1}:AA{r}", [value])