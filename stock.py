import re
import ast
import time
import requests
import pandas as pd
from decimal import Decimal
from sqlalchemy import create_engine
from datetime import datetime, timedelta

#东财 http://data.eastmoney.com/hsgt/top10/2020-04-17.html

# 时间列表
def datelist(startdate, enddate):
    time_list = []
    start_date = datetime.strptime(startdate, '%Y-%m-%d')
    end_date = datetime.strptime(enddate, '%Y-%m-%d')
    while start_date <= end_date:
        date_str = start_date.strftime('%Y-%m-%d')
        time_list.append(date_str)
        start_date += timedelta(days=1)
    return time_list



# 网络异常处理
def try_again(url): #连接
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Cookie': 'intellpositionL=1522.39px; cowminicookie=true; cowCookie=true; '
                  'HAList=a-MMK-156; st_si=44739368759479; '
                  'st_asi=delete; '
                  'emshistory=%5B%22A50%E6%9C%9F%E6%8C%87%22%2C%22A50%22%2C%22A50%E6%8C%87%E6%95%B0%22%2C%22%E5%AF%8C%E6%97%B6%E4%B8%AD%E5%9B%BDA50%E6%8C%87%E6%95%B0%22%2C%22ETF%22%2C%22%E4%BA%8C%E5%80%8D%22%2C%22%E4%BA%8C%E5%80%8D%20%E4%B8%AD%E5%9B%BD%22%2C%22%E4%BA%8C%E5%80%8D%E4%B8%AD%E5%9B%BD%22%2C%22VIX%22%2C%22VIX%E6%81%90%E6%85%8C%E6%8C%87%E6%95%B0%22%2C%22vix%22%5D; dRecords=%u516C%u53F8%u9898%u6750%7Chttp%3A//data.eastmoney.com/gstc/%2C*%u673A%u6784%u8C03%u7814%7Chttp%3A//data.eastmoney.com/jgdy/%2C*%u80A1%u4E1C%u9AD8%u7BA1%u6301%u80A1%7Chttp%3A//data.eastmoney.com/gdggcg/%20%2C*%u4F30%u503C%u5206%u6790%7Chttp%3A//data.eastmoney.com/gzfx/%2C*%u4E3B%u529B%u6570%u636E%7Chttp%3A//data.eastmoney.com/zlsj/%2C*%u80A1%u4E1C%u5206%u6790%7Chttp%3A//data.eastmoney.com/gdfx/%2C*%u9F99%u864E%u699C%u5355-%u4EAC%u7CAE%u63A7%u80A1%7Chttp%3A//data.eastmoney.com/stock/lhb%2C2020-04-01%2C000505.html%2C*%u9F99%u864E%u699C%u5355-%u6DF1%u4E2D%u534EA%7Chttp%3A//data.eastmoney.com/stock/lhb%2C2020-03-13%2C000017.html%2C*%u9F99%u864E%u699C%u5355-%u667A%u6167%u80FD%u6E90%7Chttp%3A//data.eastmoney.com/stock/lhb%2C2020-03-13%2C600869.html%2C*%u9F99%u864E%u699C%u5355-%u4EAC%u6295%u53D1%u5C55%7Chttp%3A//data.eastmoney.com/stock/lhb%2C2020-03-13%2C600683.html%2C*%u9F99%u864E%u699C%u5355-%u6D77%u521BB%u80A1%7Chttp%3A//data.eastmoney.com/stock/lhb%2C2020-03-13%2C900955.html%2C*%u56FD%u5BB6%u961F%u6301%u80A1%7Chttp%3A//data.eastmoney.com/gjdcg/%2C*%u80A1%u7968%u8D26%u6237%u7EDF%u8BA1%28%u6708%29%7Chttp%3A//data.eastmoney.com/cjsj/gpkhsj.html%2C*%u5927%u5B97%u4EA4%u6613%7Chttp%3A//data.eastmoney.com/dzjy/default.html%2C*%u6CAA%u6DF1%u6E2F%u901A%u8D44%u91D1%7Chttp%3A//data.eastmoney.com/hsgt/index.html%2C*%u6CAA%u6DF1%u6E2F%u901A%u6301%u80A1%7Chttp%3A//data.eastmoney.com/hsgtcg/%2C*%u6CAA%u6DF1%u6E2F%u901A%u6210%u4EA4%7Chttp%3A//data.eastmoney.com/hsgt/top10.html; '
                  'intellpositionT=1575.91px; '
                  'qgqp_b_id=97931591a8ff5231cd4146f92987c02b; '
                  'st_pvi=14434505422424; st_sp=2020-03-22%2021%3A39%3A42; '
                  'st_inirUrl=http%3A%2F%2Fdata.eastmoney.com%2Fhsgtcg%2F; '
                  'st_sn=29; st_psi=20200419000949773-112101300783-4633673003',
        'Host': 'data.eastmoney.com',
        'Referer': 'http://data.eastmoney.com/hsgt/index.html',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
    }
    while True:
        try:
            res = requests.get(url, headers=headers)
            res.encoding = 'gbk'
            res = res.text

            list = []
            for i in range(1, 5):
                str = f'var DATA{i}'
                list.append(re.findall(r'%s = {"data":(.*})' % str, res)[0][:-1])
            return list
        except Exception as e:
            print(f"{type(e).__name__}: {e}")
            time.sleep(10)



