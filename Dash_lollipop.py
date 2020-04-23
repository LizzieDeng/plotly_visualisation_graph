import pandas as pd
from datetime import datetime as dt
import plotly.graph_objects as go
import numpy as np
from dash.dependencies import Input, Output
import plotly.offline as plt
import dash
import dash_html_components as html
import dash_core_components as dcc

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash()
excel_pd = pd.read_excel('data\IC期货商历史数据(1).xlsx', index_col='日期')
excel_pd.dropna()  # 去空
excel_pd = excel_pd.drop(labels='000905_SH', axis=1)
# 去0
excel_pd = excel_pd[~(excel_pd==0).all(axis=1)]

date_list = excel_pd.index.values.tolist()
min_date = min(date_list)
max_date = max(date_list)
# print( )2013-04-10 2020-02-20


def get_data_via_date_from_excel(date):
    # 筛选日期
    sheet1_data = excel_pd.loc[date]
    # 去除0
    sheet1_data = sheet1_data[sheet1_data != 0]
    # 排序 从小到大
    sheet1_data = sheet1_data.sort_values()
    # print(sheet1_data.index.values.tolist())
    return sheet1_data


def draw_lollipop_graph(sheet1_data, date):
    # 负
    sheet_minor = sheet1_data[sheet1_data < 0]
    # 正
    sheet_major = sheet1_data[sheet1_data >= 0].sort_values(ascending=False)
    # columns
    minor_columns = sheet_minor.index.values.tolist()
    major_columns = sheet_major.index.values.tolist()
    minor = list(sheet_minor)
    major = list(sheet_major)
    # 使得负和正长度一样，不够补0
    if len(major) > len(minor):
        for i in range(len(major)-len(minor)):
            minor.append(0)
            minor_columns.append('empty')
    else:
        for i in range(len(minor)-len(major)):
            major.append(0)
            major_columns.append('empty')
    max_len = max(len(major), len(minor))
    index = [i for i in range(max_len)]
    index.reverse()
    list_a = []
    fig = go.Figure()
    for i, j, k, i_col, j_col in zip(minor, major, index, minor_columns, major_columns):
        dict_1 = {'type': 'line',
                  'yref': 'y1',
                  'y0': k,
                  'y1': k,
                  'xref': 'x1',
                  'x0': 0,
                  'x1': i,
                  'line': dict(
                        color="blue",
                    ),
                  'path': '红'
        }
        dict_2 = {'type': 'line',
                  'yref': 'y1',
                  'y0': k,
                  'y1': k,
                  'xref': 'x1',
                  'x0': j,
                  'x1': 0,
                  'line': dict(
                      color="red",
                  )
                  }
        list_a.append(dict_1)
        list_a.append(dict_2)
        fig.add_trace(go.Scatter(
            x=[0],
            y=[k],
            mode='text',
            text=[str(len(major) - k)],
            textposition='top center',
            showlegend=False
        ))
        if i_col != 'empty':
            fig.add_trace(go.Scatter(
                x=[i],
                y=[k],
                mode='markers+text',
                marker=dict(color='blue'),
                text=[i_col + '(' + str(abs(i)) + ')'],
                textposition='middle left',
                # legendgroup="group1",
                showlegend=False
            ))
            if k == len(index) - 1:
                fig.add_trace(go.Scatter(
                    x=[0, i],
                    y=[k, k],
                    mode='lines',
                    marker=dict(color='blue'),
                    name='空'
                ))
        if j_col != 'empty':
            fig.add_trace(go.Scatter(
                x=[j],
                y=[k],
                mode='markers+text',
                marker=dict(color='red'),
                text=[j_col + '(' + str(j) + ')'],
                textposition='middle right',
                showlegend=False,
            ))
            if k == len(index) - 1:
                fig.add_trace(go.Scatter(
                    x=[0, j],
                    y=[k, k],
                    mode='lines',
                    marker=dict(color='red'),
                    name='多'
                ))
    fig.update_xaxes(
        showticklabels=False,
        showgrid=False,
        zeroline=False,
    )
    fig.update_yaxes(
        showticklabels=False,
        showgrid=False,
        zeroline=False,
    )
    fig.update_layout(shapes=list_a,
                      width=2000,
                      height=900,
                      legend=dict(x=0.5, y=1, orientation='h'),
                      template="plotly_white",
                      title=dict(text='黄金持仓龙虎榜单(' + date + ')', y=0.95, x=0.5, xanchor='center', yanchor='top',
                                 font=dict(family="Open Sans", size=30)))
    # fig.show()
    # plt.plot(fig, filename='Lollipop.html',  # 生成一个网页文件
    #          image='png', )
    return fig


def create_figure(date):
    # date = '2020-02-20'
    data = get_data_via_date_from_excel(date)
    return draw_lollipop_graph(data, date)


app.layout = html.Div([
    dcc.DatePickerSingle(
        id='my-date-picker-single',
        min_date_allowed=min_date,
        max_date_allowed=max_date,
        initial_visible_month=max_date,
        date=max_date
    ),
    html.Div(id='output-container-date-picker-single')
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


