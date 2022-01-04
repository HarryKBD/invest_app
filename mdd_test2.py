# 결정 표인트
# rebalancing 을 하는 방법
# 1. 항상 월마다
# 2. 안하다가 전고점을 넘었을때 리밸런싱. 또 안하다가
# 3. 항상 월마다 하고, worst로 들어갔을때 추가 매수를 하고, 전고점을 넘을때까지 안하고 있다가 그다음 부터는 다시 월마다


# worst 가 아닌한 
# 그냥 가져가는게 맞다

from datetime import datetime
import sys
import math
import hdb
import happy_utils as ht
import laa

MY_HOME='./'

def exit_prog(conn, msg):
    print(msg)
    conn.close()
    sys.exit()
def assertEqual(a, b):
    if a != b:
        print(f'Error:  a: {a}   b: {b}')
        sys.exit()


class BlAccount:
    def __init__(self, init_invest, cash_ratio, buy_penalty=0, sell_penalty=0):
        self.cash = init_invest
        self.cash_ratio = cash_ratio
        self.scount = 0
        self.invested = init_invest
        self.buy_penalty = buy_penalty
        self.sell_penalty = sell_penalty
        self.best_profit_rate = 0.0
        self.best_profit_date = 'NONE'
        self.worst_profit_rate = 0.0
        self.worst_profit_date = 'NONE'
        self.peak = 0.0
        self.peak_date = 'NONE'
        self.mdd = 0.0
        self.mdd_date = 'NONE'

    def buy_more_stock_from_internal_cash(self, sprice, amount):
        sprice_adj = sprice + (sprice * self.buy_penalty)
        to_buy_cnt = math.floor(amount / sprice_adj)
        left = amount - to_buy_cnt * sprice_adj
        self.cash = self.cash - amount + left
        self.scount += to_buy_cnt
        return to_buy_cnt

    def get_cash(self):
        return self.cash

    def get_stock_count(self):
        return self.scount

    def get_total_value(self, sprice):
        return self.scount * sprice + self.cash

    def get_cash_ratio(self):
        return self.cash_ratio

    def set_cash_ratio(self, ratio):
        self.cash_ratio = ratio

    def get_invested(self):
        return self.invested
    
    def get_best_ratio(self):
        return self.best_profit_rate

    def get_worst_ratio(self):
        return self.worst_profit_rate
    
    def stat(self, sprice, dd):
        cur_val = self.get_total_value(sprice)
        acc_diff = cur_val - self.invested
        profit_rate = acc_diff / self.invested * 100.0
        if profit_rate > self.best_profit_rate:
            self.best_profit_rate = profit_rate
            self.best_profit_date = dd
        
        if profit_rate < self.worst_profit_rate:
            self.worst_profit_rate = profit_rate
            self.worst_profit_date = dd

        #calcuate mdd
        if cur_val > self.peak:
            self.peak = cur_val
            self.peak_date = dd
        mdd = (self.peak - cur_val)/self.peak * 100.0
        if mdd > self.mdd:
            self.mdd = mdd
            self.mdd_date = dd

    def sell_all(self, sprice, dd):
        sprice_adj = sprice - sprice*self.sell_penalty
        svalue = self.scount * sprice_adj
        self.cash += svalue
        self.scount = 0
        print(f'{dd} SELL ALL  price: {sprice: .2f} now total value: {self.cash: .2f}')
        return self.cash

    def rebalance(self, sprice, dd):
        stock_value = self.scount * sprice
        cash_value = self.cash
        prev_scount = self.scount

        total_value = stock_value + cash_value
        cash_ratio = cash_value / total_value * 100.0

        #print(f'{dd} try rebal: total: {total_value}  ==> cash_ratio: {cash_ratio: .2f} stock_value: {stock_value}  cash_value: {cash_value}')
        if abs(cash_ratio - self.cash_ratio) > 5: # if diff is greather than 5 percent
            print(f'{dd} start rebalancing price: {sprice}')
            ideal_cash = total_value * self.cash_ratio/100.0

            if self.cash > ideal_cash: #TO BUY MORE
                to_buy = self.cash - ideal_cash
                bought_cnt = self.buy_more_stock_from_internal_cash(sprice, to_buy)

                #sprice_adj = sprice + (sprice * self.buy_penalty)
                #to_buy_cnt = math.floor(to_buy / sprice_adj)
                #left = to_buy - to_buy_cnt * sprice_adj
                #self.cash = self.cash - to_buy + left
                #self.scount += to_buy_cnt
                print(f'{dd} buy stock more {bought_cnt}')
            else: #TO SEE And get more cash
                to_sell = ideal_cash - self.cash
                sprice_adj = sprice - (sprice * self.sell_penalty)
                to_sell_cnt = math.floor(to_sell / sprice_adj)
                self.cash += to_sell_cnt * sprice_adj
                self.scount -= to_sell_cnt
                #print(f'{dd} sell stock {to_sell_cnt}')

            new_total = self.cash + self.scount*sprice
            #print(f'{dd} Rebalancing: before(cash p: {cash_ratio: .2f} scount:{prev_scount} After =>  cashp: {self.cash_ratio: .3f}  stock cnt: {self.scount} total: {new_total: .2f}')
            #self.print_value(sprice)
        else:
            left = 0
            #print(f'{dd} No rebalancing is rquired')

    def rebalance2(self, sprice, dd):
        stock_value = self.scount * sprice
        cash_value = self.cash
        prev_scount = self.scount

        total_value = stock_value + cash_value
        cash_ratio = cash_value / total_value * 100.0

        #print(f'{dd} try rebal: total: {total_value}  ==> cash_ratio: {cash_ratio: .2f} stock_value: {stock_value}  cash_value: {cash_value}')
        if abs(cash_ratio - self.cash_ratio) > 5: # if diff is greather than 5 percent
            self.cash = total_value * self.cash_ratio/100.0
            left = total_value - self.cash
            sprice_adj = sprice + (sprice * self.buy_penalty)
            self.scount = math.floor(left / sprice_adj)
            self.cash += (left - self.scount * sprice_adj)
            new_total = self.cash + self.scount*sprice
            print(f'{dd} Rebalancing: before(cash p: {cash_ratio: .2f} scount:{prev_scount} After =>  cashp: {self.cash_ratio: .3f}  stock cnt: {self.scount} total: {new_total: .2f}')
            #self.print_value(sprice)
        else:
            left = 0
            #print(f'{dd} No rebalancing is rquired')

    def get_value_string(self, sprice):
        total = self.cash + (self.scount * sprice)
        earn = total - self.invested
        earn_percent = earn / self.invested * 100.0
        str = f'Account:  Cash: {self.cash: .2f}   Stock cnt: {self.scount}  stock_val: {self.scount * sprice: .2f} => Total: {total: .2f} ({earn_percent: .2f} %)'
        return str
    
    def get_status_string(self, sprie):
        str = f'best: {self.best_profit_rate: .2f} worst: {self.worst_profit_rate: .2f} peak: {self.peak}, mdd: {self.mdd: .2f}'
        return str

    def print_value(self, sprice, head=None):
        if head == None:
            print(self.get_value_string(sprice))
        else:
            print(head + " " + self.get_value_string(sprice))
    
    def print_status(self, sprice, head=None):
        if head == None:
            print(self.get_status_string(sprice))
        else:
            print(head + " " + self.get_status_string(sprice))

