import datetime as dt
import yfinance as yf
import numpy as np


# Function that evaluates the alerts and organizes the result into the df
def master(df):
    Result = []
    NoD = []
    fifteenDay_close = []


    for index, row in df.iterrows():

        data = yf.download(row['Stock'], start=row['Date'], end=row['Date']+dt.timedelta(days=30))
        try:
            data = data.iloc[:15, :]
        except:
            pass
            
        highs = data['High'].round(2)
        lows = data['Low'].round(2)
        closes = data['Close'].round(2)
        day = 0
        latch = 0
        SL_counter = 1
        result = ''
        
        if row['Type']=='Bullish':
            info = get_bull(row, highs, closes, day, latch, SL_counter, result)
        else:
            info = get_bear(row, lows, closes, day, latch, SL_counter, result)
            
        Result.append(info[0])
        NoD.append(info[1])
        fifteenDay_close.append(info[2])
        

    df.insert(df.shape[1], 'Result', Result)
    df.insert(df.shape[1], '15DayClose', fifteenDay_close)
    df.insert(df.shape[1], 'NoD', NoD)
    
    return df

# Function to evaluate a bull alert
def get_bull(row, highs, closes, day, latch, SL_counter, result):
    
    for high,close in list(zip(highs, closes)):                                  # iterating over each days data for this stock
        day += 1
                                                                              
        if not(np.isnan(row['T3'])) and high>row['T3'] and latch<=2:             # Latch ensures once the highest target is
            result = 'T3'                                                        # achieved, the result would be latched on to that &
            latch = 3                                                            # wont change even if the stock starts to plummet. 
            NOD = day

        elif not(np.isnan(row['T2'])) and high>row['T2'] and latch<=1:
            result = 'T2'
            latch = 2
            NOD = day

        elif not(np.isnan(row['T1'])) and high>row['T1'] and latch<=0:
            result = 'T1'
            latch = 1
            NOD = day


        if close < row['SL1'] and latch==0:                   # SL Hit if close < SL1 for 2 consecutive days
            if SL_counter==2:
                result = 'SL Hit'
                NOD = day
                break
            else:
                SL_counter += 1

        elif SL_counter == 2:
            SL_counter -= 1



    if result=='':
        if len(closes) == 15:
            result = 'STAGNANT'
            NOD = day
        else:
            result = 'ON'
            NOD = day
            
    return result, NOD, closes[-1]

# Function to evaluate a bear alert
def get_bear(row, lows, closes, day, latch, SL_counter, result):
    
    for low,close in list(zip(lows, closes)):                                # iterating over each days data for this stock
        day += 1

        if not(np.isnan(row['T3'])) and low<row['T3'] and latch<=2:
            result = 'T3'
            latch = 3
            NOD = day

        elif not(np.isnan(row['T2'])) and low<row['T2'] and latch<=1:
            result = 'T2'
            latch = 2
            NOD = day

        elif not(np.isnan(row['T1'])) and low<row['T1'] and latch<=0:
            result = 'T1'
            latch = 1
            NOD = day


        if close > row['SL1'] and latch==0:                   # SL Hit if close > SL1 for 2 consecutive days
            if SL_counter==2:
                result = 'SL Hit'
                NOD = day
                break
            else:
                SL_counter += 1

        elif SL_counter == 2:
            SL_counter -= 1


    if result=='':
        if len(closes) == 15:
            result = 'STAGNANT'
            NOD = day
        else:
            result = 'ON'
            NOD = day
            
    
    return result, NOD, closes[-1]