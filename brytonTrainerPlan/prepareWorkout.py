from datetime import timedelta
import pandas as pd
from WorkoutInjector import warmupFlag, activityFlag, recoveryFlag, coolDownFlag, col_duration, col_max_power, col_min_power, col_type, col_cadence

def prepare_workout_dict( filename) -> pd.DataFrame:
    data = pd.read_csv(filename)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    data.rename(columns=lambda x: x.lstrip(), inplace=True)
    data.loc[data['Type'] == 'Warm up', 'Type'] = warmupFlag
    data.loc[data['Type'] == 'Steady state', 'Type'] = activityFlag
    data.loc[data['Type'] == 'Free ride', 'Type'] = recoveryFlag
    data.loc[data['Type'] == 'Cool down', 'Type'] = coolDownFlag
    data['Duration'] = data['Duration'].apply(lambda x: str(timedelta(seconds=int(x))).zfill(8))

    data = data[['Type', 'Duration', 'Min Power (% FTP)', 'Max Power  (% FTP)', 'Cadence']]
    data.rename(columns={'Type': col_type}, inplace=True)
    data.rename(columns={'Duration': col_duration}, inplace=True)
    data.rename(columns={'Min Power (% FTP)': col_min_power}, inplace=True)
    data.rename(columns={'Max Power  (% FTP)': col_max_power}, inplace=True)
    data.rename(columns={'Cadence': col_cadence}, inplace=True)
    
    
    return data
    