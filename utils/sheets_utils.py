import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

SCOPES = ["https://spreadsheets.google.com/feeds",
                    "https://www.googleapis.com/auth/drive"]

def get_google_sheet(sheet_name='Portfolio Tracker', key_path=None, creds_dict=None):
    '''Connect to Google Sheet'''
    if creds_dict:
        credentials = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    elif key_path:
        credentials = Credentials.from_service_account_file(key_path, scopes=SCOPES)
    else:
        raise ValueError('Either key_path or creds_dict must be provided')
    
    client = gspread.authorize(creds)

    try: 
        sheet = client.open(sheet_name).worksheet('PortTracker')
    except: 
        sheet.append_row(['Ticker', 'Shares', 'Avg_Buy_Price', 'Date_Added'])
    
    return sheet

def load_from_sheet(sheet):
    '''Load data from Google Sheet to DataFrame'''
    try: 
        data = sheet.get_all_records()
        port_df = pd.DataFrame(data)
        if port_df.empty:
            return pd.DataFrame(columns=['Ticker', 'Shares', 'Avg_Buy_Price', 'Date_Added'])
        return port_df
    except Exception as e:
        print(f'Error loading sheet: {e}')
        return pd.DataFrame(columns=['Ticker', 'Shares', 'Avg_Buy_Price', 'Date_Added'])
    
def save_to_sheet(sheet, port_df):
    '''Save DataFrame to Google Sheet'''
    sheet.clear()
    # Add Headers
    sheet.append_row(['Ticker', 'Shares', 'Avg_Buy_Price', 'Date_Added'])
    # Add data
    for _ , row in port_df.iterrows():
        sheet.append_row([
            row['Ticker'],
            float(row['Shares']),
            float(row['Avg_Buy_Price']),
            row['Date_Added']
        ])