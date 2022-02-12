import datetime

import pandas as pd
import numpy  as np

from pprint         import PrettyPrinter, pprint
from ..util.enums   import *
from ..util.globals import G


class AlphaQuerySpider():
    def __init__(self) -> None:
        self.reported_stocks    = dict()
        self.unreported_stocks = dict()
        self.all_stocks = dict()
        return

    def __add_to_all_stocks(self, symbol, entry_date) -> None:
        entry_date_str = entry_date[0] + '-' + entry_date[1] + '-' + entry_date[2]
        
        if symbol in self.all_stocks:
            self.all_stocks[symbol].append(entry_date_str)
        else:
            self.all_stocks[symbol] = [entry_date_str]
        return

    def __add_to_reported_stocks(self, symbol, earnings_date) -> None:
        if symbol in self.reported_stocks.keys():
            self.reported_stocks[symbol].append(earnings_date.strftime("%m-%d-%Y"))
        else:
            self.reported_stocks[symbol] = [earnings_date.strftime("%m-%d-%Y")]        
        return

    def __add_to_unreported_stocks(self, symbol, entry_date) -> None:
        entry_date_str = entry_date[0] + '-' + entry_date[1] + '-' + entry_date[2]
        
        if symbol in self.unreported_stocks:
            self.unreported_stocks[symbol].append(entry_date_str)
        else:
            self.unreported_stocks[symbol] = [entry_date_str]
        return


    def scrape_data(self) -> None:
        stock_df    = pd.read_excel(STOCK_LIST, usecols=['Date', 'Symbol', 'Price'])
        symbol_list = stock_df['Symbol'].to_list()
        stock_count = 1
        reported = False

        for row in stock_df.iterrows():
            entry_date   = row[1]['Date']
            symbol       = row[1]['Symbol']
            entry_price  = row[1]['Price']

            G.log.print_and_log(f"Fetching data for {symbol} {entry_date} {stock_count} / {len(symbol_list)}")
            
            url = ALPHA_QUERY_URL + symbol + '/' + 'earnings-history'

            try:
                earnings_df = pd.read_html(url)[0]
                entry_date  = entry_date.split('/')
                end_date    = datetime.datetime(year=int(entry_date[2]), month=int(entry_date[0]), day=int(entry_date[1]))
                start_date  = end_date - datetime.timedelta(days=7)

                self.__add_to_all_stocks(symbol, entry_date)

                for _row in earnings_df.iterrows():
                    try:
                        f_quarter_end = [int(i) for i in _row[1]['Fiscal Quarter End'].split('-')]
                        earnings_date = datetime.datetime(year=f_quarter_end[0], month=f_quarter_end[1], day=f_quarter_end[2])
                        
                        # is there an earnings day that falls between start_date and end_date?
                        if earnings_date < end_date and earnings_date >= start_date:
                            # did the price go up on or after the earnings date?
                            # if the stock reported on any of those 5 business days including the previous monday, excluding the entry day
                            # check for a weekly pattern, not daily pattern
                            # divide up the two dictionaries, reported and non-reported
                            # spreadsheet, one with reported and one non-reported
                            
                            self.__add_to_reported_stocks(symbol, earnings_date)
                            reported = True
                            break
                    except Exception as e:
                        G.log.print_and_log(e=e, filename=__file__)

                if not reported:
                    self.__add_to_unreported_stocks(symbol, entry_date)

            except Exception as e:
                G.log.print_and_log(e=e, filename=__file__)

            stock_count += 1

        reported_stock_str = PrettyPrinter(indent=1).pformat({symbol: earnings_date for (symbol, earnings_date) in self.reported_stocks.items()})
        G.log.print_and_log(f"{reported_stock_str}")

        reported_s = pd.Series(self.reported_stocks)
        unreported = pd.Series(self.unreported_stocks)

        reported_s.to_excel("Trade_Result_Reported.xlsx", sheet_name="Reported Stocks")
        unreported.to_excel("Trade_Result_Unreported.xlsx", sheet_name="Unreported Stocks")
        return



"""
    {'ALLE': ['12-31-2020'],
    'APTV': ['09-30-2020'],
    'ATVI': ['09-30-2019'],
    'BDX': ['06-30-2018', '09-30-2018', '03-31-2019'],
    'BIO': ['03-31-2019'],
    'CLX': ['06-30-2020'],
    'COST': ['11-30-2019'],
    'CTSH': ['03-31-2018'],
    'DD': ['12-31-2017'],
    'DIS': ['06-30-2019'],
    'DLR': ['09-30-2017'],
    'DXCM': ['03-31-2017'],
    'EL': ['09-30-2017', '09-30-2021'],
    'EMN': ['03-31-2017'],
    'EPAM': ['06-30-2018'],
    'EQR': ['12-31-2021'],
    'FB': ['09-30-2017'],
    'FLT': ['03-31-2017'],
    'FRT': ['12-31-2021'],
    'HES': ['12-31-2017'],
    'IT': ['06-30-2021'],
    'J': ['09-30-2019'],
    'JKHY': ['06-30-2017', '09-30-2021'],
    'LIN': ['12-31-2021'],
    'LOW': ['04-30-2019'],
    'MLM': ['12-31-2020'],
    'MSCI': ['06-30-2020'],
    'NDAQ': ['09-30-2021'],
    'NUE': ['12-31-2021', '12-31-2021'],
    'PEP': ['09-30-2019'],
    'PKI': ['09-30-2020'],
    'REG': ['12-31-2021'],
    'ROK': ['06-30-2017'],
    'ROP': ['06-30-2021'],
    'SEE': ['06-30-2020'],
    'SNPS': ['07-31-2019'],
    'SPGI': ['03-31-2018'],
    'TDG': ['06-30-2018'],
    'TMO': ['09-30-2019'],
    'TSN': ['12-31-2021'],
    'TT': ['12-31-2020'],
    'VRSK': ['09-30-2019'],
    'WST': ['09-30-2019'],
    'XOM': ['06-30-2021']}

"""        