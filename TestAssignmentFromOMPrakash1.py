import pandas as pd
import json
import os


def read_csv(filename):
    """Read CSV file for DataFrame."""
    df = pd.read_csv(filename, delimiter=';')
    return df


def read_json(filename):
    """Read JSON file for DataFrame."""
    df = pd.read_json(filename, lines=True)
    return df


def create_directory(dir_name):
    """Create directory if it does not exist."""
    try:
        os.mkdir(dir_name)
        print(f"Folder '{dir_name}' created.")
    except FileExistsError:
        print(f"Folder '{dir_name}' already exists.")


def update_player_type_column(df):
    """Modify  Player-Type column based on runs and wickets columns"""
    rows, columns = df.shape
    df = df.reset_index()

    for row in range(rows):
        if df.loc[row, 'runs'] > 500 and df.loc[row, 'wickets'] > 50:
            df.loc[row, 'Player Type'] = 'All-Rounder'
        elif df.loc[row, 'runs'] > 500 and df.loc[row, 'wickets'] < 50:
            df.loc[row, 'Player Type'] = 'Batsman'
        elif df.loc[row, 'runs'] < 500:
            df.loc[row, 'Player Type'] = 'Bowler'

    df = df.dropna()
    df['Result'] = "None"
    return df


def update_result_column(df, test_dataset_filepath, odi_dataset_filepath):
    """Modify the result column based on playertype match with other dataset."""
    df_odi_output = pd.read_csv(odi_dataset_filepath, delimiter=';')
    df_odi_output = df_odi_output.set_index('playerName')

    df_test_output = pd.read_csv(test_dataset_filepath, delimiter=';')
    df_test_output = df_test_output.set_index('playerName')

    odi_df = df[df['eventType'] == 'ODI'].copy()
    test_df = df[df['eventType'] == 'TEST'].copy()

    odi_df = odi_df.set_index('playerName')
    test_df = test_df.set_index('playerName')

    # Update result for odi dataframe
    for name in odi_df.index.tolist():
        for odi_name in df_odi_output.index.tolist():
            if name == odi_name:
                if odi_df.loc[name, 'Player Type'] == df_odi_output.loc[name, 'playerType']:
                    odi_df.loc[name, 'Result'] = 'PASS'
                else:
                    odi_df.loc[name, 'Result'] = 'FAIL'

    # Update 'Result' for test dataframe
    for name in test_df.index.tolist():
        for test_name in df_test_output.index.tolist():
            if name == test_name:
                if test_df.loc[name, 'Player Type'] == df_test_output.loc[name, 'playerType']:
                    test_df.loc[name, 'Result'] = 'PASS'
                else:
                    test_df.loc[name, 'Result'] = 'FAIL'

    # Concatenate ODI and TEST dataframe
    final_df = pd.concat([odi_df, test_df])
    final_df = final_df[final_df['Result'] != "None"]
    final_df.to_csv("test_result.csv")


# Read .csv files
df_csv = read_csv('assignmentinputDataSettestDataSet1.csv')
df_json = read_json('assignmentinputDataSettestDataSet2.json')

df_final = pd.concat([df_csv, df_json])

create_directory('temp')
df_final.to_csv('temp/FinalDataFrame.csv', index=False)

df_final['Player Type'] = "None"
df_updated = update_player_type_column(df_final)
df_updated.to_csv('PlayertypeUpdated.csv')

update_result_column(df_updated, 'assignmentoutputDataSettest.csv', 'assignmentoutputDataSetodi.csv')
