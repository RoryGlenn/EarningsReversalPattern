import datetime

import pandas as pd

from ..util.enums   import *
from ..util.globals import G


class AlphaQuerySpider():
    def __init__(self) -> None:
        self.reported_stocks     = dict()
        self.unreported_stocks   = dict()
        return

    def __add_to_reported_stocks(self, symbol, entry_date: datetime.datetime) -> None:
        if symbol in self.reported_stocks.keys():
            self.reported_stocks[symbol].append(entry_date.strftime("%m-%d-%Y"))
        else:
            self.reported_stocks[symbol] = [entry_date.strftime("%m-%d-%Y")]
        return

    def __add_to_unreported_stocks(self, symbol, entry_date: list) -> None:
        entry_date_str = entry_date[0] + '-' + entry_date[1] + '-' + entry_date[2]
        
        if symbol in self.unreported_stocks:
            self.unreported_stocks[symbol].append(entry_date_str)
        else:
            self.unreported_stocks[symbol] = [entry_date_str]
        return
    
    def __write_to_excel(self) -> None:
        reported_s   = pd.Series(self.reported_stocks)
        unreported_s = pd.Series(self.unreported_stocks)

        G.log.print_and_log(f"Reported stocks\n{reported_s}")
        G.log.print_and_log(f"Unreported stocks\n{unreported_s}")

        with pd.ExcelWriter('Trade_Result.xlsx', engine='xlsxwriter') as writer:
            reported_s.to_excel(writer, sheet_name="Reported_Stocks")
            unreported_s.to_excel(writer, sheet_name="Unreported_Stocks")   
        return

    def __get_earnings_date(self, _row: tuple) -> datetime.datetime:
        f_quarter_end = [int(i) for i in _row[1]['Fiscal Quarter End'].split('-')]
        earnings_date = datetime.datetime(year=f_quarter_end[0], month=f_quarter_end[1], day=f_quarter_end[2])
        return earnings_date

    def scrape_data(self) -> None:
        stock_df    = pd.read_excel(STOCK_LIST, usecols=['Date', 'Symbol'])
        stock_df = stock_df[::-1] # reverse the data

        symbol_list = stock_df['Symbol'].to_list()
        stock_count = 1
        reported    = False

        for row in stock_df.iterrows():
            entry_date   = row[1]['Date']
            symbol       = row[1]['Symbol']

            G.log.print_and_log(f"Fetching data for {symbol} {entry_date} {stock_count} / {len(symbol_list)}")
            
            url = ALPHA_QUERY_URL + symbol + '/' + 'earnings-history'

            try:
                earnings_df = pd.read_html(url)[0]
                entry_date  = entry_date.split('/')
                end_date    = datetime.datetime(year=int(entry_date[2]), month=int(entry_date[0]), day=int(entry_date[1]))
                start_date  = end_date - datetime.timedelta(days=7)

                for _row in earnings_df.iterrows():
                    try:
                        earnings_date = self.__get_earnings_date(_row)

                        # is there an earnings day that falls between start_date and end_date?
                        if earnings_date < end_date and earnings_date >= start_date:                           
                            # self.__add_to_reported_stocks(symbol, earnings_date)
                            self.__add_to_reported_stocks(symbol, end_date)
                            reported = True
                            break
                    except Exception as e:
                        G.log.print_and_log(e=e, filename=__file__)

                if not reported:  
                    self.__add_to_unreported_stocks(symbol, entry_date)
                reported = False

            except Exception as e:
                G.log.print_and_log(e=e, filename=__file__)
            stock_count += 1
            
        self.__write_to_excel()
        return
