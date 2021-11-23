import streamlit as st
import yfinance as yf
from yahoofinancials import YahooFinancials
import numpy as np
import pandas as pd
from pandas_datareader import data
import matplotlib.pyplot as plt
import seaborn as sb
import datetime as dt
import yahoo_fin.stock_info as si
from dateutil.relativedelta import relativedelta


class Company:
    def __init__(self, ticker):
        one_year_before = dt.datetime.date(dt.datetime.today() - relativedelta(months=+12))
        end_date_Target = dt.datetime.date(dt.datetime.today())
        price_df = si.get_data(ticker, start_date = one_year_before, end_date = end_date_Target, interval = "1wk")
        overview_df = si.get_stats(ticker)
        overview_df = overview_df.set_index('Attribute')
        overview_dict = si.get_quote_table(ticker)
        income_statement = si.get_income_statement(ticker)
        balance_sheet = si.get_balance_sheet(ticker)
        cash_flows = si.get_cash_flow(ticker)

        self.year_end = overview_df.loc['Fiscal Year Ends'][0]
        #self.market_cap = get_integer(overview_dict['Market Cap'])
        self.market_cap = str_to_num(overview_dict['Market Cap'])
        self.market_cap_cs = '{:,d}'.format(int(self.market_cap))
        self.prices = price_df['adjclose']

        self.ev = income_statement.loc['netIncomeFromContinuingOps'][0]
        self.ev_cs = income_statement.loc['netIncomeApplicableToCommonShares'][0]
        self.sales = income_statement.loc['totalRevenue'][0]
        self.gross_profit = income_statement.loc['grossProfit'][0]
        self.ebit = income_statement.loc['ebit'][0]
        self.interest = - income_statement.loc['interestExpense'][0]
        self.net_profit = income_statement.loc['netIncome'][0]

    def get_overview(self):
        self.price_earnings_ratio = self.market_cap/self.net_profit
        self.ev_sales_ratio = self.ev/self.sales
        self.overview_dict = {'Values' : [self.ev_cs, self.market_cap_cs, self.ev_sales_ratio, self.price_earnings_ratio]}

    def get_profit_margins(self):
        self.gross_margin = self.gross_profit/self.sales
        self.operating_margin = self.ebit/self.sales
        self.net_margin = self.net_profit/self.sales
        self.profit_margin_dict = {'Values' : [self.gross_margin, self.operating_margin, self.net_margin]}


num_replace = {
    'B' : 'e9',
    'M' : 'e6',
    'T' : 'e3',
}


def str_to_num(s):
    if s[-1] in num_replace:
        s = s[:-1]+num_replace[s[-1]]
    return int(float(s))

st.title('Financial Dashboard')
ticker_input = st.text_input('Please enter your company ticker:')
search_button = st.button('Search')

if search_button:
    company = Company(ticker_input)
    company.get_overview()
    company.get_profit_margins()
    #company.get_liquidity_ratios()
    #company.get_leverage_ratios()
    #company.get_efficiency_ratios()

    st.header('Company overview')
    overview_index = ['Enterprise value', 'Market cap', 'EV/sales ratio', 'P/E ratio']
    overview_df = pd.DataFrame(company.overview_dict, index = overview_index)
    st.line_chart(company.prices)
    st.table(overview_df)

    with st.beta_expander('Profit margins (as of {})'.format(company.year_end)):
        profit_margin_index = ['Gross margin', 'Operating margin', 'Net margin']
        profit_margin_df = pd.DataFrame(company.profit_margin_dict, index = profit_margin_index)
        st.table(profit_margin_df)
        st.bar_chart(profit_margin_df)