new_magic_small_code = []

low_value_code = []

super_quant_code = []

asset_alloc_code = [ '148070', '195980', '272580', '305080', '319640', '360750', '219480', '267440', '304660', \
                     '261220', '319640', '137610', '360750', '195980', '148070', '332620', '182480', '272580', \
                     '360750', '368590', '251350', '308620', '304660']

my_interested_codes = ['DOW', 'DIA', 'VIG','QQQ','VTI','VOO','IVV','EFA','SPY', 'QLD', 'TQQQ', 'FNGU', 'DDM', 'SOXL', 
                       'SSO', 'UPRO', '123320', '233160', '^KS11', '^KQ11', '^HSI', 'TMF', 'TLT', 'RPAR', '409820', '399001.SZ']

# KODEX Nasdaq leverage => 409820
my_codes = new_magic_small_code + low_value_code + super_quant_code + asset_alloc_code + my_interested_codes

#관심 주식
#코스피 지수 
#코스닥 지수

#Tiger 레버리지(123320), Tiger  코스닥150 레버리지(233160)

#미국:  DOW, SPY, QQQ, DIA, 2x레버리지(SSO, QLD) 3x(UPRO, TQQQ, SOXL)

#QQQ, TQQQ, 



#test code
if __name__ == "__main__":

    for k in my_codes:
        print(k)

