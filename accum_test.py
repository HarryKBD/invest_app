
import hdb
import sys
import math
import argparse
from datetime import datetime
from datetime import date
import matplotlib.pyplot as plt




class Account:
    def __init__(self, code):
        self.avg_price = 0
        self.code = code
        self.scnt = 0
        self.buy_penalty = 0.00
        self.sell_penalty = 0.00
        self.cash = 0
        self.total_invested = 0
        self.avg_price = 0
        pass

    def get_average_price(self):
        return self.avg_price

    def buy(self, price, invest, additional = 0):
        self.total_invested += invest

        buy_price = price + price * self.buy_penalty
        to_buy_cnt = math.floor((invest + additional)/buy_price)
        #print(f'{to_buy_cnt} {price} {invest}')

        new_avg_price = (self.scnt * self.avg_price + to_buy_cnt * buy_price)/(self.scnt + to_buy_cnt)
        print(f'Current stock cnt: {self.scnt} ==> BUY {to_buy_cnt}  after buy: {self.scnt+to_buy_cnt} todayp: {price} avgprice: {self.avg_price} => {new_avg_price:.2f}')

        self.scnt += to_buy_cnt
        self.avg_price = new_avg_price
        money_left = (invest + additional) - (to_buy_cnt * buy_price)
        self.cash += money_left

        return money_left


    def sell(self, price, percent):
        sell_cnt = math.floor(self.scnt * percent / 100.0)
        avg = self.get_average_price()
        left_cnt = self.scnt - sell_cnt
        print(f'Current stock cnt: {self.scnt} ==> Sell {sell_cnt}  left:{left_cnt}, todayp: {price} avg: {avg}')

        self.scnt = left_cnt
        get_money =  sell_cnt * (price - price * self.sell_penalty)
        self.cash += get_money

        return get_money

    def get_cur_stock_value(self, cur_price):
        return cur_price * self.scnt

    def get_total_profit_ratio(self, cur_price):
        cur_value = self.get_cur_stock_value(cur_price) + self.cash
        earned = cur_value - self.total_invested
        profit_ratio = earned / self.total_invested * 100.0
        return profit_ratio, earned

    def get_str_status(self, price):
        profit_ratio, earned = self.get_total_profit_ratio(price)
        sprofit_only = (price - self.avg_price)/self.avg_price * 100.0

        #print(f'{profit_ratio}, {earned}, {self.cash} {sprofit_only}, price  {self.avg_price}, {price}')
       
        return " total invested: {:.1f}, total value: {:.2f} earned: {:.2f}, rate: {:.1f} % |||cash: {:.1f} avg_price: {:.2f}  curr_price: {} scnt: {}".format(
                self.total_invested, self.get_total_value(price), earned, profit_ratio, self.cash, self.get_average_price(), price, self.scnt)
    def get_scnt(self):
        return self.scnt

    def print_status(self, price):
        status_str = self.get_str_status(price)
        print(status_str)

    def get_total_invested(self):
        return self.total_invested

    def get_total_value(self, price):
        return self.get_cur_stock_value(price) + self.cash

    def get_cash(self):
        return self.cash

    def widraw_cash(self, percent):
        v = self.cash * percent / 100.0
        self.cash -= v
        return v

def is_same_month(d1, d2):
    tokens = d1.split("-")
    mon1 = int(tokens[1])

    tokens = d2.split("-")
    mon2 = int(tokens[1])

    if mon1 == mon2:
        return True
    else:
        return False

def assertEqual(a, b):
    if a != b:
        print(f'Error:  a: {a}   b: {b}')
        sys.exit()

def run_test():
    acc = Account('12345')

    left = acc.buy(1000, 10000)
    avg = acc.get_average_price()
    total = acc.get_total_value(1000)
    assertEqual(avg, 1000)
    assertEqual(left, 0)
    assertEqual(acc.get_total_invested(), 10000)
    assertEqual(total, 10000)
    assertEqual(acc.get_scnt(), 10)

    left = acc.buy(500, 10000)
    total = acc.get_total_value(500)
    avg = acc.get_average_price()
    assertEqual(avg, 666)
    assertEqual(left, 0)
    assertEqual(acc.get_total_invested(), 20000)
    assertEqual(total, (10+20)*500)
    assertEqual(acc.get_scnt(), 30)

    left = acc.buy(2000, 10000)
    total = acc.get_total_value(2000)
    avg = acc.get_average_price()
    assertEqual(avg, 856)
    assertEqual(left, 0)
    assertEqual(acc.get_total_invested(), 30000)
    assertEqual(total, (10+20+5)*2000)
    assertEqual(acc.get_scnt(), 35)


    get_money = acc.sell(1000, 20)
    total = acc.get_total_value(1000)
    assertEqual(get_money, 1000*7)
    assertEqual(acc.get_cash(), get_money)
    invested = acc.get_total_invested()
    assertEqual(invested, 30000)
    avg = acc.get_average_price()
    assertEqual(avg, 856)
    assertEqual(acc.get_scnt(), 28)
    assertEqual(total, 7000+28*1000)


    get_money2 = acc.sell(2000, 30)
    total = acc.get_total_value(2000)
    assertEqual(get_money2, 2000*8)
    assertEqual(get_money + get_money2, acc.get_cash())
    invested = acc.get_total_invested()
    assertEqual(invested, 30000)
    assertEqual(acc.get_scnt(), 20)
    assertEqual(total, 7000+16000+20*2000)
    acc.print_status(2000)

    return True


