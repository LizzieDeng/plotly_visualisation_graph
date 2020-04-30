# -*- coding: utf-8 -*- 
"""
Project: huayi_interview
Creator: Administrator
Create time: 2020-04-27 12:59
IDE: PyCharm
Introduction:
"""

import re
import pandas as pd
import matplotlib.pyplot as plt




time_list= []
def read_dat_into_pandas():
    new_pd = pd.DataFrame()
    with open('ReceivedTofile-COM4-2020_4_26_17-53-28.txt', 'rb') as f:
        lines = f.readlines()[1:]
        for i, line in zip(range(len(lines)), lines):
            if line[0:3] == b't= ':
                line = line.decode('utf-8')
                line = line.split(',')
                # 获取时间
                t = re.findall(r'-?\d+\.\d+', line[0])[0]
                t = float(t)
                time_list.append(t)
                # 取出字段及其值
                column_name = line[1].split('=')[0]
                column_unit = line[1].split('=')[1]
                # 匹配整数,小数,负整数,负小数
                column_value = re.findall(r'^(\d+\.\d+|\d+|-\d+\.\d+)', column_unit)[0]
                column_value = float(column_value)
                if i == 5:
                    new_pd.loc[0, 'time'] = t
                    new_pd.loc[0, column_name] = column_value
                else:
                    if t in list(new_pd['time']):
                        new_pd.loc[new_pd[new_pd['time'].isin([t])].index.tolist()[0], column_name] = column_value
                    else:
                        new_pd.loc[new_pd.shape[0], 'time'] = t
                        new_pd.loc[new_pd[new_pd['time'].isin([t])].index.tolist()[0], column_name] = column_value
    # 重置index
    new_pd = new_pd.reset_index(drop=True)
    # new_pd.to_csv('output_nan.csv', index=False)
    # 删除全为NAN的行
    new_pd = new_pd.dropna(axis=0, how='all')
    # 值为NAN的补0
    new_pd = new_pd.fillna(0)
    # 将时间转化成int型
    new_pd['time'] = new_pd['time'].astype("int")
    new_pd.to_csv('output.csv', index=False)
    return new_pd


def draw_line_graph(new_pd):
    new_pd.plot(x='time', title='all field')
    plt.show()

    new_pd['whl_ang'].plot(title='whl_ang')
    plt.show()

    df3 = new_pd.drop(labels='whl_ang', axis=1)  # axis=1 表示按列删除，删除whl_ang列
    df3.plot(x='time', title='except whl_ang')
    plt.show()

    new_pd['lnd_whl_spd'].plot(title='lnd_whl_spd')
    plt.show()

    new_pd['rnd_whl_spd'].plot(title='rnd_whl_spd')
    plt.show()


if __name__ =="__main__":
    new_pd = read_dat_into_pandas()
    draw_line_graph(new_pd)




