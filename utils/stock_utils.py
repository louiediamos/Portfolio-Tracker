import yfinance as yf
import pandas as pd
import streamlit as st

@st.cache_data(ttl=60, show_spinner=True) # cache for 5 minutes

def get_current_price(ticker: str):
    '''Fetch current stock price with herror handling'''
    if not ticker or pd.isna(ticker):
        print('Ticker not found')
    ticker = str(ticker).strip().upper()
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period='2d',
                            timeout=10
                            )
        if data.empty:
            data = yf.download(ticker, period='2d', progress=False, timeout=10)
        if data.empty or 'Close' not in data.columns:
            return 0.0
        last_close = data['Close'].iloc[-1]
        if isinstance(last_close, pd.Series):
            last_close = last_close.iloc[0] if not last_close.empty else 0.0            
        price = float(last_close)
        if price == 0.0:
            get_current_price.clear()
        return round(price, 4)       
    except Exception as e:
        st.error(f'Error fetching {ticker}: {str(e)}') # for debugging
        return 0.0
        
def get_historical_data(tickers: list, period='1mo'):
    '''Get historical data for performance chart'''
    try:
        data = yf.download(tickers, period=period, progress=False)['Close']
        return data
    except:
        return pd.DataFrame()

def calculate_portfolio_metrics(df: pd.DataFrame):
    '''Calculate all portfolio metrics'''
    if df.empty:
        return df.copy()
    df = df.copy()
    df['Current_Price'] = df['Ticker'].apply(get_current_price)

    # Warning if failed
    failed = df['Current_Price'] == 0
    if failed.sum() > 0:
        st.warning(f'☢️ Could not fetch price for {failed.sum()} ticker(s)')    
    
    # Get prices
    df['Current_Value'] = df['Shares'] * df['Current_Price']
    df['Cost_Basis'] = df['Shares'] * df['Avg_Buy_Price']
    df['Gain_Loss'] = df['Current_Value'] - df['Cost_Basis']
    df['Gain_Loss_%'] = (df['Gain_Loss'] / df['Cost_Basis'] * 100).round(2)

    return df