import pandas as pd
import gspread
from evaluate import *

# GOOGLE SHEETS API AUTHENTICATION
scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',
                "https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

gc = gspread.service_account(filename='creds.json',scopes=scope)                 # Authorize

sheet1 = gc.open('SRTicker DB').sheet1                                           # Get Sheet 1 (Strategy 1)
df = pd.DataFrame(sheet1.get_all_records())                                      # convert sheet to pandas df

sheet2 = gc.open('SRTicker DB').worksheet('Strategy2')                           # Get Sheet 2 (Strategy 2)
df2 = pd.DataFrame(sheet2.get_all_records())

# STRATEGY 1
df = get_active_data(df)                                                         # Remove already Expired alerts
update_status(df)                                                                # Check for Expired alerts and update them, if any
master(df)                                                                       # Evaluate all alerts
push_changes(sheet1, df)

# STRATEGY 2
df2 = get_active_data(df2)                                                        # Remove already Expired alerts
update_status(df2)                                                                # Check for Expired alerts and update them, if any
Master(df2)                                                                       # Evaluate all alerts
push_changes(sheet2, df2)