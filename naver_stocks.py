import numpy as np
import pandas as pd
from datetime import datetime

import requests
import threading
import numpy as np
import io
from bs4 import BeautifulSoup


def naver_sise_time(stock, date):
    print("[%s] %s" % (stock, date))
    
    data = []
    for c in range(1, 50):
        url = "http://finance.naver.com/item/sise_time.nhn?code=%s&thistime=%s160000&page=%s" \
              % (stock, date, c)
        response = requests.get(url)
        soup = BeautifulSoup(response.text.encode('utf-8'), 'html.parser')
        quotes = soup.find_all('span', {'class': ['tah', 'p10']})

        for li in quotes:
            data.append(li.text.strip())
        try:
            if data[-7] == '09:00':
                break
        except:
            pass
        
    # 체결시각 체결가 전일비 매도 매수 거래량 변동량
    if len(data) == 0 :
        r = np.zeros(shape=(1,9))
    else:
        quote = np.reshape(np.array(data), (-1, 7)).tolist()
        r = [[date] + [stock] + i for i in quote]
        r = np.array(r)
    print(r.shape)
    
    return r

# 종목코드
def naver_sise_market_sum():
    d = pd.DataFrame() 
       
    for c in range(1, 50):
        url = "https://finance.naver.com/sise/sise_market_sum.nhn?sosok=0&page=%s" % (c)
        print(url)
        response = requests.get(url)
        soup = BeautifulSoup(response.text.encode('utf-8'), 'html.parser')
        tbl = soup.select('.type_2')[0]
        tbl_rows = tbl.find_all('tr')
        l = []
        for tr in tbl_rows:
            td = tr.find_all('td')
            row = [tr.text.replace('\n','').replace('\t','') for tr in td]
            try:
                stock_code = tr.select('.tltle')[0]['href'].split('=')[1]
                row.insert(1, stock_code)
                l.append(row)
            except:
                pass
            
        try:
            columns = ['N','종목코드','종목명','현재가','전일비','등락률','액면가','시가총액','상장주식수','외국인비율','거래량','PER','ROE','토론방']
            df = pd.DataFrame(l, columns=columns)
            df = df[pd.to_numeric(df.N) > 0].set_index('N').drop(columns='토론방')
            d = d.append(df)
        except:
            pass
        
    return d
    

if __name__=='__main__':
    # 네이버 코스피 종목코드를 받아서
    stocks = naver_sise_market_sum()
    
    # 기간동안 거래량을 입수하여
    days = pd.date_range('20200131', '20200207', ).strftime('%Y%m%d')
    r = np.vstack([np.vstack([naver_sise_time(stock=s, date=d) for d in days]) for s in stocks.종목코드])
    
    # 데이터프레임으로 작성함
    columns = ['기준일자','종목코드','체결시각','체결가','전일비','매도','매수','거래량','변동량']
    df = pd.DataFrame(r, columns=columns)
    df = df[df.기준일자.str.len()>=8].reset_index(drop=True)
    to_numeric = ['체결가','전일비','매도','매수','거래량','변동량']
    for c in to_numeric:
        df[c] = df[c].str.replace(',','').apply(pd.to_numeric)
    
    # Pickle로 저장
    df.to_pickle("./naver_sise_time_20200207")
