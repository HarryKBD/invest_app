import FinanceDataReader as fdr
import hdb
from datetime import datetime
from datetime import date
import code_list
import happy_utils as ht
import happy_server as hs
from stock_def import AssetAllocItem, StockPrice
import pandas as pd

FORMAT_DATE = '%Y-%m-%d'

def prepare_fred_init_data(conn, date_from, date_to):
    fred = hs.get_fred_data_from_server("UNRATE", date_from, date_to)
    
    print("prepare_fred")
    result = []
    for last_date, price in fred:
        s = StockPrice("UNRATE", last_date, float(price), float(price), float(price),  float(price), int(price), 0)
        result.append(s)
    
    print("Inserting data " + str(len(result)))
    hdb.insert_stock_data(conn, result)

def prepare_initial_table(conn, code_list, date_from, date_to):
    #hdb.create_table(conn)
    #hdb.clean_all_stock_price_table(conn)
    hdb.create_all_tables(conn)
    edate_str = date_to.strftime(FORMAT_DATE)
    sdate_str = date_from.strftime(FORMAT_DATE)

    print("{} from  ==> {} to".format(sdate_str, edate_str))
    cnt = 1
    for code in code_list:
        print(f'Code => {code}')
        result_list = hs.get_stock_data_from_server(code, date_from, date_to)
        hdb.insert_stock_data(conn, result_list)
        print("Getting {} data:  {} / {} ==> cnt: {}".format(code, str(cnt), str(len(code_list)), str(len(result_list))))
        cnt += 1

    prepare_fred_init_data(conn, date_from, date_to)
    

    #op 1: 'BUY'  2: 'SELL'

#python init_stock_db -c 283782 -c 283728


#my_codes = ['140410', '302550', '251370', '064760', '036810', '005070', '278280', '298050', '009830', '306200', '327260',
        #'218410', '099320', '001820', '009150', '066570', '012330', '102120', '036420', '005930']
        
def init_fund_list_db(conn):
    hdb.create_fund_table(conn)
    f = open("fund_list.txt", "r")
    fund_name = 'Default'
    code = 'Default'
    price = 0.0
    cnt = 0
    buy_date = '2021-05-08'
    code_list = []
    for l in f:
        tokens = l.split()
        if len(tokens) < 2:
            continue
        if tokens[0] == 'fund_name':
            if len(tokens) != 2:
                print("Read error line => " + l)
                return -1
            fund_name = tokens[1]
        else:
            if len(tokens) != 3:
                print("Read error2: line => " + l)
                return -1
            code = tokens[0]
            price = float(tokens[1])
            cnt = int(tokens[2])
            code_list.append(code)
            print(f"Inserting data: {code}, {buy_date}, {price}, {cnt}, {fund_name}")
            hdb.insert_stock_in_fund(conn, code, buy_date, price, cnt, fund_name)
    
    f.close()
    return 1

def init_asset_alloc_fund_db(conn, fname):
    hdb.create_asset_allocation_stock_table(conn)
    df = pd.read_csv(fname, \
                dtype = {"stock_code":str, "avg_price":float, "ideal_ratio":float, "category":int, "last_updated":str})

    slist = []
    for idx, row in df.iterrows():
        item = AssetAllocItem()
        item.set_asset_data_by_series(row)
        print(item.to_string())
        slist.append(item)

    hdb.insert_asset_alloc_stock_data(conn, slist)

#class asset_alloc_stock:
#    def __init__(self, fund, code, name_eng, name_kor, price, count, ideal_ratio, category, last_update=None):