def HSGT(url, date):
    print('开始爬取：' + date)
    list = try_again(url)
    df_lsit = []
    num = 0
    for res in list:
        num += 1
        if ast.literal_eval(res):
            df = pd.DataFrame(ast.literal_eval(res))
            df.rename(columns={
                'MarketType': '市场类型',
                'DetailDate': '日期',
                'Rank': '排名',
                'Code': '代码',
                'Name': '名称',
                'Close': '收盘价',
                'ChangePercent': '涨跌幅',
            }, inplace=True)

            if num == 1: df.rename(columns={'HGTJME': '净买额'}, inplace=True)
            if num == 2: df.rename(columns={'SGTJME': '净买额'}, inplace=True)
            if num == 3: df.rename(columns={'GGTHJME': '净买额'}, inplace=True)
            if num == 4: df.rename(columns={'GGTSJME': '净买额'}, inplace=True)

            df['市场类型'].replace(1, '沪港通十大成交股', inplace=True)     #DATA1
            df['市场类型'].replace(3, '深港通十大成交股', inplace=True)     #DATA2
            df['市场类型'].replace(2, '港股通(沪)十大成交股', inplace=True)  #DATA3
            df['市场类型'].replace(4, '港股通(深)十大成交股', inplace=True)  #DATA4

            df = df[['市场类型', '日期', '排名','代码', '名称', '收盘价', '涨跌幅', '净买额']]
            df['收盘价'] = df['收盘价'].map(lambda x: Decimal(x).quantize(Decimal('0.00')))
            df['涨跌幅'] = df['涨跌幅'].map(lambda x: Decimal(x).quantize(Decimal('0.00')))
            df['日期'] = df['日期'].map(lambda x: x[0:10])
            df.sort_values('净买额', ascending=False, inplace=True)
            df.reset_index(drop=True, inplace=True)
            for i in range(0, len(df.index)):
                df.loc[i, '排名'] = int(i + 1)
            df_lsit.append(df)

    if df_lsit:
        df = pd.concat(df_lsit)
        df.reset_index(drop=True, inplace=True)
        for i in range(len(df.index)):
            if df.loc[i,'市场类型'] == '沪港通十大成交股':df.loc[i, '成交额'] = f'=EM_S_DQ_AMOUNT(D{i+2},B{i+2},1)'
            if df.loc[i,'市场类型'] == '深港通十大成交股':df.loc[i, '成交额'] = f'=EM_S_DQ_AMOUNT(D{i+2},B{i+2},1)'
            if df.loc[i,'市场类型'] == '港股通(沪)十大成交股':df.loc[i, '成交额'] = f'=EM_HKS_DQ_AMOUNT(D{i+2},B{i+2},"4",1)'
            if df.loc[i,'市场类型'] == '港股通(深)十大成交股':df.loc[i, '成交额'] = f'=EM_HKS_DQ_AMOUNT(D{i+2},B{i+2},"4",1)'
            df.loc[i,'占当日成交比例'] = f'=ABS(H{i+2})/I{i+2}'
        return df
    else:
        print('              休息日')
        return '休息日'


if __name__ == "__main__":
    engine = create_engine('mysql+pymysql://geliang:geliang@192.168.56.101/BI')
    # 范围时间
    start_dt = '2020-04-01'
    end_dt = '2020-04-03'
    dt_list = datelist(start_dt, end_dt)

    # dt_list = ['2020-04-17']                                    # 自定义时间
    # dt_list = [time.strftime("%Y-%m-%d", time.localtime())]     # 当天时间

    list = []
    res = pd.DataFrame()
    for date in dt_list:
        url = f'http://data.eastmoney.com/hsgt/top10/{date}.html'
        print("url", url)
        df = HSGT(url, date)
        print("df", df, type(df))
        res = res.append(df)
    print(res)





        # if type(df) != str:list.append(df)

    # df = pd.DataFrame(list)
    # df.to_excel('aaaa.xlsx')

    # num = 0
    # for i in range(0,len(list)):
    #     num += 1
    #     eval(f"""df{num} = {list[i]}""")
        # print(list[i])

    # print(df3)

    # pd.concat
        #     df.to_sql('hsgt_top10', engine, index=False, if_exists='append')  # append、replace
