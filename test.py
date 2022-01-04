import yahoo_fin.stock_info as si 
import FinanceDataReader as fdr
# 종목 조회 
#dow_list = si.tickers_dow()
#nasdaq_list = si.tickers_nasdaq()
#sp500_list = si.tickers_sp500()
#other_list= si.tickers_other()
#Tickers in Dow Jones: 30 #Tickers in Nasdaq: 3841 #Tickers in S&P 500: 505 # �용stock_list �성(�스+ 기�) stock_list = nasdaq_list + other_list print("Tickers in stock_list:", len(stock_list)) #Tickers in Others: 9382

#AAPL = si.get_stats('AAPL')
#print(AAPL.loc[[8,31,32,33],:])

#from yahoo_fin.stock_info import get_data
#from yahoo_fin.stock_info import get_live_price

#amazon_daily= get_data("amzn", start_date="12/01/2000", end_date="01/02/2022", index_as_date = True, interval="1d")
#print(amazon_daily)

#day_price = get_data("amzn", start_date="12/20/2021", end_date="12/31/2022", index_as_date = True, interval="1d")
#print(day_price)

#lp = get_live_price("amzn")
#print(lp)

sp = fdr.DataReader('SPY') # S&P 500 지(NYSE)
print(sp)

#import FinanceDataReader as fdr
# �플(AAPL), 2018-01-01 ~ 2018-03-30
#df = fdr.DataReader('AAPL', '2018-01-01', '2018-03-30')
#df.tail()

if __name__ == '__main__':
    df = fdr.DataReader('QQQ', '2020-12-30', '2021-12-30')
    print(df)
