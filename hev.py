from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine
from tqdm import tqdm
import pandas as pd
import numpy as np
import warnings
import os


def createEngine():
    load_dotenv()
    USER = os.getenv('USER')
    PSWD = os.getenv('PSWD')
    HOST = os.getenv('HOST')
    PORT = os.getenv('PORT')
    NAME = os.getenv('NAME')
    return create_engine(f'postgresql://{USER}:{PSWD}@{HOST}:{PORT}/{NAME}')


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

    # initialize progress bar
    pbar = tqdm(total=100, position=0, desc="Overall")

    # make directory to house leaderboards
    if not os.path.exists('data'):
        os.mkdir('data')

    # get player id data and read into a pandas dataframe
    url = "https://raw.githubusercontent.com/chadwickbureau/register/master/data/people.csv"
    lookup = pd.read_csv(url, index_col="key_mlbam")
    lookup['name'] = lookup['name_first'] + ' ' + lookup['name_last']
    pbar.update(25)

    # select necessary columns from database only
    columns = [
        'game_year',
        'batter',
        'launch_speed',
        'launch_angle',
        'woba_denom',
        'bb_type'
    ]

    # get savant data from postgres and read into pandas dataframe
    engine = createEngine()
    df = pd.read_sql('baseball_savant', engine, columns=columns)
    df['game_year'] = df['game_year'].astype(int)
    df['batter'] = df['batter'].astype(int)
    df['launch_speed'] = df['launch_speed'].astype(float)
    df['launch_angle'] = df['launch_angle'].astype(float)
    pbar.update(25)

    # clean up data and calculate hEV
    df = df[['batter', 'game_year', 'launch_speed', 'launch_angle', 'woba_denom', 'bb_type']].fillna(0)
    df['woba_denom'] = df['woba_denom'].astype(float)
    df['hEV'] = np.where(df['bb_type'] != 0, df['launch_speed'] * np.cos(np.radians(df['launch_angle'] - 25)), 0)
    df['BBE'] = np.where(df['bb_type'] != 0, 1, 0)
    pbar.update(25)

    # create .xlsx file
    with pd.ExcelWriter('data/hEV_leaderboards.xlsx') as writer:
        for year in tqdm(range(df['game_year'].min(), df['game_year'].max()+1), position=1, desc="Leaderboards"):
            # filter df by season
            df_year = df[df['game_year'] == year]

            # groupby batters and get average hEV
            df_year = df_year.groupby('batter').agg({'hEV': 'sum', 'BBE': 'sum', 'woba_denom': 'sum'})
            df_year.rename(columns={'woba_denom': 'PA'}, inplace=True)
            df_year['hEV/PA'] = df_year['hEV'] / df_year['PA']
            df_year['hEV/BBE'] = df_year['hEV'] / df_year['BBE']
            df_year.index = df_year.index.map(name)
            df_year[['BBE', 'PA', 'hEV/BBE', 'hEV/PA']].dropna().sort_values(by=['hEV/PA'], ascending=False).to_excel(writer, sheet_name=str(year))
    pbar.update(25)
