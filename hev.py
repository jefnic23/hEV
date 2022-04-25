from datetime import datetime
from tqdm import tqdm
import pandas as pd
import numpy as np
import warnings
import os


def name(mlbam):
    '''
    map mlb ids to name
    '''
    try:
        return lookup.loc[mlbam]['name']
    except:
        return mlbam


if __name__ == '__main__':
    warnings.filterwarnings('ignore')

    while True:
        year = input("Enter a year from 2015 to present: ")
        try:
            year = int(year)
        except ValueError:
            print('Not a valid year')
            continue
        if 2015 <= year <= datetime.now().year:
            break
        else:
            print('Not a valid year')

    # initialize progress bar
    pbar = tqdm(total=100)

    while True:
        # get player id data and read into a pandas dataframe
        url = "https://raw.githubusercontent.com/chadwickbureau/register/master/data/people.csv"
        lookup = pd.read_csv(url, index_col="key_mlbam")
        lookup['name'] = lookup['name_first'] + ' ' + lookup['name_last']
        pbar.update(20)

        # locate savant data and read into pandas dataframe
        dir = os.path.abspath(f'../baseball_savant/data/savant_{year}.csv')
        df = pd.read_csv(dir)
        pbar.update(20)

        # clean up data and calculate hEV
        df = df[['batter', 'launch_speed', 'launch_angle']].dropna()
        df['hEV'] = df['launch_speed'] * np.cos(np.radians(df['launch_angle'] - 25))
        pbar.update(20)

        # groupby batters and get average hEV
        df = df.groupby('batter').agg({'hEV': 'mean'})
        df.index = df.index.map(name)
        pbar.update(20)

        # make directory to house savant data
        if not os.path.exists('data'):
            os.mkdir('data')

        df.to_csv(f"data/hEV_{year}.csv")
        pbar.update(20)

        break
    