new_magic_small_code = []

low_value_code = []

super_quant_code = [
                    '048470','012620','134060','072130','026910','071090','054040','054930','094970','005860',
                    '001770','153460','026040','025880','080520','187270','208140','123700','093380','131180',
                    '023350','131090','005360','318010','088910','119500','017480','069730','032680','023790',
                    '225590','071090','002220','048470','079170','025560','072950','001770','072130','002690',
                    '030720','079000','011420','044780','010660','037760','149980','008420','025880','014910',
                    '147760','138070','080010','010470','087600','263860','060380']

asset_alloc_code = [ '148070', '195980', '272580', '305080', '319640', '360750', '219480', '267440', '304660', \
                     '261220', '319640', '137610', '360750', '195980', '148070', '332620', '182480', '272580', \
                     '360750', '368590', '251350', '308620', '304660']

my_interested_codes = ['DOW', 'DIA', 'VIG','QQQ','VTI','VOO','IVV','EFA','SPY', 'QLD', 'TQQQ', 'FNGU', 'DDM', 'SOXL', 'SSO', 'UPRO', '123320', '233160', '^KS11', '^KQ11', '^HSI', 'TMF', 'TLT', 'RPAR', '409820', '399001.SZ']

ticker_code = ['^GSPC', '^IXIC', 'QQQ', 'QLD', 'TQQQ', 'SPY', 'SSO', 'UPRO', 'SOXL', 'TLT', 'TMF', 'RPAR', '^KS11', '^KQ11', '409820', '399001.SZ']

# KODEX Nasdaq leverage => 409820
# ^GSPC => S&P 500 index
# ^IXIC => Nasdaq index
# 305720 => Kodex Second Battery



my_codes = new_magic_small_code + low_value_code + super_quant_code + asset_alloc_code + my_interested_codes + ticker_code
my_codes = list(set(my_codes))

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

