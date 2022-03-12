from re import I
import yfinance as yf
import happy_utils as ht
import numpy as np
import happy_server as hs
import happy_utils as ht
import stock_utils as st
import hdb

if __name__ == "__main__":
    #df = yf.download('048470.KS',start = '2022-03-10')
#    df = yf.download("148070.KS")
#
#    print(df)
#
#    print(len(df))
#    print(df.index)
#    dt = ht.to_datetime('2022-03-10')
#    if dt in df.index:
#        data = df.loc[dt]
#        print(df.loc[dt])
#        print(data['Close'])
#    else:
#        print("No data")
#
    #print(df.loc[dt])
    #r = df.loc[dt]
    #print(len(r))
    start = '2022-01-01'
    end = '2022-03-31'
    #t = hs.get_stock_data_from_server('005930', ht.to_datetime(start), ht.to_datetime(end))
    t = hs.get_stock_data_from_server('AAPL', ht.to_datetime(start), ht.to_datetime(end))

    for s in t:
        print(s.to_full_text())

    conn = hdb.connect_db("stock_all.db") 
    st.update_stock_db_today(conn, 'AAPL')
    st.update_stock_db_today(conn, '005930')
    conn.close()