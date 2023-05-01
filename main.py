from datetime import datetime
import pandas as pd

from bs4 import BeautifulSoup as bs
import requests

import OpenDartReader
from api_key import DART_API_KEY

import telegram

# 공시 타입
pblntf_ty = "I"
pblntf_detail_ty='I006' # 공정공시

EARNING_REPORT = ['영업(잠정)실적(공정공시)', '연결재무제표기준영업(잠정)실적(공정공시)']
REPORT_URL = "https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcp_no}"
NAVER_URL = "https://finance.naver.com/item/main.nhn?code={code}"


def search_report_today():
    # today = datetime.today().strftime('%Y-%m-%d')
    today = '2023-04-28'
    print(f"Search {today} reports...")
    
    # 공시 검색
    try:
        report_list = dart.list(start=today, end=today, kind=pblntf_ty, kind_detail=pblntf_detail_ty, final=False)
    except Exception as e:
        print('Failed searching by: ', e)
        return

    print(f"num of today's 공정공시 reports: {len(report_list)}")

    return report_list

def get_earning_report(report_df):

    is_earning_1 = report_df['report_nm'] == EARNING_REPORT[0]
    is_earning_2 = report_df['report_nm'] == EARNING_REPORT[1]
    earning_df = report_df[is_earning_1 | is_earning_2]
    print(f"num of earning reports: {len(earning_df)}")
    return earning_df

def report_parser(earning_df):
    # parsing earning value and consensus
    for i, (idx, row) in enumerate(earning_df.iterrows()):
        if i != 0:
            break
        xml_text = dart.document(row['rcept_no'])
        soup = bs(xml_text, 'html.parser')

        trs = soup.find_all('tr')
        #############
        # earning value parsing
        #############
        # print(trs[2])
        # print(trs[2].find_all('td'))
        # print(trs[2].find("td").find("span").text)

        stock_code = row['stock_code']
        print(stock_code)
        get_consen(stock_code)

def get_consen(code):
    r = requests.get(NAVER_URL.format(code=code))
    df = pd.read_html(r.text)[3]
    print(df.head())
    #############
    # consensus value parsing
    #############

if __name__ == "__main__":
    dart = OpenDartReader(DART_API_KEY)
    
    # get today reports in dart
    report_df = search_report_today() 
    # get only earning notice
    earning_df = get_earning_report(report_df)
    report_parser(earning_df)

