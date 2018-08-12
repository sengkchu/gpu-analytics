import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import flask
import plotly.graph_objs as go
import os
from random import randint

import time
import pandas as pd
import numpy as np
import sqlite3


#Application object
server = flask.Flask(__name__)
server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))

app = dash.Dash(__name__, server=server)
app.title ='GPU Analytics'


#CSS and Javascript
external_css = ["https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css"]
for css in external_css:
    app.css.append_css({"external_url": css})

external_js = ['https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js']
for js in external_js:
    app.scripts.append_script({'external_url': js})


#Load in data:
import os
DB = "gpudata.db"

def run_query(q):
    with sqlite3.connect('/appdata/'+DB) as conn:
        return pd.read_sql(q,conn)

#Load chipsets ids/names into memory (chipsets without price history/benchmarks are excluded) for input1
chipsets_query = '''
SELECT 
    s.chipset_id,
    c.chipset_name
FROM card_specs s
INNER JOIN card_prices p ON s.card_id = p.card_id
INNER JOIN chipsets c ON c.chipset_id = s.chipset_id
INNER JOIN benchmarks b ON b.chipset_id = c.chipset_id
'''
chipsets = run_query(chipsets_query).drop_duplicates().sort_values('chipset_id')

#Load chipset prices into memory	
prices_query = '''
SELECT 
    s.chipset_id,
    c.chipset_name,
	s.manufacturer,
    p.datetime,
	p.merchant_id,
	m.merchant_name,
    p.price
FROM card_specs s
INNER JOIN card_prices p ON s.card_id = p.card_id
INNER JOIN chipsets c ON c.chipset_id = s.chipset_id
INNER JOIN merchants m ON p.merchant_id = m.merchant_id
'''
prices = run_query(prices_query)
prices['datetime'] = prices['datetime'].apply(lambda x: time.strftime('%Y-%m-%d', time.localtime(x))) 

#Load chipset benchmarks into memory
benchmarks_query = '''
SELECT
    c.chipset_id,
    c.chipset_name,
    b.passmark_g3d,
    b.passmark_direct_compute
FROM chipsets c
INNER JOIN benchmarks b ON b.chipset_id = c.chipset_id

'''
benchmarks = run_query(benchmarks_query)

#Load chipset specs into memory
specs_query = '''
SELECT
    c.chipset_id,
    c.chipset_name,
    s.memory_in_GB,
    s.memory_type,
    s.tdp_in_watts,	
    s.core_clock_in_GHz
FROM chipsets c
INNER JOIN card_specs s ON s.chipset_id = c.chipset_id

'''
specs = run_query(specs_query)

#Load merchant data into memory
merchants_query = '''
SELECT
    c.chipset_id,
    c.chipset_name,
    s.manufacturer,
    p.price,
    p.datetime,
    m.merchant_id,
    m.merchant_name
FROM chipsets c
INNER JOIN card_specs s ON s.chipset_id = c.chipset_id
INNER JOIN card_prices p on p.card_id = s.card_id
INNER JOIN merchants m on m.merchant_id = p.merchant_id
'''
merchants_df = run_query(merchants_query)
merchants_df['datetime'] = merchants_df['datetime'].apply(lambda x: time.strftime('%Y-%m-%d', time.localtime(x))) 

# App Layouts
app.config.suppress_callback_exceptions = True
    
def get_menu():
    menu = html.Div(
        className='col-lg-2 p-3 mb-2 bg-light text-dark text-center', 
        children=[
            html.Div(
                children=[            
                    dcc.Markdown('### GPU Analytics'),
                    dcc.Markdown('''---''')
                ]
            ),
            html.Div(
                className='btn-group-vertical', 
                children=[
                    dcc.Link('Overview', href='/overview', className = 'btn btn-light'),
                    dcc.Link('Merchant Comparison', href='/merchant-comparison', className = 'btn btn-light'),
                    dcc.Link('Brand Comparison', href='/brand-comparison', className = 'btn btn-light')
                ]
            )
        ]
    )
    return menu
    