def run_port_item_test():
    dd = '2021-01-01'
    acc = BlAccount(10000, 50)
    acc.rebalance(100, dd)
    ret = acc.get_cash_ratio()
    assertEqual(ret, 50)
    ret = acc.get_total_value(100)
    assertEqual(ret, 10000)
    ret = acc.get_stock_count()
    assertEqual(ret, 50)
    ret = acc.get_total_value(200)
    assertEqual(ret, 15000)
    acc.rebalance(200, dd)
    ret = acc.get_stock_count()
    assertEqual(ret, 38)
    ret = acc.get_cash()
    assertEqual(ret, 7400)
    ret = acc.get_invested()
    assertEqual(ret, 10000)
    ret = acc.get_total_value(200)
    assertEqual(ret, 15000)

    acc = BlAccount(10000, 50, 0.05, 0.05)
    acc.rebalance(100, dd)

    ret = acc.get_stock_count()
    assertEqual(ret, 47)
    ret = acc.get_cash()
    assertEqual(ret, 5065)
    ret = acc.sell_all(100, dd)
    assertEqual(ret, 9530)

    acc = BlAccount(10000, 50, 0.02, 0.02)
    acc.rebalance(100, dd)

    ret = acc.get_stock_count()
    assertEqual(ret, 49)
    ret = acc.get_cash()
    assertEqual(ret, 5002)
    ret = acc.sell_all(100, dd)
    assertEqual(ret, 9804)

    acc.rebalance(100, dd)
    ret = acc.get_stock_count()
    assertEqual(ret, 48)
    ret = acc.get_cash()
    assertEqual(ret, 4908)
    ret = acc.sell_all(100, dd)
    assertEqual(ret, 9612)

    acc = BlAccount(10000, 40, 0.02, 0.02)
    acc.rebalance(100, dd)

    ret = acc.get_stock_count()
    assertEqual(ret, 58)
    ret = acc.get_cash()
    assertEqual(ret, 4084)
    ret = acc.sell_all(100, dd)
    assertEqual(ret, 9768)

    acc = BlAccount(10000, 40, 0.1, 0.1)
    acc.rebalance(200, dd)

    ret = acc.get_stock_count()
    assertEqual(ret, 27)
    ret = acc.get_cash()
    assertEqual(ret, 4060)
    ret = acc.sell_all(200, dd)
    assertEqual(ret, 8920)
    print("Passed all test cases")

