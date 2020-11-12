import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output, State
import plotly.express as px
import dash_table
import dash_bootstrap_components as dbc

from conversion import klass_conversion
from data_retrival import fetch_data

app = dash.Dash(__name__,
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5,'}]
                            )
app.title = 'Землетрясения в Прибайкалье'
server = app.server
# ------------------------------------------------------------------------------
# data 
df = fetch_data()

last_earthquake = df.head(1).values.tolist()
l_date, l_time, l_lon, l_lat, l_m = tuple(last_earthquake[0])
# ------------------------------------------------------------------------------
# App layout
app.layout = dbc.Container([

    html.Br(),
    dbc.Row([
            dbc.Col(dbc.Button("Инструкция", id="open", color="info"),
                        xs=10, sm=5, md=5, lg=4, xl=4
                    ),
            dbc.Col(html.H3("Землетрясения в Прибайкалье"),
                        xs=10, sm=5, md=5, lg=8, xl=8
                    ),
            ]),
    dbc.Modal([
            dbc.ModalHeader("Как пользоваться этим приложением?"),
            dbc.ModalBody([
                        html.Span("На этой странице представлены данные о землетрясениях в Байкальском регионе. Все данные получены с "),
                        html.A("сайта БФ ФИЦ ЕГС РАН", href="http://seis-bykl.ru", target='_blank'),
                        html.Br(),
                        html.A("Сообщить о проблеме", href="https://github.com/rishm069/earthquakes38", target='_blank'),
                        html.Br(),
                        dbc.ListGroup([
                                    dbc.ListGroupItem([
                                                    dbc.ListGroupItemHeading("Селектор"),
                                                    dbc.ListGroupItemText("Селектор позволяет выбрать отображение на карте всех землетрясений за текущий год ('Землетрясения за текущий год'), только последнего землетрясения ('Последнее землетрясение') или все землетрясения с 1994 года ('Исторические данные')"),
                                                    ]
                                                    ),
                                    dbc.ListGroupItem([
                                                    dbc.ListGroupItemHeading("Таблица"),
                                                    dbc.ListGroupItemText("Таблица позволяет выбирать землетрясения для отображения на карте: по умолчанию отображаются все землетрясения, при выборе одного и более землетрясений на карте будут отмечены только эти землятресения. Данные можно сортировать и фильтровать с помощью таблицы, например:"),
                                                    dbc.ListGroupItemText("'-09-' в столбце 'Дата' покажет только данные за Сентябрь"),
                                                    html.Img(style={'height':'100%', 'width':'100%'}, src='https://drive.google.com/uc?id=1ZQk2IKkEiJcGFbgMgyge64mXN7FOKjFH'),
                                                    dbc.ListGroupItemText("'>5' в столбце 'Магнитуда' покажет только землетрясения силой более 5 баллов"),
                                                    html.Img(style={'height':'100%', 'width':'100%'}, src='https://drive.google.com/uc?id=1O8aJXNgRF3co2Cq9FVrPUAxa6YXJuwan'),
                                                    ]
                                                    ),
                        dbc.ListGroupItem([
                                        dbc.ListGroupItemHeading("Карта"),
                                        dbc.ListGroupItemText("Карта отображает отфильтрованные селектором и таблицей события, либо все сразу (по-умолчанию)"),
                                        html.Img(style={'height':'100%', 'width':'100%'}, src='https://drive.google.com/uc?id=17outz8jEb4ya7qa-Tzv8aTvtdJ6Chgew'),
                                        ]
                                        ),
                                    ]
                                    )        
                        ]),
            dbc.ModalFooter(
                        dbc.Button("Закрыть", id="close", className="ml-auto", color="danger")
                        ),
            ],
            id="modal", size="lg",
        ),
    dbc.Alert([
                html.H4("Данные о последнем землетрясении", className="alert-heading"),
                html.Hr(),
                html.Span(f"Дата и время (GMT +8, Иркутск): {l_date} {l_time}"),
                html.Br(),
                html.Span("Координаты: "),
                html.A(f"{l_lon} {l_lat}", href=f"https://www.google.com/maps/place/{l_lon},{l_lat}", target='_blank', id='map_link'),
                html.Br(),
                html.Span(f"Магнитуда: {l_m}"),
                dbc.Tooltip(
                     "Открыть на Google Maps",
                     target="map_link",
                     placement='right'
                    )    
                ], color="warning", dismissable=True),
    html.Div([
    dcc.Dropdown(
        id='dropdown',
        options=[
            {'label': 'Землетрясения за текущий год', 'value': 'current'},
            {'label': 'Последнее землетрясение', 'value': 'latest'},
            {'label': 'Исторические данные', 'value': 'history'}
        ],
        value='current'
    ),
    html.Div(id='dd-output-container')
    ]),
    html.Br(),
    html.Br(),
    html.Div(id='data_table-container'),
    html.Br(),
    html.Br(),
    dbc.Spinner(children=[html.Div(id='scatter_mapbox-container')], size="lg", color="primary", type="border", fullscreen=False),
    html.A("Все данные получены с сайта БФ ФИЦ ЕГС РАН", href="http://seis-bykl.ru", target='_blank', style={'text-align': 'center'})
    ])

