import os
import warnings

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from tqdm import tqdm


def createEngine():
    '''creates database connection'''
    load_dotenv()
    USER = os.getenv('USER')
    PSWD = os.getenv('PSWD')
    HOST = os.getenv('HOST')
    PORT = os.getenv('PORT')
    NAME = os.getenv('NAME')
    return create_engine(f'postgresql://{USER}:{PSWD}@{HOST}:{PORT}/{NAME}')


def name(mlbam):
    '''map mlb ids to name'''
    try:
        return lookup.loc[mlbam]['name']
    except:
        return mlbam


if __name__ == '__main__':
    warnings.filterwarnings('ignore')

    # initialize progress bar
    pbar = tqdm(total=19, position=0, desc="Overall")

    # make directory to house leaderboards
    if not os.path.exists('data'):
        os.mkdir('data')

    # get player id data
    lookup = []
    for key in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']:
        url = f"https://raw.githubusercontent.com/chadwickbureau/register/master/data/people-{key}.csv"
        lookup.append(pd.read_csv(url, index_col="key_mlbam"))
        pbar.update(1)
    lookup = pd.concat(lookup)
    lookup['name'] = lookup['name_first'] + ' ' + lookup['name_last']

    # select necessary columns from database only
    columns = [
        'game_year',
        'batter',
        'launch_speed',
        'launch_angle',
        'woba_denom',
        'bb_type'
    ]

    # get savant data from postgres
    engine = createEngine()
    df     = pd.read_sql('baseball_savant', engine, columns=columns)
    pbar.update(1)

    # clean up data and calculate hEV
    df = df[['batter', 'game_year', 'launch_speed', 'launch_angle', 'woba_denom', 'bb_type']].fillna(0)
    df['hEV'] = np.where(df['bb_type'] != 0, df['launch_speed'] * np.cos(np.radians(df['launch_angle'] - 25)), 0)
    df['BBE'] = np.where(df['bb_type'] != 0, 1, 0)
    pbar.update(1)

    # create .xlsx file
    with pd.ExcelWriter('data/hEV_leaderboards.xlsx') as writer:
        for year in tqdm(range(df['game_year'].min(), df['game_year'].max()+1), position=1, desc="Leaderboards"):
            # filter df by season
            df_year = df[df['game_year'] == year]

            # groupby batters and get average hEV
            df_year = df_year.groupby('batter').agg({'hEV': 'sum', 'BBE': 'sum', 'woba_denom': 'sum'})
            df_year.rename(columns={'woba_denom': 'PA'}, inplace=True)
            df_year['hEV/PA']  = df_year['hEV'] / df_year['PA']
            df_year['hEV/BBE'] = df_year['hEV'] / df_year['BBE']
            df_year.index      = df_year.index.map(name)
            df_year[['BBE', 'PA', 'hEV/BBE', 'hEV/PA']].dropna().sort_values(by=['hEV/PA'], ascending=False).to_excel(writer, sheet_name=str(year))
    pbar.update(1)
