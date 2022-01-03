import FinanceDataReader as fdr
from datetime import datetime
from datetime import timedelta
from datetime import date
from stock_def import StockPrice
from happy_utils import FORMAT_DATE
import happy_utils as ht

       

#import FinanceDataReader as fdr
# 애플(AAPL), 2018-01-01 ~ 2018-03-30
#df = fdr.DataReader('AAPL', '2018-01-01', '2018-03-30')
#df.tail()

if __name__ == '__main__':
    df = fdr.DataReader('QQQ', '2020-12-30', '2021-12-30')
    print(df)