# ------------------------------------------------------------------------------
# Callbacks
@app.callback(
    Output("modal", "is_open"),
    [Input("open", "n_clicks"), Input("close", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@app.callback(
    Output(component_id='data_table-container', component_property='children'),
    [Input(component_id='dropdown', component_property='value')]
)
def update_data_table(dropdown):
    dff = df
    if dropdown == 'latest':
        dff = df.head(1)
    if dropdown == 'history':
        dfh = pd.read_csv(r'historical_data.csv')
        dfh = dfh.append(df)
        dfh.drop_duplicates(keep="first", inplace=True)
        dfh.to_csv(r'historical_data.csv', index=False)
        dff = dfh
    return [
        dash_table.DataTable(
        id='datatable-interactivity',
        style_header={'textOverflow': 'ellipsis'},
        style_cell={
            'whiteSpace': 'normal',
            'height': 'auto',
            'textAlign': 'left'
        },
        columns=[ {"name": i, "id": i, "selectable": False} for i in df.columns],
        data=dff.to_dict('records'),
        filter_action="native",     
        sort_action="native",       
        sort_mode="single",         
        row_selectable="multi",     
        page_action="native",       
        page_current=0,             
        page_size=6,
        )
    ]


@app.callback(
    Output(component_id='scatter_mapbox-container', component_property='children'),
    [Input(component_id='datatable-interactivity', component_property="derived_virtual_data"),
     Input(component_id='datatable-interactivity', component_property='derived_virtual_selected_rows'),
     Input(component_id='dropdown', component_property='value')]
)
def update_map(all_rows_data, slctd_row_indices, dropdown_input):

    if len(slctd_row_indices) == 0:
        dff = pd.DataFrame(all_rows_data)
        dff.drop_duplicates(keep="first", inplace=True)
    else:
        sl_list = [all_rows_data[n] for n in slctd_row_indices]
        dff = pd.DataFrame(sl_list)

    return [
            dcc.Graph(id='choropleth', config={'displayModeBar': False, 'scrollZoom': True},
            figure = px.scatter_mapbox(
            dff, 
            lat=dff['Широта'], 
            lon=dff['Долгота'], 
            hover_data=['Дата', 'Время', 'Широта', 'Долгота', 'Магнитуда'],     
            color_continuous_scale=px.colors.sequential.Burg,
            color=dff['Магнитуда'],
            size=dff['Магнитуда'],
            size_max=15, 
            zoom=5,
            height=450).update_layout(mapbox_style="open-street-map", 
                                      coloraxis_showscale=True, 
                                      coloraxis_colorbar=dict(title=dict(text="M",font=dict(size=25, family="Droid Sans Mono")), thickness=20),
                                      autosize=True, 
                                      margin=dict(t=0, b=0, l=0, r=0)
                                      )
            )
            ]  
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=False)