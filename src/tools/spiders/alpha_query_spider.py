import datetime

import pandas as pd

from ..util.enums   import *
from ..util.globals import G


class AlphaQuerySpider():
    def __init__(self) -> None:
        self._reported_stocks      = dict()
        self._reported_stock_dates = dict()
        self._unreported_stocks    = dict()
        return

    def __add_to_reported_stocks(self, symbol, entry_date: datetime.datetime) -> None:
        if symbol in self._reported_stocks.keys():
            self._reported_stocks[symbol].append(entry_date.strftime("%m-%d-%Y"))
        else:
            self._reported_stocks[symbol] = [entry_date.strftime("%m-%d-%Y")]
        return

    def __add_to_reported_stock_dates(self, symbol, reported_date: datetime.datetime) -> None:
        if symbol in self._reported_stock_dates.keys():
            self._reported_stock_dates[symbol].append(reported_date.strftime("%m-%d-%Y"))
        else:
            self._reported_stock_dates[symbol] = [reported_date.strftime("%m-%d-%Y")]
        return

    def __add_to_unreported_stocks(self, symbol: str, entry_date: list) -> None:
        entry_date_str = entry_date[0] + '-' + entry_date[1] + '-' + entry_date[2]
        
        if symbol in self._unreported_stocks:
            self._unreported_stocks[symbol].append(entry_date_str)
        else:
            self._unreported_stocks[symbol] = [entry_date_str]
        return
    
    def __write_to_excel(self) -> None:
        reported_df   = pd.DataFrame({'Symbols': list(self._reported_stocks.keys()), 'Entry Dates': self._reported_stocks.values(), 'Reported Dates': self._reported_stock_dates.values()})
        unreported_df = pd.DataFrame({'Symbols': list(self._unreported_stocks.keys()), 'Entry Dates': self._unreported_stocks.values()})

        G.log.print_and_log(f"Reported stocks\n{reported_df}")
        G.log.print_and_log(f"Unreported stocks\n{unreported_df}")

        with pd.ExcelWriter('Trade_Result.xlsx', engine='xlsxwriter') as writer:
            reported_df.to_excel(writer,   sheet_name="Reported_Stocks")
            unreported_df.to_excel(writer, sheet_name="Unreported_Stocks")   
        return

    def __get_earnings_date(self, _row: tuple) -> datetime.datetime:
        f_quarter_end = [int(i) for i in _row[1][ANNOUNCEMENT_DATE].split('-')]
        earnings_date = datetime.datetime(year=f_quarter_end[0], month=f_quarter_end[1], day=f_quarter_end[2])
        return earnings_date

    def scrape_data(self) -> None:
        stock_df        = pd.read_excel(STOCK_LIST, usecols=['Date', 'Symbol', 'Type'])
        symbol_list_len = len(stock_df['Symbol'].to_list())
        stock_count     = 1
        reported        = False

        for row in stock_df.iterrows():
            entry_date_list = row[1]['Date']
            order_type      = row[1]['Type']
            symbol          = row[1]['Symbol']
            order_type      = order_type.replace(' ', '').upper()

            if order_type == LONG_ENTRY:
                G.log.print_and_log(f"Fetching data for {symbol} {entry_date_list} {stock_count} / {symbol_list_len}")
                
                url = ALPHA_QUERY_URL + symbol + '/' + 'earnings-history'

                try:
                    earnings_df     = pd.read_html(url)[0]
                    entry_date_list = entry_date_list.split('/')
                    entry_date_dt   = datetime.datetime(year=int(entry_date_list[2]), month=int(entry_date_list[0]), day=int(entry_date_list[1]))
                    start_date      = entry_date_dt - datetime.timedelta(days=7)

                    for _row in earnings_df.iterrows():
                        try:
                            earnings_date_dt = self.__get_earnings_date(_row)

                            if earnings_date_dt < entry_date_dt and earnings_date_dt >= start_date:
                                self.__add_to_reported_stocks(symbol, entry_date_dt)
                                self.__add_to_reported_stock_dates(symbol, earnings_date_dt)
                                reported = True
                                break
                        except Exception as e:
                            G.log.print_and_log(e=e, filename=__file__)

                    if not reported:
                        self.__add_to_unreported_stocks(symbol, entry_date_list)
                    
                    reported = False
                except Exception as e:
                    G.log.print_and_log(e=e, filename=__file__)
                stock_count += 1
            
        self.__write_to_excel()
        return
