from log import last_id
from datetime import datetime as dt
import asyncio
import configparser
import pandas as pd 
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from utils import get_results


# Create a backup of current data before proceeding further
df_old = pd.read_excel('stock data.xlsx')
df_old.to_excel('backup stock data.xlsx', index=False)


# Reading Configs
config = configparser.ConfigParser()
config.read("config.ini")

# Setting configuration values
api_id = config['Telegram']['api_id']
api_hash = str(config['Telegram']['api_hash'])
phone = config['Telegram']['phone']
username = config['Telegram']['username']

# Create client and connect to API
client = TelegramClient(username, api_id, api_hash)
client.start()

user_input_channel = 'https://t.me/SRStockAlertBot'                    #channel link
loop = asyncio.get_event_loop()                                        

# Get channel ID
def getentity():
    return client.get_entity(user_input_channel)
task1 = loop.create_task(getentity())
my_channel = loop.run_until_complete(task1)

# Variables & Parameters
offset_id = 0
min_id = last_id
limit = 100
all_messages = []
total_messages = 0
total_count_limit = 500
anchor_ids = []

# Function to fetch messages 
def get_history(offset_id):
    return client(GetHistoryRequest(
        peer=my_channel,
        offset_id=offset_id,
        offset_date=None,
        add_offset=0,
        limit=limit,
        max_id=0,
        min_id=min_id,
        hash=0
    ))

# Fetch all msgs since this script last ran, up untill today and store it in all_messages.
while True:
    task2 = loop.create_task(get_history(offset_id))
    history = loop.run_until_complete(task2)

    if not history.messages:
        break
    message_batch = history.messages
    anchor_ids.append(message_batch[0].id)
    offset_id = message_batch[-1].id

    for msg in message_batch:
        if 'message' in msg.to_dict().keys() and msg.to_dict()['message'][:5] == 'What:':
            all_messages.append(msg.to_dict()['message'].split())
    
    total_messages = len(all_messages)
    print("offset id:", offset_id, "; Total Messages:", total_messages)
    if total_count_limit != 0 and total_messages >= total_count_limit:  
        break

# For convinience to fetch Stoploss.
all_Messages = []
for i in all_messages:
    all_Messages.append(['Above' if j == 'Below' else j for j in i])

# Filter out required data from each msg in all_Messages and store it into all_values inorder to create a df later.
all_values = []
for i in all_Messages:
    values = []
    for j in i:
        if j in ['What:', 'Time:', 'Stock:', 'Price:',  'Above', 'Target:']:
            if j=='Target:':                                    # Upto 4 targets
                targets = i[i.index(j)+1 : i.index(j)+5]
                targets = [t.replace(',','') for t in targets]

                if 'RS:' in targets:                            # If targets < 4, 'RS:' will crop up in targets, need to remove that.
                    targets = targets[:targets.index('RS:')]
                    targets.extend([None for x in range(4-len(targets))])  # Pad targets with None if targets < 4
                
                values.extend(targets)

            else:
                values.append(i[i.index(j)+1])                   # append value of current parameter to values
                i.remove(j)                                      # Above occurs 2 time (since 2 SL), therefore to fetch '2nd' Above.

    all_values.append(values)                                    # Append all parameter values into all_values


# Format df
df_recent = pd.DataFrame(all_values, columns = ['Type', 'Date', 'Stock', 'Price', 'SL1', 'SL2', 'T1', 'T2', 'T3','T4'])
df_recent['Date'] = pd.to_datetime(df_recent['Date'], format='%d/%m/%Y')
df_recent['Type'] = df_recent['Type'].str[-7:]
df_recent['Stock'] = df_recent['Stock'].str.replace('#', '')
df_recent['Stock'] = df_recent['Stock'].str[:] + '.NS'
df_recent['Price'] = df_recent['Price'].astype(float)
df_recent['SL1'] = df_recent['SL1'].astype(float)
df_recent['SL2'] = df_recent['SL2'].astype(float)
df_recent['T1'] = df_recent['T1'].astype(float)
df_recent['T2'] = df_recent['T2'].astype(float)
df_recent['T3'] = df_recent['T3'].astype(float)
df_recent['T4'] = df_recent['T4'].astype(float)

# Manage excels
df_results = pd.read_excel('Result.xlsx')                # load already existing results on previous data
df_recent_results = get_results(df_recent)               # Get results for recent data

df_updated_results = pd.concat([df_recent_results, df_results])       # merge recent & old results
df_updated_results.to_excel('Result.xlsx', index=False)

df_updated = pd.concat([df_recent, df_old])                           # merge recent & old stock data
df_updated.to_excel('stock data.xlsx', index=False)

# update log file to maintain ID of most recent msg to use it as min_id parameter next time when the script is run.
last_id = anchor_ids[0]
today = dt.today()
with open('log.py', 'w') as file:
    file.write(f"last_id = {last_id}\nlast_updated = '{today}'")


# Update log file with today's results
T1_acc = df_updated_results[df_updated_results['Result']=='Target Achieved'].shape[0] / df_updated_results.shape[0] * 100
SL_acc = df_updated_results[df_updated_results['Result']=='SL Hit'].shape[0] / df_updated_results.shape[0] * 100
sideways_acc = df_updated_results[df_updated_results['Result']=='Sideways'].shape[0] / df_updated_results.shape[0] * 100
NoD_avg = df_updated_results[df_updated_results['Result']=='Target Achieved']['NoD'].mean()
string = f"""

# # # # # # # # # # # # # # # # # # # #
date = {today}
# # # # # # # # # # # # # # # # # # # #

T1 = {T1_acc}
SL = {SL_acc}
sideways = {sideways_acc}
NoD_avg_T1 = {NoD_avg}
         
         """

with open('log.py', 'a') as file:
        file.write(string)