def test_mdd(conn, start_date, end_date, code, cash_ratio, laa_bad_sell_all):
    
    sdate = ht.to_datetime(start_date)
    edate = ht.to_datetime(end_date)
    c = code 
    valid, dd, price = hdb.get_stock_data_from_db(conn, c, sdate, edate)
    print(f'{c} => len {len(dd)}')
    if valid == False:
        print(c)
        exit_prog(conn, "code not found in the db error")

    idx = 0
    peak = -100
    lowest = 100000000
    max_mdd = 0
    this_mdd = 0
    last_peak_date = 'NONE'
    this_mdd_date = 'NONE'
    max_mdd_date = 'NONE'
    cur_down = 0
    max_account_mdd = 0

    in_bad_state = False
    cur_laa_status = False

    for_sure_cnt = 5
    recover_check_cnt = 0
    bad_check_cnt = 0

    target_sell_price = 0
    account = BlAccount(100000, cash_ratio, 0.02, 0.02)
    #laa_bad_sell_all = False  #param
    monthly_rebalance = True
    monthly_rebalance_hold = False
    buy_more_when_laa_bad = True
    peak_rebalance = True
    peak_rebalance_hold = True
    account.rebalance(price[0], dd[0])
    print(f'Init account done')

    prev_dd = '0000-00-00'
    for d, p in zip(dd, price):
        if d == '2016-02-27':
            continue

        if ht.is_same_month(prev_dd, d):
            if  monthly_rebalance and monthly_rebalance_hold == False:
                account.rebalance(p, d)

        un_status = laa.get_unrate_status(conn, ht.to_datetime(d))
        snp_status = laa.get_snp_status(conn, ht.to_datetime(d))
        if un_status == False and snp_status == False:
            cur_laa_status = False
        else:
            cur_laa_status = True

        if in_bad_state == False:  #We are in normal status, check if bad signal
            if cur_laa_status == False:
                bad_check_cnt+= 1
                if bad_check_cnt > for_sure_cnt:
                    print(f'{d} ==> {p: .3f}  Became bad status')
                    in_bad_state = True
                    bad_check_cnt = 0
                    recover_check_cnt = 0
                    if laa_bad_sell_all:
                        account.sell_all(p, d)
                        monthly_rebalance_hold = True
            else:
                #print(f'{d} --> Reset bad check cnt')
                bad_check_cnt = 0

        if in_bad_state:   #now we are in bad status, check if recover signal
            if cur_laa_status == True:
                recover_check_cnt += 1
                if recover_check_cnt > for_sure_cnt:
                    print(f'{d} ==> {p: .3f} Became good status')
                    in_bad_state = False
                    recover_check_cnt = 0
                    bad_check_cnt = 0
                    if buy_more_when_laa_bad == False:
                        account.rebalance(p, d)

            else:
                recover_check_cnt = 0
                #print(f'{d} --> Reset Recover check cnt')

        if p > peak:
            #print(f'{d} ==> {p: .3f} cur_down: {cur_down: .3f} this_mdd: {this_mdd: .3f} ({this_mdd_date}) last_peak: {last_peak_date} max_mdd: {max_mdd: .2f} ({max_mdd_date}) acc_worst: {account.get_worst_ratio(): .2f}')
            if buy_more_when_laa_bad and peak_rebalance and peak_rebalance_hold == False and p >= target_sell_price:
                account.rebalance(p, d)
                monthly_rebalance_hold = False #we can continue montly rebalance
                peak_rebalance_hold = True
            #account.print_value(p, d)
            peak = p
            last_peak_date = d
            this_mdd = 0
            #print(f'{d} ==> {p: .3f} NEW Peak')

        cur_down = (peak - p)/peak * 100.0
        prev_dd = d

        if cur_down > this_mdd:
            this_mdd = cur_down
            #print(f'{d} ==> {p: .3f} cur_down: {cur_down: .3f} this_mdd: {this_mdd: .3f} ({this_mdd_date}) last_peak: {last_peak_date} max_mdd: {max_mdd: .2f} ({max_mdd_date}) acc_worst: {account.get_worst_ratio(): .2f}')
            #account.print_value(p, d)
            if in_bad_state and buy_more_when_laa_bad: #buy more when laa bad and this time mdd goes more down
               cnt = account.buy_more_stock_from_internal_cash(p, account.get_cash() * 0.3)
               print(f'{d} MORE BUY price({p: .2f}) NEW This MDD==> {p: .3f} _mdd: {this_mdd: .3f} buy more: {cnt}')
               monthly_rebalance_hold = True
               peak_rebalance_hold = False
               target_sell_price = peak * 1
            if this_mdd > max_mdd:
                max_mdd = this_mdd
                max_mdd_date = d
            this_mdd_date = d
        
        account.stat(p, d)
        #account.print_status(p)

    print(f'RESULT: {start_date} - {end_date} {c} => {account.get_value_string(p)} {account.get_status_string(p)}')