# Page layouts
overview = html.Div(
    className='container-fluid',  
    children=[  
        html.Div(
		    className='row', 
            children=[
            
                #Overview - Plot Dashboard                          
                get_menu(),
    
                #Overview - Plot Elements     
                html.Div(
                    className='col-lg-10 p-3 mb-2 bg-white text-dark',
                    children=[  
                    
                        #Overview - Header
                        html.Div(
                            children=[
                            dcc.Markdown('''## __Overview__''', className='text-center'),
                            dcc.Markdown('''Use the drop-down menu below to add or remove GPU from the plots.
                         Use the cursor to interact with the plot. Double-click on the plot to return to default view.'''),                             
                            html.B('''Select or type in GPU(s):'''),                          
                        ]),
                        
                        #Overview - Top Menus
                        html.Div(
                            className='row',
                            children=[
                                html.Div(dcc.Dropdown(
                                    id='input1',
                                    options=[{'label': s[0], 'value': s[1]} for s in zip(chipsets.chipset_name, chipsets.chipset_id)							   
							         ],
                                    value=[1, 7, 2, 4, 8, 13, 14],
                                    multi= True
                                ), className='col-lg-12'),
                                                                
                            ]
                        ),
                        
                        #Overview - Section 1 graphs
                        html.Div(
                            className='row',
                            children=[
                                html.Div(dcc.Graph(id='update_gpu_history'), className='col-lg-12')
                            ]
                        ),
                        
                        #Overview - Section 2 graphs
                        html.Div(
                            className='row col-lg-12',
                            children=[
                                html.Div(dcc.Graph(id='update_gpu_g3d', style={'height': '50vh'}), className='col-lg-8'),   
                                html.Div(dcc.Graph(id='update_gpu_direct_compute', style={'height': '50vh'}), className='col-lg-4')  
                            ]
                        ), 
                        
                        #Overview - Section 3 graphs
                        html.Div(
                            className='row',
                            children=[
                                html.Div(dcc.Graph(id='update_gpu_table'), className='col-lg-12'),
                                html.Div(dcc.Graph(id='update_gpu_price_performance_hist'), className='col-lg-8'),                       
                                html.Div(dcc.Graph(id='update_gpu_price_performance'), className='col-lg-4')
                            ]
                        ),
                        
                        #Overview - Footer
                        html.Div(
                            className='row',
                            children=[
                                html.Div(dcc.Markdown('''Data Source: [PCPartPicker](https://pcpartpicker.com/) 
                                    and [PassMark](https://www.videocardbenchmark.net/)'''), className='col-lg-12'),
                                html.Div(dcc.Markdown('''My GitHub Repo: 
                                    [GPU Analytics](https://github.com/sengkchu/gpu-analytics)'''), className='col-lg-12'),                                    
                            ]
                        ),                     
                    ]
                )                   
			]
        )
    ]
) 

merchants = html.Div(
    className='container-fluid',  
    children=[  
        html.Div(
		    className='row', 
            children=[
            
                #Merchants - Plot dashboard                          
                get_menu(),
    
                #Merchants - Plot elements     
                html.Div(
                    className='col-lg-10 p-3 mb-2 bg-white text-dark',
                    children=[
                    
                        #Merchants - Header
                        html.Div(
                            children=[
                            dcc.Markdown('''## __Merchant Comparison__''', className='text-center'),                       
                            html.B('''Select or type in GPU:'''),                          
                        ]),
                        
                        #Merchants - Top Menus
                        html.Div(
                            className='row',
                            children=[
                                html.Div(dcc.Dropdown(
                                    id='input2',
                                    options=[{'label': s[0], 'value': s[1]} for s in zip(chipsets.chipset_name, chipsets.chipset_id)							   
							         ],
                                    value=1,
                                    multi= False
                                ), className='col-lg-12'),
                            ]
                        ),
                        
                        #Merchants - Section 1 graphs
                        html.Div(
                            className='row',
                            children=[
                                html.Div(dcc.Graph(id='update_merchant_prices'), className='col-lg-12')     
                            ]
                        ),

                        #Merchants - Description
                        html.Div(
                            className='row',
                            children=[
                                html.Div(dcc.Markdown('''__Click on the legend above to isolate trace(s), 
                                    use the cursor or slider to zoom in, double click to zoom out__'''), className='col-lg-12 text-center')
                            ]
                        ),
                        
                        #Merchants - Footer
                        html.Div(
                            className='row',
                            children=[
                                html.Div(dcc.Markdown('''Data Source: [PCPartPicker](https://pcpartpicker.com/) 
                                    and [PassMark](https://www.videocardbenchmark.net/)'''), className='col-lg-12'),
                                html.Div(dcc.Markdown('''My GitHub Repo: 
                                    [GPU Analytics](https://github.com/sengkchu/gpu-analytics)'''), className='col-lg-12'),                                    
                            ]
                        ),                          
                    ]
                )                   
			]
        )
    ]
) 

