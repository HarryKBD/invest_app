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


class BlAccount:
    def __init__(self, init_invest, cash_ratio):
        self.cash = init_invest
        self.cash_ratio = cash_ratio
        self.scount = 0
        self.invested = init_invest

    def sell_all(self, sprice, dd):
        svalue = self.scount * (sprice * 0.98)
        self.cash += svalue
        self.scount = 0
        print(f'{dd} SELL ALL  now total value: {self.cash: .2f}')

    def rebalance(self, sprice, dd):
        stock_value = self.scount * sprice
        cash_value = self.cash

        total_value = stock_value + cash_value
        cash_ratio = cash_value / total_value * 100.0

        #print(f'{dd} try rebal: total: {total_value}  ==> cash_ratio: {cash_ratio: .2f} stock_value: {stock_value}  cash_value: {cash_value}')
        if abs(cash_ratio - self.cash_ratio) > 5: # if diff is greather than 5 percent
            self.cash = total_value * self.cash_ratio/100.0
            left = total_value - self.cash
            self.scount = math.floor(left / (sprice * 1.02))
            new_total = self.cash + self.scount*sprice
            print(f'{dd} Rebalancing: before(cash percent: {cash_ratio: .2f} After =>  cash: {self.cash: .3f}  stock cnt: {self.scount} total: {new_total: .2f}')
            #self.print_value(sprice)
        else:
            left = 0
            #print(f'{dd} No rebalancing is rquired')

    def print_value(self, sprice):
        total = self.cash + (self.scount * sprice)
        earn = total - self.invested
        earn_percent = earn / self.invested * 100.0
        print(f'Account:  Cash: {self.cash: .2f}   Stock cnt: {self.scount}  stock_val: {self.scount * sprice} => Total: {total: .2f} ({earn_percent: .2f} %)')

if __name__ == '__main__':
    conn = hdb.connect_db("./stock_all.db")
    start_date = '2000-01-01'
    end_date = '2021-12-30'
    #end_date = '2015-03-05'
    
    today = datetime.now()
    sdate = ht.to_datetime(start_date)
    edate = ht.to_datetime(end_date)
    
    c = 'TQQQ'
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

    in_bad_state = False
    cur_laa_status = False

    for_sure_cnt = 4
    recover_check_cnt = 0
    bad_check_cnt = 0

    account = BlAccount(100000, 10)
    check_laa = True
    account.rebalance(price[0], dd[0])
    print(f'Init account done')

    prev_dd = '0000-00-00'
    for d, p in zip(dd, price):
        if d == '2016-02-27':
            continue

        if ht.is_same_month(prev_dd, d) == False and in_bad_state == False:
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
                    if check_laa:
                        account.sell_all(p, d)
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
                    if check_laa:
                        account.rebalance(p, d)
            else:
                recover_check_cnt = 0
                #print(f'{d} --> Reset Recover check cnt')

        if p > peak:
            #print(f'{d} ==> {p: .3f} cur_down: {cur_down: .3f} this_mdd: {this_mdd: .3f} ({this_mdd_date}) last_peak: {last_peak_date}  max_mdd: {max_mdd} ({max_mdd_date})')
            peak = p
            last_peak_date = d
            this_mdd = 0
            #print(f'{d} ==> {p: .3f} NEW Peak')

        cur_down = (peak - p)/peak * 100.0
        prev_dd = d

        if cur_down > this_mdd:
            this_mdd = cur_down
            #print(f'{d} ==> {p: .3f} cur_down: {cur_down :.3f} this_mdd: {this_mdd: .3f} ({this_mdd_date}) last_peak: {last_peak_date}  max_mdd: {max_mdd} ({max_mdd_date})')
            if this_mdd > max_mdd:
                max_mdd = this_mdd
                max_mdd_date = d
            this_mdd_date = d

    print(f'{d} ==> {p: .3f} cur_down: {cur_down :.3f} this_mdd: {this_mdd: .3f} ({this_mdd_date}) last_peak: {last_peak_date}  max_mdd: {max_mdd} ({max_mdd_date})')

    account.print_value(p)
    conn.close()




