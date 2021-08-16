import stock_utils as su
import code_list
import hdb
import datetime
import happy_utils as ht
import init_stock_db as indb


def update_stock_daily_db(conn):
    for c in code_list.my_codes:
        price = su.update_stock_db_today(conn, c)
        if price != None:
            t = datetime.datetime.now()
            today_str = ht.datetime_to_str(t)
            print(f'today:{today_str}   Updating {c} ==> {price}')

if __name__ == '__main__':
    conn = hdb.connect_db("stock_all.db")

    update_stock_daily_db(conn)
    indb.prepare_fred_init_data(conn, ht.to_datetime('1900-01-01'), datetime.datetime.now())

    conn.close()