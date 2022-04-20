import os
import json
import requests
import geopandas as gpd

import numpy as np
import pandas as pd
import plotly.express as px
from dash import Dash, dash_table, dcc, html, Input, Output
import dash_bootstrap_components as dbc

from .util_wcloud import *



def read_geojson():
    
    # if not os.path.exists("./src/data/geodata.json"):
    #     url = "https://geo.datav.aliyun.com/areas_v3/bound/310000_full.json"
    #     response = requests.get(url)
    #     versionInfo = response.text
    #     versionInfoPython = json.loads(versionInfo)
    #     with open("./src/data/geodata.json", "w") as out_file:
    #         json.dump(versionInfoPython, out_file, indent = 4)
            
    # else:   
    with open("./src/data/geodata.json", "r") as read_file:
        versionInfoPython = json.load(read_file)
    
    return versionInfoPython

def clean(data):
    
    area_list = [i["properties"]["name"] for i in versionInfoPython["features"]]
    mapper = {"浦东区":"浦东新区", "闸北区区":"闸北区"}
    data["county"] = data["county"].replace(mapper)
    data = data.loc[data["county"].isin(area_list)].reset_index(drop=True)
    data.dropna(subset=["createdAt"], inplace=True)
    
    return data
    
def preprocess(data):

    data["date"] = pd.to_datetime(data["createdAt"])
    # data = data[["createdAt", "date", "county", "helpLevel", "type"]]
    for col in ["helpLevel", "type"]:
        for val in pd.unique(data[col]):
            data[col+"_"+val] = data[col].apply(lambda x: 1 if x==val else 0)

    data = data[[x for x in data if x not in ["helpLevel", "type"]]]
    data["total"] = 1    

    return data


data = pd.read_excel("./src/helpothers.xlsx")
versionInfoPython = read_geojson()
data = clean(data)
data_af = preprocess(data)
column_show = ['createdAt', 'county', 'helpLevel', 'type', 'tags', 'contentText']
data = data[column_show]


app = Dash(__name__)

server = app.server

app.layout = html.Div([
    html.H4('上海各区疫情求助数据:'),
    html.P("求助等级:"),
    dcc.RadioItems(
        id='helplevel', 
        options=[{"label":i.split("_")[1], "value":i} for i in ['helpLevel_极紧急', 'helpLevel_紧急', 'helpLevel_较急', 'helpLevel_全部']],
        value="helpLevel_全部",
    ),
    html.P("求助类型:"),
    dcc.RadioItems(
        id='typelevel', 
        options=[{"label":i.split("_")[1], "value":i} for i in ['type_重病', 'type_疾病', 'type_物资', 'type_孕妇', 'type_其它', 'type_全部']],
        value="type_全部",
    ),

    html.Br(),

    dbc.Col([
        dcc.Loading(dcc.Graph(id="graph"), type="cube")
    ], width=4),
    
    html.Br(),
    html.Br(),
    html.Br(),
    
    dbc.Col(
        [
            dbc.Container(
                dbc.Row([
                    dbc.Col([
                        dash_table.DataTable(
                            id='table',
                            columns=[{"name": col, "id": col, 'selectable': True} for col in column_show], 
                            data=data.to_dict('records'),
                            style_cell={'padding': '5px',
                                        'overflow': 'hidden',
                                        'textOverflow': 'ellipsis',
                                        'maxWidth': 0,},
                            style_cell_conditional=[
                                {'if': {'column_id': 'createdAt'},
                                'width': '10%'},
                                {'if': {'column_id': 'county'},
                                'width': '10%'},
                                {'if': {'column_id': 'helpLevel'},
                                'width': '10%'},
                                {'if': {'column_id': 'type'},
                                'width': '10%'},
                                {'if': {'column_id': 'tags'},
                                'width': '10%'},
                                ],
                            sort_action="native",
                            page_action='native',
                            column_selectable="multi",
                            selected_columns=['createdAt', 'county', 'helpLevel', 'type', "tags"], 
                            page_size= 10,
                            filter_action='native',
                            style_data={'whiteSpace': "normal", "height": "auto"}, 
                            style_data_conditional=[{
                                'if': {'row_index': 'odd'},
                                'backgroundColor': 'rgb(248, 248, 248)'}],
                            style_header={
                                'backgroundColor': 'rgb(230, 230, 230)',
                                'fontWeight': 'bold'}),
                    ], width=4),
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody(
                                    dcc.Loading(dcc.Graph(id="trend", style={'overflow-x': 'scroll'}), type="cube"))])
                            ]),
                    ]),
                    
                    

                ])
            ),
            
        ]
    )

])


@app.callback(
    Output("graph", "figure"),
    [
        Input("helplevel", "value"), 
        Input("typelevel", "value"),
    ]
    )
