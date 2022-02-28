from last_id import free_last_id, paid_last_id
from datetime import datetime as dt
import configparser
import pandas as pd
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
import utils


# Reading Configs
config = configparser.ConfigParser()
config.read("D:/Yash/Python Projects/tgm_stk_tkr/default/config.ini")

# Setting configuration values
api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']
username = config['Telegram']['username']

# Create client and connect to API
client = TelegramClient(username, api_id, api_hash)
client.start()

#Get channel entity
async def main():
    async for dialog in client.iter_dialogs():
        if dialog.name=='SRStockAlertBot_FnO':
            return dialog.entity

my_channel = client.loop.run_until_complete(main())
    
# Variables & Parameters
all_messages = []
anchor_ids = []
offset_id = 0
total_messages = 0

# Function to fetch messages (main function)
def get_history(offset_id):
    return client(GetHistoryRequest(
        peer=my_channel,
        offset_id=offset_id,
        offset_date=None,
        add_offset=0,
        limit=100,
        max_id=0,
        min_id=paid_last_id,
        hash=0
    ))

while True:
    history = client.loop.run_until_complete(get_history(offset_id))

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
            if j=='Target:':                                    # Upto 3 targets
                targets = i[i.index(j)+1 : i.index(j)+4]
                targets = [t.replace(',','') for t in targets]

                if 'RS:' in targets:                            # If targets < 3, 'RS:' will crop up in targets, need to remove that.
                    targets = targets[:targets.index('RS:')]
                    targets.extend([None for x in range(3-len(targets))])  # Pad targets with None if targets < 3
                
                values.extend(targets)

            else:
                values.append(i[i.index(j)+1])                   # append value of current parameter to values
                i.remove(j)                                      # Above occurs 2 time (since 2 SL), therefore to fetch '2nd' Above.

    all_values.append(values)                                    # Append all parameter values into all_values


# Format df
df_recent = pd.DataFrame(all_values, columns = ['Type', 'Date', 'Stock', 'Price', 'SL1', 'SL2', 'T1', 'T2', 'T3'])
df_recent.insert(0, 'What', df_recent.Type.str[:2])
df_recent['Date'] = pd.to_datetime(df_recent['Date'], format='%d/%m/%Y')
df_recent['Type'] = df_recent['Type'].str[3:10]
df_recent['Stock'] = df_recent['Stock'].str.replace('#', '')
df_recent['Stock'] = df_recent['Stock'].str[:] + '.NS'
df_recent['Price'] = df_recent['Price'].astype(float)
df_recent['SL1'] = df_recent['SL1'].astype(float)
df_recent['SL2'] = df_recent['SL2'].astype(float)
df_recent['T1'] = df_recent['T1'].astype(float)
df_recent['T2'] = df_recent['T2'].astype(float)
df_recent['T3'] = df_recent['T3'].astype(float)

# MANAGE EXCELS

# Adding the previous 15 day data from current data to df_recent in order to be evaluated again
backup = pd.read_excel('D:/Yash/Python Projects/tgm_stk_tkr/default/data/paid channel/backup data.xlsx')
day15data = backup[backup.Date>=backup.Date.unique()[:15][-1]]        # Get previous 15 day's data from current data
backup = pd.concat([df_recent, backup])                               # update backup data with df_recent
backup.to_excel('D:/Yash/Python Projects/tgm_stk_tkr/default/data/paid channel/backup data.xlsx', index=False)

df_recent = pd.concat([df_recent, day15data])
df_recent_results = utils.master(df_recent)                            # Get results for recent & previous 15 day data
result_dummy = ['Target achieved' if x in ['T1','T2','T3'] else x for x in df_recent_results.Result]
df_recent_results.insert(df_recent_results.shape[1], 'result dummy', result_dummy)

df_result = pd.read_excel('D:/Yash/Python Projects/tgm_stk_tkr/default/data/paid channel/Result.xlsx') 
df_result.drop(labels=range(day15data.shape[0]), axis=0, inplace=True)    # Drop previous 15 day data from current data
df_updated_results = pd.concat([df_recent_results, df_result])            # merge recent & old results
df_updated_results.to_excel('D:/Yash/Python Projects/tgm_stk_tkr/default/data/paid channel/Result.xlsx', index=False)

# update last_id file to maintain ID of most recent msg to use it as min_id parameter next time when the script is run.
last_id = anchor_ids[0]
today = dt.today()
with open('D:/Yash/Python Projects/tgm_stk_tkr/default/last_id.py', 'w') as file:
    file.write(f"free_last_id = {free_last_id}\npaid_last_id = {last_id}\nlast_updated = '{today}'")

client.disconnect()