def to_datetime(date_str):
     tokens = date_str.split("-")
     return datetime(int(tokens[0]), int(tokens[1]), int(tokens[2]))

def to_datetime5(date_str):
     tokens = date_str.split("-")
     return datetime(int(tokens[0])+5, int(tokens[1]), int(tokens[2]))

if __name__ == "__main__":

    #run_test()
    conn = hdb.connect_db("stock_all.db")
    #my_codes = hdb.get_stock_code_list_interested(conn)

    #test_code = 'QQQ'
    test_code = '069500'

    sdate = '2002-01-01'
    edate = '2015-05-01'

    #valid, fdate, price = hdb.get_stock_data_from_db(conn, test_code, to_datetime(sdate), to_datetime(edate))
    valid, fdate, price = hdb.get_stock_data_from_db(conn, test_code, to_datetime(sdate), to_datetime5(sdate))
    print(len(fdate))

    minvest = 1000000

    profit_rate = [10, 20, 30, 40, 50]
    #sell_ratio = [20, 25, 33, 50, 100]
    sell_ratio = [20, 20, 20, 20, 20]
    sell_ratio = [0, 0, 0, 0, 0]

    pidx = 0
    idx = 1
    acc = Account(test_code)
    acc.buy(price[0], minvest)
    prev_date = fdate[0]
    print(prev_date)
    max_val = 0
    min_val = 1000000000000000000000
    mdd = 0

    val_list = []
    invested_list = []
    profit_list = []
    d_list = []
    x_list = []
    for p in price[1:]:
        today = fdate[idx]
        x_list.append(idx)
        if is_same_month(prev_date, today) != True:
            print(f"Month changed BUY date: {today}")
            sprofit_only = (p - acc.get_average_price())/acc.get_average_price()* 100.0
            print(f"{today}  => sprofit   {sprofit_only} ----------------------------------------------------------------------")
            if sprofit_only < -20.0:
                more = acc.widraw_cash(50.0)
                print(f"{today}  => buy more   {more}")
            else:
                more = 0
            #more = acc.widraw_cash(0.0)

            #more = acc.widraw_cash(10.0)
            #more = 0
            acc.buy(p, minvest, additional = more)
            acc.print_status(p)

        earn_rate = (p - acc.get_average_price())/acc.get_average_price() * 100.0
        val = acc.get_total_value(p)
        val_list.append(val)
        invested_list.append(acc.get_total_invested())
        profit_list.append(earn_rate)

        if val > max_val:
            max_val = val
            min_val = val
            #print(f'MAX SET {today} => {max_val}')

        if val < min_val:
            min_val = val
            down = (max_val - min_val)/max_val * 100.0 * -1
            if down < mdd:
                mdd = down
            #print(f'MIN SET {today} => {min_val}, {down} {mdd}')



        #print(f'{today}  today_price: {p} avg: {acc.get_average_price()}  earn_rate: {earn_rate:.2f}')
        if earn_rate > profit_rate[pidx]:
            #sell some
            print(f'SELL date: {today}, cur_idx: {pidx} --------------------------------------')
            acc.sell(p, sell_ratio[pidx])
            pidx += 1
            d_list.append(today)
            acc.print_status(p)
            if pidx == len(profit_rate):
                pidx = 0
                #print("Done")
                #sys.exit()
        else:
            d_list.append('.')

        if earn_rate < 0:
            pidx = 0

        prev_date = today
        idx += 1

    print('-'*200)
    print(f"Test end.  mdd = {mdd}")
    acc.print_status(p)
    #plt.plot(val_list)
    #plt.plot(invested_list)
    #plt.figure(figsize=(100, 40))
    #plt.plot(x_list, profit_list)
    #plt.xticks(x_list, d_list, rotation=90)
    #plt.show()


    conn.close()
