import stock_utils as su
import code_list
import hdb
import datetime
import happy_utils as ht
import init_stock_db as indb


def update_stock_daily_db(conn):
    t = datetime.datetime.now()
    today_str = ht.datetime_to_str(t)
    for c in code_list.my_codes:
        price = su.update_stock_db_today(conn, c)
        if price != None:
            log.w('today: ' + today_str + ' Updating ' + c + '  ' + str(price))
        else:
            log.w('today: ' + today_str + ' No update ' + c)

if __name__ == '__main__':

    #global log
    log = ht.Logger("daily")
    log.enable()    

    log.w("Getting today's data from server and insert into database. today is : " + ht.datetime_to_str(datetime.datetime.now()))
    conn = hdb.connect_db("stock_all.db")

    update_stock_daily_db(conn)
    indb.prepare_fred_init_data(conn, ht.to_datetime('1900-01-01'), datetime.datetime.now())

    conn.close()
