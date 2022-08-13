import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import calendar
import json

stats = {"Type":{"FO":{"total_alerts":0, "avg_NoD":0, "total_stagnant":0, "total_bull":0, "total_bear":0},
        "Cash_N500":{"total_alerts":0, "avg_NoD":0, "total_stagnant":0, "total_bull":0, "total_bear":0},
        "Cash_Other_N500":{"total_alerts":0, "avg_NoD":0, "total_stagnant":0, "total_bull":0, "total_bear":0},
        "BO_Rising_Triangle":{"total_alerts":0, "avg_NoD":0, "total_stagnant":0, "total_bull":0, "total_bear":0},
        "Combined":{"total_alerts":0, "avg_NoD":0, "total_stagnant":0, "total_bull":0, "total_bear":0}},
        "to_date":0}
        
dfcf = pd.read_excel('data/FnO.xlsx', engine="openpyxl")
dfcn = pd.read_excel('data/NCASH.xlsx', engine="openpyxl")
dfno = pd.read_excel('data/NCASH_Other.xlsx', engine="openpyxl")
dfrtp = pd.read_excel('data/RTP.xlsx', engine="openpyxl")


def statistics(df):
    total_alerts = df.shape[0]                     # total alerts
    stats['Type'][df.iloc[0,0]]["total_alerts"] = total_alerts

    total_bull = df[df.Type=='Bullish'].shape[0]             # Total bullish alerts
    stats['Type'][df.iloc[0,0]]["total_bull"] = total_bull

    total_bear = df[df.Type=='Bearish'].shape[0]         #Total bearish alerts
    stats['Type'][df.iloc[0,0]]["total_bear"] = total_bear

    Stagnant = df[df.Result=='STAGNANT'].shape[0]           #Total stagnant alerts
    stats['Type'][df.iloc[0,0]]["total_stagnant"] = Stagnant
    
    avg_nod = df[df['result dummy']=='Target achieved'].NoD.mean()     # Avg no. of days needed to reach the highest target
    stats['Type'][df.iloc[0,0]]["avg_NoD"] = avg_nod

def TASL(df):

    ons = df[df.Result=='ON'].index # Identify OPEN/ON alerts
    df.drop(ons, axis=0, inplace=True) # Drop the ON alerts from analysis

    # Total Target achieved and SL Hit alerts
    TA = df[df['result dummy']=='Target achieved'].shape[0]
    SL = df[df['result dummy']=='SL Hit'].shape[0]

    # (+)ive & (-)ive STAGNANT alerts
    n1 = df[(df['result dummy']=='STAGNANT') & (df.Type=='Bullish') & (df['15DayClose']<df.Price)].shape[0]
    p1 = df[(df['result dummy']=='STAGNANT') & (df.Type=='Bullish') & (df['15DayClose']>df.Price)].shape[0]

    n2 = df[(df['result dummy']=='STAGNANT') & (df.Type=='Bearish') & (df['15DayClose']>df.Price)].shape[0]
    p2 = df[(df['result dummy']=='STAGNANT') & (df.Type=='Bearish') & (df['15DayClose']<df.Price)].shape[0]

    p = p1 + p2
    n = n1 + n2

    # Weightage of 0.5 to TA & SL
    TA += p*0.5
    SL += n*0.5 

    stat = {'Target achieved':round(TA/(TA+SL)*100, 2), 'SL Hit':round(SL/(TA+SL)*100,2)}

    plt.figure(figsize=(9,6))
    plt.bar(stat.keys(), stat.values(), color=['forestgreen','indianred'])

    for i,j in enumerate(stat):
        plt.annotate(f"{stat[j]}%", xy=(i-0.1, stat[j]+0.5), xycoords='data', fontsize=15)

    plt.yticks(fontweight='bold')
    plt.xticks(fontweight='bold')
    plt.ylabel(ylabel='%', fontsize=20)
    plt.savefig(f"report/data/plots/{df.iloc[0, 0]}/tasl.png")
    plt.close()

    return [ons]

def bull_bear_plot(df, side):
    # Total bullish alerts
    side_df = df[df.Type==side]
    # Total Target achieved and SL Hit alerts in bull df
    TA = side_df[side_df['result dummy']=='Target achieved'].shape[0]
    SL = side_df[side_df['result dummy']=='SL Hit'].shape[0]
    # (+)ive & (-)ive STAGNANT alerts
    if side=='Bullish':
        n = side_df[(side_df['result dummy']=='STAGNANT') & (side_df['15DayClose']<side_df.Price)].shape[0]
        p = side_df[(side_df['result dummy']=='STAGNANT') & (side_df['15DayClose']>side_df.Price)].shape[0]
    else:
        n = side_df[(side_df['result dummy']=='STAGNANT') & (side_df['15DayClose']>side_df.Price)].shape[0]
        p = side_df[(side_df['result dummy']=='STAGNANT') & (side_df['15DayClose']<side_df.Price)].shape[0]
    # Weightage of 0.5 to TA & SL
    TA += p*0.5
    SL += n*0.5 
    stat = {'Target achieved':round(TA/(TA+SL)*100, 2), 'SL Hit':round(SL/(TA+SL)*100,2)}

    plt.figure(figsize=(9,6))
    plt.bar(stat.keys(), stat.values(), color=['forestgreen','indianred'])

    for i,j in enumerate(stat):
        plt.annotate(f"{stat[j]}%", xy=(i-0.1, stat[j]+0.5), xycoords='data', fontsize=15)
        
    plt.yticks(fontweight='bold')
    plt.xticks(fontweight='bold')
    plt.ylabel(ylabel='%', fontsize=20)
    plt.savefig(f"report/data/plots/{df.iloc[0, 0]}/{side}.png")
    plt.close()