def display_choropleth(helplevel, typelevel):
    
    latitude = 31.2
    longitude = 121.5

    source = data_af.copy()
        
    if helplevel != "helpLevel_全部":
        source = source[source[helplevel] == 1]
    if typelevel != "type_全部":
        source = source[source[typelevel] == 1]
        
    data_merge = pd.DataFrame([], index = pd.MultiIndex.from_product([set(source["county"]),set(source["date"])],
                                                                 names=["county", "date"])).reset_index()
    
    source = pd.merge(data_merge, source, how='left').fillna(0)   
    source = source.groupby("county").resample('12H', on='date').sum().groupby("county").cumsum().reset_index()
    source["date"] = source["date"].astype(str)


    
    fig = px.choropleth_mapbox(
        data_frame=source,
        geojson=versionInfoPython,
        color=np.log2(source["total"] + 1),
        locations="county",
        featureidkey="properties.name",
        mapbox_style="white-bg",
        animation_frame="date",
        color_continuous_scale='viridis',
        center={"lat": latitude, "lon": longitude},
        zoom=7.8,
        width=1000,
        height=600,
        range_color=[5, np.log2(source["total"]).max()],
        opacity=0.65,
        # labels={candidate: candidate},
        hover_name="county",
        hover_data={"date": True, 'county':False, "total": ':.0f'}
    )


    fig.update_layout(
        clickmode = 'event+select',
        margin={"r":0,"t":0,"l":0,"b":0},
        title={'x':0.5,'xanchor':'center','font':{'size':20}},
        xaxis=dict(title=dict(font=dict(size=20))),
        yaxis={'title':{'text':None}},
        legend={'font':{'size':18},'title':{'font':{'size':18}}},
        coloraxis_colorbar=dict(
            title="total",
            tickvals=list(range(5, 13)),
            ticktext=[str(2**i) for i in range(5, 13)])
        )
    
    
    fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 100
    fig.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 80
        
    return fig


@app.callback(
    Output('table', 'data'),
    [
        Input("helplevel", "value"), 
        Input("typelevel", "value"),
    ]
    )

def display_table(helplevel, typelevel):
    
    rst = data.copy()
    if helplevel != "helpLevel_全部":
        rst = data[data[helplevel.split("_")[0]] == helplevel.split("_")[1]]
    if typelevel != "type_全部":
        rst = rst[rst[typelevel.split("_")[0]] == typelevel.split("_")[1]]
    
    # print(rst.columns)
    return rst.to_dict('records')


@app.callback(
    Output('trend', "figure"),
    Input('table', "derived_virtual_data"),
    Input('table', "selected_columns"))
def update_histogram(rows_dict, selected_columns):
    
    rows = pd.DataFrame(rows_dict).copy()        
    rows["createdAt"] = pd.to_datetime(rows["createdAt"])
    rows["数量"] = 1
    # fig = px.area(rows.resample("15T", on="createdAt").aggregate({"数量":'count'})["数量"], title="每15分钟求救人数")
    
    from plotly import subplots
    import plotly.graph_objects as go


    trend_df = rows.resample("15T", on="createdAt").aggregate({"数量":'count'})
    trend = go.Scatter(x=list(trend_df.index), y=trend_df["数量"], fill='tozeroy')

    dist_area = go.Histogram(x=rows["county"])
    dist_level = go.Histogram(x=rows["helpLevel"])

    fig = subplots.make_subplots(rows=3, cols=3, 
                                subplot_titles=('每15分钟求救人数', '行政区分布', '紧急程度分布','词云分析'),
                                specs=[[{"rowspan": 1, "colspan": 1}, {"rowspan": 1, "colspan": 1}, {"rowspan": 1, "colspan": 1},],
                                        [ {"rowspan": 2, "colspan": 3}, None, None,],
                                        [ None, None, None,]],

                                )

    # text = ",".join(list(rows["tags"]))

    text = ",".join([str(x) for x in list(rows["tags"]) if x])
    wordcloud = plotly_wordcloud(text)

    fig.add_trace(trend,1,1)
    fig.add_trace(dist_area,1,2)
    fig.add_trace(dist_level,1,3)
    fig.add_trace(wordcloud,2,1)
    fig.update_layout(height=700)

    return fig

# @app.callback(
#     Output('scatter', "srcDoc"),
#     Input('table', "derived_virtual_data"),
#     Input('table', "selected_columns"))
# def update_scatter(rows, selected_column):
#     chart2 = alt.Chart(pd.DataFrame(rows)).mark_point().encode(
#         alt.X(selected_column[0]),
#         alt.Y('Horsepower'),
#         tooltip='Name')
#     return chart2.properties(width=320, height=320).to_html()
if __name__ == '__main__':
    
    app.run_server(debug=False)