if __name__ == '__main__':
    #run_port_item_test()
    conn = hdb.connect_db("./stock_all.db")
    start_date = '2018-09-01'
    end_date = '2020-12-30'
    code = 'QLD'
    cash_ratio = 0 
    laa_bad_sell_all = False

    #cash_ratio_list = [0, 30, 40, 50, 60, 70]
    cash_ratio_list = [0, 50]
    #code_list = ['QQQ', 'SPY', 'QLD', 'SSO', 'SOXL', 'UPRO', 'TQQQ']
    code_list = ['TQQQ']
    laa_bad_sell_all_list= [False]
    #laa_bad_sell_all_list= [True]
    #date_list = [('2018-09-01', '2020-12-30'), ('2007-01-01', '2021-12-30'), ('2015-01-01', '2021-12-31'),  ('2011-01-01', '2020-12-31')]
    date_list = [('2011-01-01', '2012-12-31')]


    for dd_pair in date_list:
        start_date = dd_pair[0]
        end_date = dd_pair[1]
        for code in code_list:
            for cash_ratio in cash_ratio_list:
                for laa_bad_sell_all in laa_bad_sell_all_list:
                    print(f'Testing - {start_date} - {end_date} : {code}  {cash_ratio} {laa_bad_sell_all}')
                    test_mdd(conn, start_date, end_date, code, cash_ratio, laa_bad_sell_all)
                    print(f'-------------------------------- Done ---------------------------------------')

    conn.close()