def final(df, opens):
    dfm = df.sort_values(by='Date').set_index('Date')
    months = []
    mos = pd.Series(dfm.index.to_numpy().astype('datetime64[M]')).unique()
    for mo in mos:
        months.append(dt.datetime.date(pd.to_datetime(mo)).strftime(format="%b%y"))

    monthly_stats = []
    monthly_alerts = []
    for i in months:
        month = dt.datetime.strptime(i, "%b%y").month                                               # current_month
        year = dt.datetime.strptime(i, "%b%y").year                                                 # current_year
        end = calendar.monthrange(year, month)[1]                      
        current_month = dfm.loc[f"{year}-{month}-01":f"{year}-{month}-{end}"]                  # get that month's df
        
        monthly_alerts.append(current_month.shape[0])                                   # total alerts in current month
        
        # Total Target achieved and SL Hit alerts in current month
        TA = current_month[current_month['result dummy']=='Target achieved'].shape[0]
        SL = current_month[current_month['result dummy']=='SL Hit'].shape[0]
        
        # (+)ive & (-)ive STAGNANT alerts
        n1 = current_month[(current_month['result dummy']=='STAGNANT') & (current_month.Type=='Bullish') & (current_month['15DayClose']<current_month.Price)].shape[0]
        p1 = current_month[(current_month['result dummy']=='STAGNANT') & (current_month.Type=='Bullish') & (current_month['15DayClose']>current_month.Price)].shape[0]

        n2 = current_month[(current_month['result dummy']=='STAGNANT') & (current_month.Type=='Bearish') & (current_month['15DayClose']>current_month.Price)].shape[0]
        p2 = current_month[(current_month['result dummy']=='STAGNANT') & (current_month.Type=='Bearish') & (current_month['15DayClose']<current_month.Price)].shape[0]

        p = p1 + p2
        n = n1 + n2

        TA += p*0.5
        SL += n*0.5 
        current_stat = {'Target achieved':round(TA/(TA+SL)*100, 2), 'SL Hit':round(SL/(TA+SL)*100,2)}
        monthly_stats.append(current_stat)

    line_data = ([x['Target achieved'] for x in monthly_stats]), ([x['SL Hit'] for x in monthly_stats])

    fig, ax = plt.subplots(figsize=(10,6))
    ax.set_facecolor('white')

    ax.plot(months, line_data[0], marker='o', color='darkgreen')
    ax.plot(months, line_data[1], marker='o', color='red')
    ax.grid(axis='y', lw=0.25)
    ax.set_title(f'Totals alerts in {months[-1]}: {monthly_alerts[-1] + sum([len(p) for p in opens])}; OPEN alerts: {sum([len(p) for p in opens])}')

    for i,j in enumerate(line_data[0]):
        ax.annotate(f'{round(j,1)}', xy=(i-0.1, j+1), xycoords='data', fontsize=9, color='darkgreen')
        
    for i,j in enumerate(line_data[1]):
        ax.annotate(f'{round(j,1)}', xy=(i-0.1, j-3), xycoords='data', fontsize=9, color='red')

    ax.legend(['Target achieved %', 'SL Hit %'], loc='upper left', facecolor='white', fancybox=True, framealpha=0.5)
    ax.set_xticklabels(labels = months, fontweight='bold')
    ax.set_ylabel('Target & SL Hit in %', fontsize=16)

    ax2 = ax.twinx()
    ax2.plot(months, monthly_alerts, marker='o')
    ax2.set_ylabel('No. of alerts', fontsize=14, rotation=-90, labelpad=13)
    ax2.legend(labels=['# of closed alerts'], loc='upper left', bbox_to_anchor=(0.004, 0.9), facecolor='white', fancybox=True, framealpha=0.5)

    for i,j in enumerate(monthly_alerts):
        ax2.annotate(j, xy=(i+0.1, j+1), xycoords='data', fontsize=9, color='blue')
    plt.savefig(f"report/data/plots/{df.iloc[0, 0]}/final.png")

on = []
for sheet in [dfcf, dfcn, dfno, dfrtp]:
    statistics(sheet)
    ons_ = TASL(sheet)
    on.append(ons_)
    bull_bear_plot(sheet, 'Bullish')
    if sheet.iloc[0,0]=='FO':
        bull_bear_plot(sheet, 'Bearish')
    final(sheet, ons_)
on = [p[0] for p in on]

# Combined results
df1 = pd.concat([dfcn, dfcf]).reset_index(drop=True)
df2 = pd.concat([dfno, dfrtp]).reset_index(drop=True)
df = pd.concat([df1, df2]).sort_values(by='Date', ascending=False)
df = df.reset_index(drop=True)
df.loc[:, 'What'] = 'Combined'

stats['Type']["Combined"]["total_alerts"] = sum([stats['Type'][x]['total_alerts'] for x in stats['Type']])
stats['Type']["Combined"]["avg_NoD"] = df[df['result dummy']=='Target achieved'].NoD.mean()
stats['Type']["Combined"]["total_stagnant"] = sum([stats['Type'][x]['total_stagnant'] for x in stats['Type']])
stats['Type']["Combined"]["total_bull"] = sum([stats['Type'][x]['total_bull'] for x in stats['Type']])
stats['Type']["Combined"]["total_bear"] = sum([stats['Type'][x]['total_bear'] for x in stats['Type']])
stats["to_date"] = dt.datetime.strftime(dt.date.today(), format="%d %b, %y")

ons_ = TASL(df) 
bull_bear_plot(df, 'Bullish')
bull_bear_plot(df, 'Bearish')
final(df, on)

with open('report/data/stats.json' ,'w') as file:
    json.dump(stats, file)