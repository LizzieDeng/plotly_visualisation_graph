import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import plotly.offline as plt
import dash
import dash_html_components as html
import dash_core_components as dcc

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

excel_pd = pd.read_excel('data\IC期货商历史数据(1).xlsx', index_col='日期')
# 去空
excel_pd.dropna()
# 去除000905_SH列
excel_pd = excel_pd.drop(labels='000905_SH', axis=1)
# 去0行
excel_pd = excel_pd[~(excel_pd == 0).all(axis=1)]
# 取出时间列表，获取最大日期和最小日期，为日历选项做判断
date_list = excel_pd.index.values.tolist()
min_date = min(date_list)
max_date = max(date_list)


def get_data_via_date_from_excel(date):
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
    fig = go.Figure()
    # 空仓水平线
    short_shapes = [{'type': 'line',
                     'yref': 'y1',
                     'y0': k,
                     'y1': k,
                     'xref': 'x1',
                     'x0': 0,
                     'x1': i,
                     'layer': 'below',
                     'line': dict(
                         color="#1a68cc",
                     ),
                     } for i, k in zip(short_hold, range(len(short_hold)))]
    # 多仓水平线
    long_shapes = [{'type': 'line',
                    'yref': 'y1',
                    'y0': k,
                    'y1': k,
                    'xref': 'x1',
                    'x0': j,
                    'x1': 0,
                    'layer': 'below',
                    'line': dict(
                      color="red",
                     )
                    } for j, k in zip(long_hold, range(len(long_hold)))]
    # 画散点
    fig.add_trace(go.Scatter(
        x=short_hold,
        y=[i for i in range(len(short_hold))],
        mode='markers+text',
        marker=dict(color="#1a68cc", symbol='diamond-open'),
        text=[label + '(' + str(abs(i)) + ') ' for label, i in zip(short_hold.index, short_hold)],   # 散点两端的期货公司标注和持仓数
        textposition='middle left',  # 标注文字的位置
        showlegend=False             # 该轨迹不显示图例legend
    ))
    fig.add_trace(go.Scatter(
        x=long_hold,
        y=[i for i in range(len(long_hold))],
        mode='markers+text',
        text=[' ' + label + '(' + str(abs(i)) + ')' for label, i in zip(long_hold.index, long_hold)],  # 散点两端的期货公司标注和持仓数
        marker=dict(color='red', symbol='diamond-open'),
        textposition='middle right',  # 标注文字的位置
        showlegend=False              # 该轨迹不显示图例legend
    ))
    # 加上这条trace只是为了显示legend图例,因为上面的图例显示的text在plotly现有的版本基础上去除不了
    fig.add_trace(go.Scatter(
        x=[0, long_hold[0]],
        y=[range(len(long_hold))[0], range(len(long_hold))[0]],
        mode='lines',
        marker=dict(color='red'),
        name='多'
    ))
    fig.add_trace(go.Scatter(
        x=[0, short_hold[0]],
        y=[range(len(short_hold))[0], range(len(short_hold))[0]],
        mode='lines',
        marker=dict(color='#1a68cc'),
        name='空'
    ))
    # 线上的排名顺序
    fig.add_trace(go.Scatter(
        x=[0]*max(len(short_hold), len(long_hold)),
        y=[i for i in range(max(len(short_hold), len(long_hold)))],
        mode='text',
        text=[str(i+1) for i in range(max(len(short_hold), len(long_hold)))],  # 排名从1开始
        textfont=dict(color=['#b91818', '#e26012', '#dd9f10'] + ['#404040' for i in range(max(len(short_hold), len(long_hold)) - 3)],
                      size=[17, 16, 15] + [10 for i in range(max(len(short_hold), len(long_hold)) - 3)],
                      family="Open Sans"),
        textposition='top center',
        showlegend=False
    ))
    # X, Y坐标轴不可见
    fig.update_xaxes(
        showticklabels=False,
        showgrid=False,
        zeroline=False,
    )
    fig.update_yaxes(
        showticklabels=False,
        showgrid=False,
        zeroline=False,
        autorange='reversed'  # Y 轴倒置
    )
    fig.update_layout(shapes=short_shapes+long_shapes,  # 添加水平线
                      width=2100,
                      height=900,
                      legend=dict(x=0.62, y=1.02, orientation='h'),
                      template="plotly_white",
                      title=dict(text='黄金持仓龙虎榜单(' + date + ')', y=0.95, x=0.65, xanchor='center', yanchor='top',
                                 font=dict(family="Open Sans", size=30)))
    # fig.show()
    # plt.plot(fig, filename='Lollipop.html',  # 生成一个网页文件
    #          image='png', )
    return fig


def create_figure(date):
    # date = '2020-02-20'
    short_hold, long_hold = get_data_via_date_from_excel(date)
    return draw_lollipop_graph(short_hold, long_hold, date)


app.layout = html.Div([
    html.Div(dcc.DatePickerSingle(
        id='my-date-picker-single',
        min_date_allowed=min_date,  # 日历最小日期
        max_date_allowed=max_date,  # 日历最大日期
        date=max_date   # dash 程序初始化日历的默认值日期
    ), style={"margin-left": "300px"}),
    html.Div(id='output-container-date-picker-single', style={"text-align": "center"})
])


@app.callback(
    Output('output-container-date-picker-single', 'children'),
    [Input('my-date-picker-single', 'date')])
def update_output(date):
    print("date", date)
    if date is not None:
        if date not in date_list:
            return html.Div([
               "数据不存在"
            ])
        fig = create_figure(date)
        return html.Div([
            dcc.Graph(figure=fig)
        ])


if __name__ == '__main__':
    app.run_server(debug=True)
