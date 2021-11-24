import pandas as pd
import datetime as dt
import yfinance as yf

def get_results(df):

    Result = []
    fifteenDay_close = []
    NoD = []


    for index, row in df.iterrows():
        
        data = yf.download(row['Stock'], start=row['Date'], end=row['Date']+dt.timedelta(days=19))
        highs = data['High'].round(2)
        lows = data['Low'].round(2)
        closes = data['Close'].round(2)
        fifteenDay_close.append(closes[-1])
        nod = 0
        
        if row['Type']=='Bullish':
            for high,close in list(zip(highs, closes)):
                if high>row['T1']:
                    Result.append('Target Achieved')
                    break
                elif close<row['SL1']:
                    Result.append('SL Hit')
                    break
                    
                nod += 1
                    
            else:
                Result.append('Sideways')
                
        else:
            for low,close in list(zip(lows, closes)):
                if low<row['T1']:
                    Result.append('Target Achieved')
                    break  
                elif close>row['SL1']:
                    Result.append('SL Hit')
                    break
                    
                nod += 1
                
            else:
                Result.append('Sideways')
            
        NoD.append(nod)

    df['Result'] = Result
    df['15Day Close'] = fifteenDay_close
    df['NoD'] = NoD

    return df