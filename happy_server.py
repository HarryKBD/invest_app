
import FinanceDataReader as fdr
from datetime import datetime
from datetime import timedelta
from datetime import date
from stock_def import StockPrice
from happy_utils import FORMAT_DATE
import happy_utils as ht

def get_stock_data_from_server(code, s_datetime, e_datetime):
    price_days = []
    col_closed = 'Close'
    sdate_str = s_datetime.strftime(FORMAT_DATE)
    edate_str = e_datetime.strftime(FORMAT_DATE)
    #print("Connecting server to get data code: {}  from: {}  to: {} ".format(code, sdate_str, edate_str))
    while True:
        df = fdr.DataReader(code, sdate_str, edate_str)
        if len(df) == 0:
            #print("No more data for code : " + code)
            break
        #print(df.head())
        openp = df['Open']
        highp = df['High']
        lowp = df['Low']
        closep = df[col_closed]
        vol = df['Volume']
        change = df['Change']

        idx = df.index
        i = 0
        for c in closep:
            last_date =  idx[i].to_pydatetime()
            s = StockPrice(code, last_date, float(openp[i]), float(highp[i]), 
                    float(lowp[i]),  float(c), int(vol[i]), float(change[i]))
            price_days.append(s)
            #print(s.to_text())
            i += 1
        
        if ht.same_date(e_datetime, last_date):
            break;
        last_date += timedelta(days=1)
        sdate_str = "{}-{}-{}".format(last_date.year, last_date.month, last_date.day)
        #sdate_str = "{}-{}-{}".format(last_date.year, last_date.month+1, last_date.day)

    return price_days

def get_fred_data_from_server(code, s_datetime, e_datetime):
    sdate_str = s_datetime.strftime(FORMAT_DATE)
    edate_str = e_datetime.strftime(FORMAT_DATE)
    print("Connecting server to get data code: {}  from: {}  to: {} ".format(code, sdate_str, edate_str))
    ret = []
    while True:
        df = fdr.DataReader(code, sdate_str, edate_str, data_source='fred')
        if len(df) == 0:
            #print("No more data for code : " + code)
            break
        data_list = df[code]

        idx = df.index
        i = 0
        for value in data_list:
            last_date =  idx[i].to_pydatetime()
            print(f'{last_date} => {value}')
            ret.append((last_date, value))
            i += 1
        
        break

    return ret