brands = html.Div(
    className='container-fluid',  
    children=[  
        html.Div(
		    className='row', 
            children=[
            
                #Brands - Plot dashboard                          
                get_menu(),
    
                #Brands - Plot elements     
                html.Div(
                    className='col-lg-10 p-3 mb-2 bg-white text-dark',
                    children=[
                    
                        #Brands - Header
                        html.Div(
                            children=[
                            dcc.Markdown('''## __Brand Comparison__''', className='text-center'),                       
                            html.B('''Select or type in GPU:'''),                          
                        ]),
                        
                        #Brands - Top Menus
                        html.Div(
                            className='row',
                            children=[
                                html.Div(dcc.Dropdown(
                                    id='input3',
                                    options=[{'label': s[0], 'value': s[1]} for s in zip(chipsets.chipset_name, chipsets.chipset_id)							   
							         ],
                                    value=1,
                                    multi= False
                                ), className='col-lg-12'),
                            ]
                        ),
                        
                        #Brands - Section 1 graphs
                        html.Div(
                            className='row',
                            children=[
                                html.Div(dcc.Graph(id='update_brand_prices'), className='col-lg-12')     
                            ]
                        ),

                        #Brands - Description
                        html.Div(
                            className='row',
                            children=[
                                html.Div(dcc.Markdown('''__Click on the legend above to isolate trace(s), 
                                    use the cursor or slider to zoom in, double click to zoom out__'''), className='col-lg-12 text-center')
                            ]
                        ),
                        
                        #Brands - Footer
                        html.Div(
                            className='row',
                            children=[
                                html.Div(dcc.Markdown('''Data Source: [PCPartPicker](https://pcpartpicker.com/) 
                                    and [PassMark](https://www.videocardbenchmark.net/)'''), className='col-lg-12'),
                                html.Div(dcc.Markdown('''My GitHub Repo: 
                                    [GPU Analytics](https://github.com/sengkchu/gpu-analytics)'''), className='col-lg-12'),                                    
                            ]
                        ), 
                    ]
                ),  
			]
        )
    ]
) 	

noPage = html.Div([  # 404

    html.P(["404 Page not found"])

    ])
	

# Describe the layout, or the UI, of the app
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])
		

@app.callback(
    Output(component_id='update_gpu_history', component_property='figure'),
    [Input(component_id='input1', component_property='value')]
)
def update_gpu_history(input1_values):

    #Filter data based on inputs    
    plots = {}
    for input_value in input1_values:
        df_filtered = prices[prices['chipset_id'] == input_value]
        name_1 = df_filtered['chipset_name'].values[0]
        data_1 = df_filtered.groupby(['datetime'])['price'].mean()		   
        plots[str(input_value)] = go.Scatter(name = str(name_1), x=data_1.index, y=data_1.values, \
            opacity=0.7, hoverinfo="x+y+name")

	#Plot itself
    return {
            'data':[trace for key, trace in plots.items()],
            'layout': {
                'yaxis': {'title':'Average Price (USD)'},
                'title': '<br>Price History<br>',
                'legend': {'orientation':'h'},
                'hoverlabel': {'namelength': 30},
                'margin': {'r': 20, 'pad': 5}
            }
    }           

    
@app.callback(
    Output(component_id='update_gpu_g3d', component_property='figure'),
    [Input(component_id='input1', component_property='value')]
)          
def update_gpu_g3d(input1_values):        
    plots = {}  
    xs = []
    names_len = []
    for input_value in input1_values:
        df_filtered = benchmarks[benchmarks['chipset_id'] == input_value]
        y = df_filtered['chipset_name'].values[0]
        x = df_filtered['passmark_g3d'].mode().values[0]
        xs.append(x)
        names_len.append(len(y))
        plots[str(input_value)] = go.Bar(x=[x], y=[y], text='<b>{}</b>'.format(x), opacity = 0.7, \
			textposition='outside', hoverinfo='none', orientation = 'h', cliponaxis = False)
	
	
    #Plot itself
    return {
            'data':[trace for key, trace in plots.items()],
            'layout': {
                'xaxis': {'title':'', 'range':[0, max(xs)*1.15], 'showticklabels':False, 'showgrid':False},
                'title': 'Passmark: G3D Score',
				'showlegend': False,
                'margin' : {'l' : 9*max(names_len), 'r':40, 'pad': 5, 'b': 10}
            }
    }
	
    
