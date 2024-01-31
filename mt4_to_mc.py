import pandas as pd
import numpy as np
import tkinter as tk
import tkinter.filedialog as filedialog
import json
import pandas_montecarlo

author = """
  /$$$$$$             /$$$$$$                        /$$     /$$          
 /$$$_  $$           /$$__  $$                      | $$    |__/          
| $$$$\ $$ /$$   /$$| $$  \__/ /$$   /$$  /$$$$$$  /$$$$$$   /$$  /$$$$$$$
| $$ $$ $$|  $$ /$$/| $$      | $$  | $$ /$$__  $$|_  $$_/  | $$ /$$_____/
| $$\ $$$$ \  $$$$/ | $$      | $$  | $$| $$  \__/  | $$    | $$|  $$$$$$ 
| $$ \ $$$  >$$  $$ | $$    $$| $$  | $$| $$        | $$ /$$| $$ \____  $$
|  $$$$$$/ /$$/\  $$|  $$$$$$/|  $$$$$$/| $$        |  $$$$/| $$ /$$$$$$$/
 \______/ |__/  \__/ \______/  \______/ |__/         \___/  |__/|_______/ 
                                                                                                                                  
"""

if __name__ == "__main__":
    # Load conf file
    with open("conf.json") as json_file:
        data = json.load(json_file)
    
    dd = data['dd']
    target = data['target']
    multiplier = data['multiplier']
    initial = data['initial']
    simLimit = data['simLimit']

    # Ask the user for the file to use
    root = tk.Tk()
    root.withdraw()
    fileName = filedialog.askopenfilename()
    # auto detect the delimiter and the number of rows to skip
    with open(fileName) as f:
        first_line = f.readline()
        if first_line.count(';') > first_line.count(','):
            delimiter = ';'
        else:
            delimiter = ','
        f.close()
    
    df = pd.read_csv(fileName, names=['balance', 'P/L'], delimiter=delimiter, skiprows=1, engine='python')

    # if balance is not a float convert it to float
    if df['balance'].dtype != float or df['balance'].dtype != np.float64:
        df['balance'] = df['balance'].str.replace(',', '.').str.replace(' ', '').astype(np.float64)
    
    df['pct_change'] = df.balance.pct_change()
    df['log_ret'] = np.log(df.balance) - np.log(df.balance.shift(1))
    
    # Generates the number of simulations based on the number of trades squared
    simCount = int((len(df.index)*len(df.index)) * multiplier)
    if simCount > simLimit:
        simCount = simLimit

    mc = df['log_ret'].montecarlo(sims=simCount, bust=dd, goal=target)

    # Returns percentage statistics on the simulations
    print("===============")
    print(mc.stats)
    print("Profit:", initial*(1+mc.stats['min']))
    print("Max Drawdown:", initial*(1+mc.stats['maxdd']))
    print("Under ", str(dd*100) ,"% drawdown:", mc.stats['bust'] * 100)
    print("Over ", str(target*100) ,"% target:", mc.stats['goal'] * 100)
    print("===============")

    # Plots the MonteCarlo Simulation
    mc.plot(title="Log Returns at " + str(simCount) + " Simulations")
