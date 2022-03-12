import stock_utils as su
import code_list
import hdb
import datetime
import happy_utils as ht
import init_stock_db as indb


def update_stock_daily_db(conn):
    #code_l = ['^KS11', 'QQQ', 'QLD', '302440', '285130', '024090', 'RPAR', 'UPRO']
    #for c in code_l:
    for c in code_list.my_codes:
        price, dd = su.update_stock_db_today(conn, c)
        if price != None:
            log.w('today: ' + dd + ' Updating ' + c + '  ' + str(price))
        else:
            log.w('today: ' + dd + ' No update ' + c)

if __name__ == '__main__':

    #global log
    log = ht.Logger("daily")
    log.enable()    

    log.w("Getting today's data from server and insert into database. today is : " + ht.datetime_to_str(datetime.datetime.now()))
    conn = hdb.connect_db("stock_all.db")

    update_stock_daily_db(conn)
    indb.prepare_fred_init_data(conn, ht.to_datetime('1900-01-01'), datetime.datetime.now())

    conn.close()