def init_target_list(conn):
    hdb.create_target_list_table(conn)
    hdb.insert_target_list(conn, 'Health', '048260', 36500, '2020-12-01', 'Dang', wanted='1')
    hdb.insert_target_list(conn, 'Space', '047810', 23700, '2020-12-01', 'Dang')
    hdb.insert_target_list(conn, 'Airplaine', '067390', 5430, '2020-12-01', 'Dang', wanted='1')
    hdb.insert_target_list(conn, 'Travel','080160', 16450, '2020-12-01', 'Dang')
    hdb.insert_target_list(conn, 'Food system', '051500', 18850,'2020-12-01', 'Dang', wanted='1')
    hdb.insert_target_list(conn, 'Battery','247540', 55000,'2020-12-01', 'Dang')
    hdb.insert_target_list(conn, 'Battery','020150', 42150,'2020-12-01', 'Dang')
    hdb.insert_target_list(conn, 'Battery','243840', 39500,'2020-12-01', 'Dang', wanted='1')
    hdb.insert_target_list(conn, 'Battery','131390', 11000,'2020-12-01', 'Dang')
    hdb.insert_target_list(conn, 'Battery','079810', 9500,'2020-12-01', 'Dang', wanted='1')
    hdb.insert_target_list(conn, 'Battery','137400', 6470,'2020-12-01', 'Dang')
    hdb.insert_target_list(conn, 'Battery/OLED', '161580', 14200,'2020-12-01', 'Dang', wanted='1')
    hdb.insert_target_list(conn, '4th','086960', 15650, '2020-12-01', 'Dang')
    hdb.insert_target_list(conn, 'Green','009450', 55300,'2020-12-01', 'Dang', wanted='1')
    hdb.insert_target_list(conn, 'IT material', '178920', 29300,'2020-12-01', 'Dang')
    hdb.insert_target_list(conn, 'Electric Medicine', '302550', 26000,'2020-12-01', 'Dang')
    hdb.insert_target_list(conn, 'Health','054950', 35500, '2020-12-01', 'Dang', wanted='1')
    hdb.insert_target_list(conn, 'OLED', '347770', 16800,'2021-01-01', 'Dang', wanted='1')
    hdb.insert_target_list(conn, 'Consumer', '036670', 9780, '2020-12-01', 'Dang')
    hdb.insert_target_list(conn, 'Ship', '010620', 49500, '2021-02-02', 'Dang', wanted='1')
    hdb.insert_target_list(conn, 'Ship', '010140', 6480,'2021-02-02', 'Dang')
    hdb.insert_target_list(conn, 'Ship', '042660', 26600,'2021-02-02', 'Dang')
    hdb.insert_target_list(conn, 'LNG/H','033500', 11000,'2021-02-02', 'Dang', wanted='1')
    hdb.insert_target_list(conn, 'LNG Parts', '013030', 14950, '2021-02-02', 'Dang', wanted='1')
    hdb.insert_target_list(conn, 'Shipping','028670', 4110, '2020-12-01', 'Dang')
    hdb.insert_target_list(conn, 'Shipping','044450', 10300, '2020-12-01', 'Dang')
    hdb.insert_target_list(conn, 'Food system','051160', 11700, '2020-12-01', 'Dang')
    hdb.insert_target_list(conn, 'Semiconductor','140860', 50400, '2020-12-01', 'Dang')
    hdb.insert_target_list(conn, 'Semiconductor','083450', 20100, '2020-12-01', 'Dang')
    hdb.insert_target_list(conn, '5G','050890', 11050, '2020-12-01', 'Dang')
    hdb.insert_target_list(conn, '5G','039560', 12500, '2020-12-01', 'Dang')
    hdb.insert_target_list(conn, '5G','032640', 12100, '2020-12-01', 'Dang', wanted='1')
    hdb.insert_target_list(conn, 'China/Food','222980', 6870, '2020-12-01', 'Dang')
    hdb.insert_target_list(conn, 'IT material', '009150', 219000, '2020-01-01', 'Jiho')
    
    hdb.insert_target_list(conn, 'IT material', '272210', 18050, '2020-01-01', 'Jiho')                       
    hdb.insert_target_list(conn, 'Battery', '298000', 218500, '2020-01-01', 'Jiho')                       
    hdb.insert_target_list(conn, 'Space', '298050', 297816, '2020-01-01', 'Jiho')                       
    hdb.insert_target_list(conn, 'IT material', '064760', 147300, '2020-01-01', 'Jiho')                       
    hdb.insert_target_list(conn, 'Space', '099320', 66934, '2020-01-01', 'Jiho')                       
    hdb.insert_target_list(conn, 'Medical', '140410', 176897, '2020-01-01', 'Jiho')                       
    hdb.insert_target_list(conn, 'Battery', '251370', 21900, '2020-01-01', 'Jiho')                       
    hdb.insert_target_list(conn, 'Battery', '327260', 32507, '2020-01-01', 'Jiho')                           
    
