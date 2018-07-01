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
DB = "gpudata.db"	
def run_query(q):
    with sqlite3.connect(DB) as conn:
        return pd.read_sql(q,conn)

#Load chipsets data into memory (chipsets without price history are excluded) for input1
chipsets_query = '''
SELECT 
    s.chipset_id,
    c.chipset_name
FROM card_specs s
INNER JOIN card_prices p ON s.card_id = p.card_id
INNER JOIN chipsets c ON c.chipset_id = s.chipset_id
'''
chipsets = run_query(chipsets_query).drop_duplicates().sort_values('chipset_id')

#Load chipsets prices into memory	
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

memory_query = '''
SELECT
    s.chipset_id,
    c.chipset_name,
    s.memory_in_GB
FROM card_specs s
INNER JOIN chipsets c ON c.chipset_id = s.chipset_id

'''
memory = run_query(memory_query)

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

manufacturers = prices['manufacturer'].drop_duplicates()
merchants = run_query('SELECT * FROM merchants')
specs = run_query('SELECT * FROM card_specs')



#App Layouts
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
    
## Page layouts
overview = html.Div(
    className='container-fluid',  
    children=[  
        html.Div(
		    className='row', 
            children=[
            
                #Plot dashboard                          
                get_menu(),
    
                #Plot elements     
                html.Div(
                    className='col-lg-10 p-3 mb-2 bg-white text-dark',
                    children=[  
                    
                        #Top Text
                        html.Div(
                            html.B('''Select or type in GPU(s):''')
                        ),
                        
                        #Top Menus
                        html.Div(
                            className='row',
                            children=[
                                html.Div(dcc.Dropdown(
                                    id='input1',
                                    options=[{'label': s[0], 'value': s[1]} for s in zip(chipsets.chipset_name, chipsets.chipset_id)							   
							         ],
                                    value=[1, 7, 2, 4],
                                    multi= True
                                ), className='col-lg-12'),
                                                                
                            ]
                        ),
                        
                        #Row 1 graphs
                        html.Div(
                            className='row',
                            children=[
                                html.Div(dcc.Graph(id='update_gpu_history'), className='col-lg-8'),
                                html.Div(dcc.Graph(id='update_gpu_price_performance'), className='col-lg-4'),  
                            ]
                        ),
                        
                        #Row 2 graphs
                        html.Div(
                            className='row',
                            children=[
                                html.Div(dcc.Graph(id='update_gpu_g3d'), className='col-lg-4'),
                                html.Div(dcc.Graph(id='update_gpu_direct_compute'), className='col-lg-4'),                                
                                html.Div(dcc.Graph(id='update_gpu_memory'), className='col-lg-4'),  
                            ]
                        ), 
                        
                        #Row 3 graphs
                        html.Div(
                            className='row',
                            children=[
                                html.Div(dcc.Graph(id='update_gpu_price_performance_hist'), className='col-lg-12')
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
            
                #Plot dashboard                          
                get_menu(),
    
                #Plot elements     
                html.Div(
                    className='col-lg-10 p-3 mb-2 bg-white text-dark',
                    children=[
                        html.P('Work In Progress')
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
            
                #Plot dashboard                          
                get_menu(),
    
                #Plot elements     
                html.Div(
                    className='col-lg-10 p-3 mb-2 bg-white text-dark',
                    children=[
                        html.P('Work In Progress')
                    ]
                )                   
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


		
#callbacks
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
        plots[str(input_value)] = go.Scatter(name = str(name_1), x=data_1.index, y=data_1.values, opacity=0.7, hoverinfo="x+y")

	#Plot itself
    return {
            'data':[trace for key, trace in plots.items()],
            'layout': {
                'yaxis': {'title':'Average Price (USD)'},
                'legend' : {'x' : 0.015, 'y': 0.975},
                'title': '<br>Price History<br>'
            }
    } 

            
@app.callback(
    Output(component_id='update_gpu_memory', component_property='figure'),
    [Input(component_id='input1', component_property='value')]
)        
def update_gpu_memory(input1_values):        
    plots = {}  
    for input_value in input1_values:
        df_filtered = memory[memory['chipset_id'] == input_value]
        y = df_filtered['chipset_name'].values[0]
        x = df_filtered['memory_in_GB'].mode().values[0]	      
        plots[str(input_value)] = go.Bar(x=[x], y=[y], hoverinfo="x+y", orientation = 'h')
    
    #Plot itself
    return {
            'data':[trace for key, trace in plots.items()],
            'layout': {
                'xaxis': {'title':'Memory (GB)', 'tickformat': '.2f'},
                'title': '<br>Memory<br>',
                'showlegend' : False
            }
    }                

    
@app.callback(
    Output(component_id='update_gpu_g3d', component_property='figure'),
    [Input(component_id='input1', component_property='value')]
)        
def update_gpu_g3d(input1_values):        
    plots = {}  
    for input_value in input1_values:
        df_filtered = benchmarks[benchmarks['chipset_id'] == input_value]
        y = df_filtered['chipset_name'].values[0]
        x = df_filtered['passmark_g3d'].mode().values[0]	      
        plots[str(input_value)] = go.Bar(x=[x], y=[y], hoverinfo="x+y", orientation = 'h')
    
    #Plot itself
    return {
            'data':[trace for key, trace in plots.items()],
            'layout': {
                'xaxis': {'title':'Score'},
                'title': '<br>Passmark: G3D Mark<br>',
                'showlegend' : False
            }
    } 


@app.callback(
    Output(component_id='update_gpu_direct_compute', component_property='figure'),
    [Input(component_id='input1', component_property='value')]
)          
def update_gpu_direct_compute(input1_values):        
    plots = {}  
    for input_value in input1_values:
        df_filtered = benchmarks[benchmarks['chipset_id'] == input_value]
        y = df_filtered['chipset_name'].values[0]
        x = df_filtered['passmark_direct_compute'].values[0]	      
        plots[str(input_value)] = go.Bar(x=[x], y=[y], hoverinfo="x+y", orientation = 'h')
    
    #Plot itself
    return {
            'data':[trace for key, trace in plots.items()],
            'layout': {
                'xaxis': {'title' : 'Operations per second'},
                'title': '<br>Passmark: Direct Compute<br>',
                'showlegend' : False
            }
    }

@app.callback(
    Output(component_id='update_gpu_price_performance', component_property='figure'),
    [Input(component_id='input1', component_property='value')]
)          
def update_gpu_price_performance(input1_values):        
    plots = {}  
    for input_value in input1_values:
        df_filtered = benchmarks[benchmarks['chipset_id'] == input_value]
        x = df_filtered['chipset_name'].values[0]
        
        current_price = prices[prices['chipset_id'] == input_value].groupby(['datetime'])['price'].mean()[-1]
        y = df_filtered['passmark_direct_compute'].values[0]/current_price	      
        plots[str(input_value)] = go.Bar(x=[x], y=[y], hoverinfo="x+y")
    
    #Plot itself
    return {
            'data':[trace for key, trace in plots.items()],
            'layout': {
                'yaxis': {'title' : 'Operations per second / USD'},
                'title': '<br>Current Price Performance<br>',
                'showlegend' : False
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
        
        plots[str(input_value)] = go.Scatter(name = str(name_1), x=data_1.index, y=data_1.values, opacity=0.7, hoverinfo="x+y")

	#Plot itself
    return {
            'data':[trace for key, trace in plots.items()],
            'layout': {
                'yaxis': {'title':'Operations per second / USD'},
                'title': '<br>Price Performance History<br>'
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
			
       
if __name__ == '__main__':
	app.server.run(debug=True, threaded=True)