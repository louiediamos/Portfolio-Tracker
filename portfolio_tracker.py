import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime
from utils.stock_utils import get_current_price, calculate_portfolio_metrics
from utils.stock_utils import get_historical_data

# Page configuration
st.set_page_config(page_title='PortTracker', layout='centered', page_icon='💼')
st.title('💼 Portfolio Tracker')

# Data file
DATA_FILE = 'data/portfolio.csv'

# Load portfolio data
if 'portfolio' not in st.session_state:
      st.session_state.portfolio = pd.DataFrame(
            columns=['Ticker', 'Shares', 'Avg_Buy_Price', 'Date_Added']
      )

portfolio = st.session_state.portfolio

# Sidebar
st.sidebar.header('Add New Stock')

with st.sidebar.form('add_stock_form'):
    col1, col2 = st.columns(2)
    with col1:
        ticker = st.text_input('Ticker',
                                placeholder='(input ticker)').upper().strip()
    with col2:
        shares = st.number_input('Shares', min_value=0.10, value=10.00, step=0.10)
    
    avg_buy_price = st.number_input('Avg Buy Price ($)', min_value=0.10, 
                                    value=150.00,step=0.10)
        
    if st.form_submit_button("➕ Add to Portfolio"):
        if not ticker:
            st.error('Please enter a Ticker Symbol')
            # Check for duplicate        
        elif not portfolio.empty and ticker in portfolio['Ticker'].values:
            st.warning(f'{ticker} already exixts in your portfolio. Please use ✏️ Edit button.')
        else:
            # Create a new row and add it
            new_row = pd.DataFrame({
                'Ticker': [ticker],
                'Shares': [shares],
                'Avg_Buy_Price': [avg_buy_price],
                'Date_Added': [datetime.now().strftime('%Y-%m-%d')]
            })
            st.session_state.portfolio = pd.concat([st.session_state.portfolio,
                                                    new_row], ignore_index=True)
            st.success(f'Success! ✅ {ticker} has been added.')
            st.rerun()
        
# ====== Main Content =======

if not portfolio.empty:
    # Calculate all metrics
    portfolio = calculate_portfolio_metrics(portfolio)

    # Summary Metrics
    total_value = portfolio['Current_Value'].sum()
    total_cost = portfolio['Cost_Basis'].sum()
    total_gain = total_value - total_cost
    total_gain_pct = (total_value-total_cost/ total_cost* 100) if total_cost> 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric('Total Value', f'${total_value:.2f}')
    col2.metric('Total Gain/Loss', f'${total_gain:.2f}')
    col3.metric('Holdings', len(portfolio))
    col4.metric('Cash', '$0.00')

    # Portfolio Table
    st.subheader('Portfolio Holdings')
    display_df = portfolio[['Ticker', 'Shares', 'Avg_Buy_Price', 'Current_Price',
                            'Current_Value', 'Gain_Loss', 'Gain_Loss_%']].round(2)

    st.dataframe(
        display_df.style.format({
            'Shares': '{:.2f}',
            'Avg_Buy_Price': '${:.2f}',
            'Current_Price': '${:.2f}',
            'Current_Value': '${:.2f}',
            'Gain_Loss': '${:.2f}',
            'Gain_Loss_%': '{:.2f}%'
        },
        na_rep='-',
        subset=['Shares', 'Avg_Buy_Price', 'Current_Price', 'Current_Value',
                'Gain_Loss', 'Gain_Loss_%']
        ).map(
              lambda v: 'color: green' if v > 0 else 'color: red',
              subset=['Gain_Loss', 'Gain_Loss_%']
        ),
        hide_index=True)

    # Charts
    tab1, tab2 = st.tabs(['Allocation', 'Performance'])

    with tab1:
        fig_pie = px.pie(portfolio, values='Current_Value', names='Ticker',
                         title='Portfolio Allocation')
        st.plotly_chart(fig_pie, width="stretch")
    
    with tab2:
        st.subheader('30-Day Portfolio Performance')
        tickers = portfolio['Ticker'].tolist()
        hist_data = get_historical_data(tickers, period ='1mo')
        if not hist_data.empty:
            fig_hist = px.line(hist_data, title='Historical Price Movement (last 30 Days)')
            st.plotly_chart(fig_hist, width="stretch")
else:
    st.info('👋 Your Portfolio is empty. Add some holdings using the sidebar!')

# ====== Manage Holdings =======
if not portfolio.empty:
    st.subheader('Manage Holdings')
    ticker_list = st.session_state.portfolio['Ticker'].unique()
    selected_ticker = st.selectbox('Select Ticker', ticker_list)

    col1, col2 = st.columns(2)
    with col1:
        if st.button('🗑️ Delete', type='primary'):
            st.session_state.portfolio = portfolio[portfolio['Ticker']!=selected_ticker].reset_index(drop=True)
            st.success(f'Deleted {selected_ticker}')
            st.rerun()

    with col2:
        if st.button('✏️ Edit'):
            row = portfolio[portfolio['Ticker'] == selected_ticker].iloc[0]
            new_shares = st.number_input('Shares', value=float(row['Shares']))
            new_price = st.number_input('Avg Buy Price', value=float(row['Avg_Buy_Price']))

            if st.button('Save Changes'):
                portfolio.loc[portfolio['Ticker'] == selected_ticker, 'Shares'] = new_shares
                portfolio.loc[portfolio['Ticker'] == selected_ticker, 'Avg_Buy_Price'] = new_price
                portfolio.to_csv(DATA_FILE, index=False)
                st.success('Updated successfull!')
                st.rerun()

# Export
if not portfolio.empty and st.button('🗂️ Export to CSV'):
                                     portfolio.to_csv('portfolio_export.csv', index=False)
                                     st.success('Exported Successfully!')