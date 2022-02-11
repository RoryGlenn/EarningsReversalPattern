import datetime

import pandas as pd

from pprint         import pprint
from ..util.enums   import *
from ..util.globals import G



class AlphaQuerySpider():
    def __init__(self) -> None:
        return

    def scrape_data(self) -> None:

        stock_df             = pd.read_excel(STOCK_LIST, usecols=['Date', 'Symbol', 'Price'])
        symbol_list          = stock_df['Symbol'].to_list()
        reported_stocks      = dict()
        reported_stock_count = 0
        stock_count          = 1

        for row in stock_df.iterrows():
            entry_date   = row[1]['Date']
            symbol       = row[1]['Symbol']
            entry_price  = row[1]['Price']

            G.log.print_and_log(f"Fetching data for {symbol} {entry_date} {stock_count} / {len(symbol_list)}")
            
            url = ALPHA_QUERY_URL + symbol + '/' + 'earnings-history'
            # time.sleep(0.25)

            try:
                earnings_df = pd.read_html(url)[0]
                entry_date  = entry_date.split('/')
                end_date    = datetime.datetime(year=int(entry_date[2]), month=int(entry_date[0]), day=int(entry_date[1]))
                start_date  = end_date - datetime.timedelta(days=7)
                
                for _row in earnings_df.iterrows():
                    f_quarter_end = _row[1]['Fiscal Quarter End'].split('-')
                    f_quarter_end = [int(i) for i in f_quarter_end]
                    earnings_date = datetime.datetime(year=f_quarter_end[0], month=f_quarter_end[1], day=f_quarter_end[2])
                    
                    # is there an earnings day that falls between start_date and end_date?
                    if earnings_date <= end_date and earnings_date >= start_date:
                        # did the price go up on or after the earnings date?
                        if symbol in reported_stocks.keys():
                            reported_stocks[symbol].append(earnings_date)
                        else:
                            reported_stocks[symbol] = [earnings_date]
                        
                        reported_stock_count += 1
                        print("reported_stock_count:", reported_stock_count)
                        break
            except Exception as e:
                G.log.print_and_log(e=e, filename=__file__)
      
            stock_count += 1

        pprint({symbol: earnings_date for (symbol, earnings_date) in reported_stocks.items()})
        return



"""
DXCM [datetime.datetime(2017, 3, 31, 0, 0)]
FLT [datetime.datetime(2017, 3, 31, 0, 0)]
EMN [datetime.datetime(2017, 3, 31, 0, 0)]
JKHY [datetime.datetime(2017, 6, 30, 0, 0), datetime.datetime(2021, 9, 30, 0, 0)]
ROK [datetime.datetime(2017, 6, 30, 0, 0)]
HD [datetime.datetime(2017, 7, 31, 0, 0)]
DLR [datetime.datetime(2017, 9, 30, 0, 0)]
EL [datetime.datetime(2017, 9, 30, 0, 0), datetime.datetime(2021, 9, 30, 0, 0)]
FB [datetime.datetime(2017, 9, 30, 0, 0)]
DD [datetime.datetime(2017, 12, 31, 0, 0)]
HES [datetime.datetime(2017, 12, 31, 0, 0)]
CTSH [datetime.datetime(2018, 3, 31, 0, 0)]
SPGI [datetime.datetime(2018, 3, 31, 0, 0)]
BDX [datetime.datetime(2018, 6, 30, 0, 0), datetime.datetime(2018, 9, 30, 0, 0), datetime.datetime(2019, 3, 31, 0, 0)]
EPAM [datetime.datetime(2018, 6, 30, 0, 0)]
TDG [datetime.datetime(2018, 6, 30, 0, 0)]
LOW [datetime.datetime(2019, 4, 30, 0, 0)]
BIO [datetime.datetime(2019, 3, 31, 0, 0)]
DIS [datetime.datetime(2019, 6, 30, 0, 0)]
SNPS [datetime.datetime(2019, 7, 31, 0, 0)]
WST [datetime.datetime(2019, 9, 30, 0, 0)]
COST [datetime.datetime(2019, 11, 30, 0, 0)]
J [datetime.datetime(2019, 9, 30, 0, 0)]
TSLA [datetime.datetime(2019, 9, 30, 0, 0)]
ATVI [datetime.datetime(2019, 9, 30, 0, 0)]
PEP [datetime.datetime(2019, 9, 30, 0, 0)]
TMO [datetime.datetime(2019, 9, 30, 0, 0)]
VRSK [datetime.datetime(2019, 9, 30, 0, 0)]
CLX [datetime.datetime(2020, 6, 30, 0, 0)]
MSCI [datetime.datetime(2020, 6, 30, 0, 0)]
GNRC [datetime.datetime(2020, 6, 30, 0, 0)]
SEE [datetime.datetime(2020, 6, 30, 0, 0)]
PKI [datetime.datetime(2020, 9, 30, 0, 0)]
APTV [datetime.datetime(2020, 9, 30, 0, 0)]
ALLE [datetime.datetime(2020, 12, 31, 0, 0)]
MLM [datetime.datetime(2020, 12, 31, 0, 0)]
TT [datetime.datetime(2020, 12, 31, 0, 0)]
NDAQ [datetime.datetime(2021, 9, 30, 0, 0)]
XOM [datetime.datetime(2021, 6, 30, 0, 0)]
ROP [datetime.datetime(2021, 6, 30, 0, 0)]
IT [datetime.datetime(2021, 6, 30, 0, 0)]
MMC [datetime.datetime(2021, 9, 30, 0, 0)]
PAYX [datetime.datetime(2021, 11, 30, 0, 0)]
EQR [datetime.datetime(2021, 12, 31, 0, 0)]
FRT [datetime.datetime(2021, 12, 31, 0, 0)]
LIN [datetime.datetime(2021, 12, 31, 0, 0)]
REG [datetime.datetime(2021, 12, 31, 0, 0)]
TSN [datetime.datetime(2021, 12, 31, 0, 0)]
NUE [datetime.datetime(2021, 12, 31, 0, 0), datetime.datetime(2021, 12, 31, 0, 0)]"""        