def init_current_stock(conn):
    hdb.create_current_stock_table(conn)
    hdb.insert_current_stock(conn, '009150', 219000, 92)
    hdb.insert_current_stock(conn, '009450', 49124, 204)
    hdb.insert_current_stock(conn, '010140', 6380, 782)
    hdb.insert_current_stock(conn, '010620', 55200, 90)
    hdb.insert_current_stock(conn, '047810', 34500, 581)
    hdb.insert_current_stock(conn, '272210', 18050, 1111)
    hdb.insert_current_stock(conn, '298000', 218500, 91)
    hdb.insert_current_stock(conn, '298050', 297816, 139)
    hdb.insert_current_stock(conn, '033500', 11905, 557)
    hdb.insert_current_stock(conn, '048260', 61000, 328)
    hdb.insert_current_stock(conn, '064760', 147300, 133)
    hdb.insert_current_stock(conn, '099320', 66934, 583)
    hdb.insert_current_stock(conn, '102940', 18300, 143)
    hdb.insert_current_stock(conn, '140410', 176897, 133)
    hdb.insert_current_stock(conn, '251370', 21900, 913)
    hdb.insert_current_stock(conn, '302550', 30897, 647)
    hdb.insert_current_stock(conn, '327260', 32507, 922)
    
    
import json

#from_date = datetime(2001, 1, 1)
#prepare_initial_table(conn, from_date)  #returns only 5 per query
#log_buy_stock(conn, '068270', 300000, 999)
#log_sell_stock(conn, '068270', 380000, 999)

if __name__ == "__main__":
   
#     parser = argparse.ArgumentParser()
       
#     parser.add_argument('-c', '--code', dest='codes', required=True, action='append', 
#         help="code")

#     parser.add_argument('-f', '--from', dest='from_date', required=True, help="date from")    
#     parser.add_argument('-t', '--to', dest='to_date', required=True, help="date to")
#     args = parser.parse_args()

# #Date format 2021-01-01
#     tokens = args.from_date.split("-")
#     datef = datetime(int(tokens[0]), int(tokens[1]), int(tokens[2]))

#     tokens = args.to_date.split("-")
#     datet = datetime(int(tokens[0]), int(tokens[1]), int(tokens[2]))

    conn = hdb.connect_db("stock_all.db")
    ##################To fill the stock price list use this block##############################
    #my_codes = ['VIG','QQQ','VTI','VOO','IVV','EFA','SPY', 'QLD', 'TQQQ', 'FNGU', 'DDM', 'SOXL', 'SSO', 'UPRO','123320', '233160', '243880', '122630', '306950', '233740', '102110', '232080', '139260', '229720', '226980', '229200', '102110', '114820']
    #my_codes = ['VT', 'DBC', 'IAU', 'TLT', 'LTPZ', 'VCLT', 'EMLC']
    #my_codes = ['US500', 'UNRATE']
    #my_codes = ['399001.SZ']

    from code_list import my_codes

    tokens = '2000-01-01'.split("-")
    datef = datetime(int(tokens[0]), int(tokens[1]), int(tokens[2]))
    tokens ='2022-04-28'.split("-")
    datet = datetime(int(tokens[0]), int(tokens[1]), int(tokens[2]))
    print(my_codes)
    #prepare_initial_table(conn, my_codes, datef, datet)
    #prepare_fred_init_data(conn, datef, datet)
    #init_fund_list_db(conn)

    init_asset_alloc_fund_db(conn, './fund_list_today.csv')

  

    ###########################################################################################
    
    ###################### To init the list of the stocks interested ##########################
    #init_target_list(conn)
    ################################################################################################
    
    
    #######################  To init the current list of the stockes owned by me ######################
    #init_current_stock(conn)
    ###################################################################################################
    
    # update_codes = args.codes


    # if update_codes[0] == 'codelist':
    #     # ??????????????? ???????????? ??????
    #     df_krx = fdr.StockListing('KRX')
    #     print(df_krx.head())
    # else:
    #     if update_codes[0] == 'all':
    #         #process codes
    #         update_codes = my_codes
      
    #     print(f'updating db {datef}  {datet} with codes{update_codes}')       
    #     prepare_initial_table(conn, update_codes, datef, datet)
    
    conn.close()
