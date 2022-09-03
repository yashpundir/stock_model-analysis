import pandas as pd
import gspread
from evaluate import *

message = 'Your token has expired. Please generate a token'
if fyers.get_profile()['message'] != message:

    # GOOGLE SHEETS API AUTHENTICATION
    scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',
                    "https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

    gc = gspread.service_account(filename='creds.json',scopes=scope)                 # Authorize

    for sheet in ['Strategy1', 'Strategy2']:

        sheet1 = gc.open('FnO_Tracker').worksheet(sheet)                           # Get Sheet
        df = pd.DataFrame(sheet1.get_all_records())                                # Convert sheet to pandas df
                 
        if sheet=='Strategy1':                                                     # Check for Expired alerts and update them, if any
            master(df)
        else:
            Master(df)                                                             # Evaluate all alerts   
        update_status(df)                                                             
        push_changes(sheet1, df)

    for sheet in ['Illiquid', 'NCASH', 'Other', 'RTP']:

        sheet1 = gc.open('FnO_Tracker').worksheet(sheet)                           # Get Sheet 
        df = pd.DataFrame(sheet1.get_all_records())                                # Convert sheet to pandas df
        master2(df)                                                                 # Evaluate all alerts    
        update_status2(df)                                                         # Check for Expired alerts and update them, if any                                                            
        push_changes(sheet1, df)