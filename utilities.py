import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re

from PyQt5.QtWidgets import QMessageBox



def modify_database(df):
    if 'Cycle Time' not in df.columns:
        df['GENERAL_DATE'] = pd.to_datetime(df['GENERAL_DATE'], dayfirst=True)
        reference_time = df['GENERAL_DATE'].min()
        df['Cycle Time'] = ((df['GENERAL_DATE'] - reference_time).dt.total_seconds()//60 + 1)
    df["Cycle_change"] = df["segmentTypeName"] != df['segmentTypeName'].shift()
    df["Cycle_ID"] = df['Cycle_change'].cumsum()

    return df

def ramp_rates(type, data):
    df = data[data['segmentTypeName'] == type]
    cycles = df['Cycle_ID'].unique()
    final_slopes = []
    for j  in cycles:
        cycle = df[df['Cycle_ID']==j]
        tc_cols = cycle.filter(regex=r"^TC\d+")
        slopes = []
        for col in tc_cols:
            x = cycle['Cycle Time']
            y = cycle[col].values
            slope, _ = np.polyfit(x, y, 1)
            slopes.append(slope)
        final_slopes.append(round(np.mean(slope),2))
    return final_slopes

def ramp_rates_to_string(data):
    rates = ""
    for _,i in enumerate(data):
        rates += "Ramp Rate " + str(_+1) + ": " + str(i) + '\u00B0C/min\n'
    return rates

def avg_ramp_rate(data):
    av_slope = np.mean(data)
    print(av_slope)
    return str(av_slope) + '\u00B0C/min'

def dwell_time(data):
    df = data[data["segmentTypeName"] == 'Dwell']
    cycles = df['Cycle_ID'].unique()
    times = ""
    for _,i in enumerate(cycles):
        cycle = df[df['Cycle_ID']==i]
        times += 'Dwell Time ' + str(_+1) + ": " + str(cycle['Cycle Time'].max() - cycle['Cycle Time'].min() + 1) + ' min\n'
    return times

def tc_time(data):
    df = data[data['segmentTypeName'] != 'Dwell']
    cycles = df['Cycle_ID'].unique()
    tc_cols = [i for i in data.columns if re.search(r"TC\d+", i)]
    diffs = ""
    heating_count = 0
    cooling_count = 0
    for i in cycles:
        filter = df[df['Cycle_ID']==i]
        filter['max_difference'] = round(filter[tc_cols].max(axis=1) - filter[tc_cols].min(axis=1),2)
        cycle_type = filter.loc[filter["Cycle_ID"]==i, "segmentTypeName"].iloc[0]
        if cycle_type=='Heating':
            heating_count += 1
            count = heating_count
        if cycle_type=='Cooling':
            cooling_count += 1
            count = cooling_count
        diffs += str(cycle_type) + " "+ str(count) +": " + str(filter['max_difference'].max()) + '\u00B0C\n'
    return diffs