@app.callback(
    Output(component_id='update_gpu_direct_compute', component_property='figure'),
    [Input(component_id='input1', component_property='value')]
)  	
def update_gpu_direct_compute(input1_values):        
    plots = {}  
    xs = []
    names_len = []
    for input_value in input1_values:
        df_filtered = benchmarks[benchmarks['chipset_id'] == input_value]
        y = df_filtered['chipset_name'].values[0]
        x = df_filtered['passmark_direct_compute'].mode().values[0]
        xs.append(x)
        names_len.append(len(y))
        plots[str(input_value)] = go.Bar(x=[x], y=[y], text='<b>{}</b>'.format(x), opacity = 0.7, \
			textposition='outside', hoverinfo='none', orientation = 'h', cliponaxis = False)
	
	
    #Plot itself
    return {
            'data':[trace for key, trace in plots.items()],
            'layout': {
                'xaxis': {'title':'', 'range':[0, max(xs)*1.15], 'showticklabels':False, 'showgrid':False},
                'title': 'Passmark: Direct Compute<br>(Operations per second)',
				'showlegend': False,
                'yaxis': {'showticklabels':False},
                'margin' : {'l' : 2, 'r':40, 'pad': 5, 'b': 10}
            }
    }

	
@app.callback(
    Output(component_id='update_gpu_table', component_property='figure'),
    [Input(component_id='input1', component_property='value')]
)        
def update_gpu_table(input1_values):        
    plots = {}
    name = []
    memory = []
    memory_type = []
    tdp = []
    avg_core_clock = []
    for input_value in input1_values:
        df_filtered = specs[specs['chipset_id'] == input_value]	
        name.append(df_filtered['chipset_name'].values[0])
        memory.append(df_filtered['memory_in_GB'].mode().values[0])
        memory_type.append(df_filtered['memory_type'].mode().values[0])
        tdp.append(df_filtered['tdp_in_watts'].mode().values[0])
        avg_core_clock.append(np.round(df_filtered['core_clock_in_GHz'].mean(), 2))
    
    odd = 'lightgrey'
    even = 'white'
    trace = go.Table(
        header = dict(
            values = [
                  ['<b>Chipset Name</b>'],
                  ['<b>Memory (GB)</b>'],
                  ['<b>Memory Type</b>'],
                  ['<b>Typical TDP (Watts)</b>'],
                  ['<b>Typical Clock Speed(GHz)</b>']
            ],
            line = dict(color = '#ffffff', width = 1),
            fill = dict(color = '#000000'),
            align = ['center'],
            font = dict(color = 'white', size = 14)
        ),       
        cells = dict(
            values = [name, memory, memory_type, tdp, avg_core_clock],
            line = dict(color = '#ffffff', width = 1),
            align = ['left', 'center'],
            fill = dict(color = [[even if idx%2==0 else odd for idx, i in enumerate(input1_values)]]),
            font = dict(color = '#000000', size = 12)
        ),
        columnwidth = [0.4, 0.15, 0.15, 0.15, 0.15]
    )  
    #Plot itself
    return {
            'data':[trace],
            'layout': {
                'title': '<br>Specs<br>',
                'margin': {'b': 0, 'l': 20, 'r': 20}
            }
    }    
    
    
@app.callback(
    Output(component_id='update_gpu_price_performance', component_property='figure'),
    [Input(component_id='input1', component_property='value')]
)          
def update_gpu_price_performance(input1_values):        
    plots = {} 
    names_len = []
    for input_value in input1_values:
        df_filtered = benchmarks[benchmarks['chipset_id'] == input_value]
        x = df_filtered['chipset_name'].values[0]
        names_len.append(len(x))
        
        current_price = prices[prices['chipset_id'] == input_value].groupby(['datetime'])['price'].mean()[-1]
        y = np.round(df_filtered['passmark_direct_compute'].values[0]/current_price, 2)	      
        plots[str(input_value)] = go.Bar(x=[x], y=[y], text=[y], \
			textfont={'color':'#ffffff'}, textposition='auto', hoverinfo="x+y", \
            cliponaxis = False, opacity = 0.7)
    
    #Plot itself
    return {
            'data':[trace for key, trace in plots.items()],
            'layout': {
                'yaxis': {'title' : 'Operations per second / USD', 'showticklabels' : False},
				'xaxis': {'showticklabels' : False},
                'title': 'Current Price Performance',
				'showlegend' : False,
                'margin': {'l': 40, 'r': 20, 'pad': 5}
            }
    }      
	
	
