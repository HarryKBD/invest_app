
import json

str = ( '{"mdd_stocks" : [], '
        ' "laa": { "labor" : "True", "Spy" : "False" } ' 
        ' } ')

stock_result_list = [
        '{"code":"TQQQ", "update":"2021-12-31", "price":"33.23", "cur_down":"32", "latest_peak_date":"2021-11-01", "latest_peak_price":"50.22", "this_mdd":"40" ' ' }',
        '{"code":"TQQQ2", "update":"2021-12-31", "price":"33.23", "cur_down":"32", "latest_peak_date":"2021-11-01", "latest_peak_price":"50.22", "this_mdd":"40" ' ' }'
        '{"code":"TQQQ3", "update":"2021-12-31", "price":"33.23", "cur_down":"32", "latest_peak_date":"2021-11-01", "latest_peak_price":"50.22", "this_mdd":"40" ' ' }'
                    ]
                   
#print(str)
code_list = ['TQQQ', 'QLD', 'QQQ', 'SPY', 'SOXL', 'UPRO']
start_date = '2015-01-01'

#for c in code_list:
#    cur_date, price, cur_down, this_max_mdd, this_max_mdd_date, all_max_mdd, all_max_mdd_date = su.get_mdd_values(conn, c, start_date)

resp = json.loads(str)
resp["mdd_stocks"] = stock_result_list
print(resp["mdd_stocks"][1])

str = json.dumps(resp)
print(str)
