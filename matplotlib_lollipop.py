import pandas as pd
import matplotlib.pyplot as plt
# 正常显示中文
plt.rcParams['font.sans-serif'] = ['SimHei']
# 用来正常显示负号
plt.rcParams['axes.unicode_minus'] = False


def get_data_via_date_from_excel(date):
    excel_pd = pd.read_excel('data\IC期货商历史数据(1).xlsx', index_col='日期')
    # 去空
    excel_pd.dropna()
    # 去除000905_SH列
    excel_pd = excel_pd.drop(labels='000905_SH', axis=1)
    # 去0行
    excel_pd = excel_pd[~(excel_pd == 0).all(axis=1)]
    # 筛选日期
    sheet1_data = excel_pd.loc[date]
    # 去除列值为0
    sheet1_data = sheet1_data[sheet1_data != 0]
    # 排序 从小到大
    sheet1_data = sheet1_data.sort_values()
    # 空仓
    short_hold = sheet1_data[sheet1_data < 0]
    # 多仓
    long_hold = sheet1_data[sheet1_data >= 0].sort_values(ascending=False)
    return short_hold, long_hold


def draw_lollipop_graph(short_hold, long_hold, date):
    # sheet_major.index.values.tolist()
    fig, ax = plt.subplots(figsize=(10, 8))
    # 空仓水平线
    ax.hlines(y=[i for i in range(len(short_hold))], xmin=list(short_hold), xmax=[0] * len(short_hold.index), color='#1a68cc', label='空')
    # 多仓水平线
    ax.hlines(y=[i for i in range(len(long_hold))], xmax=list(long_hold), xmin=[0] * len(long_hold.index), color='red', label='多')
    # 画散点
    ax.scatter(x=list(short_hold), y=[i for i in range(len(short_hold))], s=10, marker='d', edgecolors="#1a68cc", zorder=2, color='white')  # zorder设置该点与其他线不相交
    ax.scatter(x=list(long_hold), y=[i for i in range(len(long_hold))], s=10, marker='d', edgecolors="red", zorder=2, color='white')  # zorder设置该点与其他线不相交
    # 画线两端标注图
    for x, y, label in zip(list(short_hold), range(len(short_hold)), short_hold.index):
        plt.text(x=x, y=y, s=label+'({}) '.format(abs(x)), horizontalalignment='right', verticalalignment='center', fontsize=10)
    for x, y, label in zip(list(long_hold), range(len(long_hold)), long_hold.index):
        plt.text(x=x, y=y, s=' '+label+'({})'.format(abs(x)), horizontalalignment='left', verticalalignment='center', fontsize=10)
    # 设置排名
    size = [17, 16, 15] + [8 for i in range(max(len(short_hold), len(long_hold))-3)]
    color = ['#b91818', '#e26012', '#dd9f10'] + ['#404040' for i in range(max(len(short_hold), len(long_hold))-3)]
    for i, s, c in zip(range(max(len(short_hold), len(long_hold))+1), size, color):
        plt.annotate(s=i+1, xy=(0, i), fontsize=s, ma='center', ha='center', color=c)
    # 坐标轴y反置
    ax.invert_yaxis()
    # 坐标轴不可见
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)  # 去上边框
    ax.spines['bottom'].set_visible(False)  # 去下边框
    ax.spines['left'].set_visible(False)  # 去左边框
    ax.spines['right'].set_visible(False)  # 去右边框
    # 设置title
    ax.set_title('黄金持仓龙虎榜单({})'.format(date), position=(0.7, 1.07), fontdict=dict(fontsize=20, color='black'))
    # 自动获取ax图例句柄及其标签
    handles, labels = ax.get_legend_handles_labels()
    plt.legend(handles=handles, ncol=2, bbox_to_anchor=(0.75, 1.05), labels=labels, edgecolor='white', fontsize=10)
    plt.show()


if __name__ == '__main__':
    date = '2020-02-20'
    short_hold, long_hold = get_data_via_date_from_excel(date)
    draw_lollipop_graph(short_hold, long_hold, date)