@app.callback(
    Output(component_id='update_gpu_price_performance_hist', component_property='figure'),
    [Input(component_id='input1', component_property='value')]
) 
def update_gpu_price_performance_hist(input1_values):

    #Filter data based on inputs    
    plots = {}
    for input_value in input1_values:
        df_filtered_1 = prices[prices['chipset_id'] == input_value]
        df_filtered_2 = benchmarks[benchmarks['chipset_id'] == input_value]
        compute_score = df_filtered_2['passmark_direct_compute'].values[0]
        name_1 = df_filtered_1['chipset_name'].values[0]       
        data_1 = compute_score/df_filtered_1.groupby(['datetime'])['price'].mean()
        
        plots[str(input_value)] = go.Scatter(name = str(name_1), x=data_1.index, y=data_1.values, \
            opacity=0.7, hoverinfo="x+y+name")

	#Plot itself
    return {
            'data':[trace for key, trace in plots.items()],
            'layout': {
                'yaxis': {'title':'Operations per second / USD'},
                'title': 'Price Performance History',
                'legend': {'orientation':'h'},
                'hoverlabel': {'namelength': 30},
                'margin' : {'r': 20}
            }
    }
	
	
@app.callback(
    Output(component_id='update_merchant_prices', component_property='figure'),
    [Input(component_id='input2', component_property='value')]
) 
def update_merchant_prices(input2_value):

    #Filter data based on inputs    
    plots = {}

    df_filtered_1 = merchants_df[merchants_df['chipset_id'] == input2_value]
    merchant_names = df_filtered_1['merchant_name'].unique()     
        
    for merchant_name in merchant_names: 
        df_filtered_2 = df_filtered_1[df_filtered_1['merchant_name'] == merchant_name]
        data_1 = df_filtered_2.groupby(['datetime'])['price'].mean()	
        plots[str(merchant_name)] = go.Scatter(name = str(merchant_name), x=data_1.index, y=data_1.values, \
            opacity=0.7, hoverinfo="x+y+name")

	#Plot itself
    return {
            'data':[trace for key, trace in plots.items()],
            'layout': {
                'yaxis': {'title':'Average Price (USD)'},
                'xaxis': {'rangeslider': {}, 'type':'date'},
                'legend': {'orientation':'h', 'y': -0.5},
                'hoverlabel': {'namelength': 30},
                'margin' : {'r': 40, 't': 40}
            }
    }
    
 
@app.callback(
    Output(component_id='update_brand_prices', component_property='figure'),
    [Input(component_id='input3', component_property='value')]
) 
def update_brand_prices(input3_value):

    #Filter data based on inputs    
    plots = {}

    df_filtered_1 = merchants_df[merchants_df['chipset_id'] == input3_value]
    brand_names = df_filtered_1['manufacturer'].unique()     
        
    for brand in brand_names: 
        df_filtered_2 = df_filtered_1[df_filtered_1['manufacturer'] == brand]
        data_1 = df_filtered_2.groupby(['datetime'])['price'].mean()	
        plots[str(brand)] = go.Scatter(name = str(brand), x=data_1.index, y=data_1.values, \
            opacity=0.7, hoverinfo="x+y+name")

	#Plot itself
    return {
            'data':[trace for key, trace in plots.items()],
            'layout': {
                'yaxis': {'title':'Average Price (USD)'},
                'xaxis': {'rangeslider': {}, 'type':'date'},
                'legend': {'orientation':'h', 'y':-0.5},
                'hoverlabel': {'namelength': 30},
                'margin' : {'r': 40, 't': 40}
            }
    } 
    
    
# Update page
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/' or pathname == '/overview':
        return overview
    elif pathname == '/merchant-comparison':
        return merchants
    elif pathname == '/brand-comparison':
        return brands
    else:
        return noPage    
			

server2 = app.server

if __name__ == '__main__':
	app.server.run(debug=True, threaded=True)
