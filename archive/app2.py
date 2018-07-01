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

#Load chipsets data into memory (chipsets without price history are excluded)
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

manufacturers = prices['manufacturer'].drop_duplicates()

merchants = run_query('SELECT * FROM merchants')

specs = run_query('SELECT * FROM card_specs')

benchmarks = run_query('SELECT * FROM benchmarks')


#App Layouts

app.config.suppress_callback_exceptions = True

'''
Page1 = html.Div(
  className='container-fluid',
  children=[
                              
    html.Div(className='row', 
             children=[
    
    #Plot dashboard                          
    html.Div(className='col-lg-2 p-3 mb-2 bg-light text-dark', 
             children=[
                     html.Div(dcc.Markdown('### TITLE')),                     
                     html.Div(dcc.Markdown
                     html.Div(dcc.Markdown('''''')),
                     html.Div(dcc.Markdown('''''')),
                     html.Div(dcc.Markdown                    
                     html.Div(className='',
                              children=[html.B('DROPDOWNTITLE:'),						  
                     dcc.Dropdown(
                             id='input1',
                             options=[{'label': s[0], 'value': s[1]} for s in zip(chipsets.chipset_name, chipsets.chipset_id)							   
							         ],
                             value= 2
                             )]
                     ),
                     html.Div(className='',
                              children=[html.B('DROPDOWNTITLE:'),	
                     dcc.Dropdown(
                             id='input2',
                             options=[{'label': s[0], 'value': s[1]} for s in zip(chipsets.chipset_name, chipsets.chipset_id)							   
							         ],
                             value= 4
                             )]
                     ),
                     html.Div(dcc.Markdown
                     
                     
                     html.Div(className='',
                              children=[html.B('RADIO TITLE:'),
                     dcc.Dropdown(
                             id='input4',
                             options=[{'label': s[0], 'value': s[0]} for s in zip(manufacturers)
                                     ],
							 multi=True,
                             value = [i for i in manufacturers]
                             )]
                     ),
                     
                     html.Div(dcc.Markdown
                      
                     html.Div(className='',
                              children=[html.B('CHECKBOX TITLE:'), 
                     dcc.Dropdown(                          
                             id='input3',
                             options=[{'label': s[0], 'value': s[1]} for s in zip(merchants.merchant_name, merchants.merchant_id)                                  
                                     ],
							 multi=True,
                             value=[i+1 for i in range(len(merchants))]
                             )]	
                     ),
                     
                     html.Div(dcc.Markdown
                     html.Div(dcc.Markdown('''''')),                      
            ]),
    
    #Plot elements     
    html.Div(className='col-lg-10 p-3 mb-2 bg-white text-dark',
             children=[                     
                     html.Div(
                             className='row',
                             children=[html.Div(dcc.Graph(id='update_gpu_1'), className='col-lg-12'),]
                             ),									   
							]
					),
                   
			]
	)
])   
'''

    
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
                            html.B('''Select or type in GPUs:''')
                        ),
                        
                        #Top Menus
                        html.Div(
                            className='row',
                            children=[
                                #NEED MULTI INPUTS
                                html.Div(dcc.Dropdown(
                                    id='input1',
                                    options=[{'label': s[0], 'value': s[1]} for s in zip(chipsets.chipset_name, chipsets.chipset_id)							   
							         ],
                                    value= 2
                                ), className='col-lg-5'),
                                html.Div(dcc.Markdown('''VS'''), className = 'col-lg-2 text-center'),
                                html.Div(dcc.Dropdown(
                                    id='input2',
                                    options=[{'label': s[0], 'value': s[1]} for s in zip(chipsets.chipset_name, chipsets.chipset_id)							   
							         ],
                                    value= 4
                                ), className='col-lg-5'),
                                                                
                            ]
                        ),
                        
                        #Row 1 graphs
                        html.Div(
                            className='row',
                            children=[
                                html.Div(dcc.Graph(id='update_gpu_history'), className='col-lg-8'),
                                html.Div(dcc.Graph(id='update_gpu_value'), className='col-lg-4'),  
                            ]
                        ),
                        
                        #Row 2 graphs
                        html.Div(
                            className='row',
                            children=[
                                html.Div(dcc.Graph(id='update_gpu_history'), className='col-lg-8'),
                                html.Div(dcc.Graph(id='update_gpu_value'), className='col-lg-4'),  
                            ]
                        )                         
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
    [Input(component_id='input1', component_property='value'),
	Input(component_id='input2', component_property='value')]
)
def update_gpu_history(input_value1, input_value2):

    #Filter data based on inputs    
    try:    
        result_1 = prices[prices['chipset_id'] == input_value1]
        name_1 = result_1['chipset_name'].values[0]
        data_1 = result_1.groupby(['datetime'])['price'].mean()
	
        result_2 = prices[prices['chipset_id'] == input_value2]
        name_2 = result_2['chipset_name'].values[0]
        data_2 = result_2.groupby(['datetime'])['price'].mean()		
		
        trace1 = go.Scatter(name = str(name_1), x=data_1.index, y=data_1.values, opacity=0.7, marker={'color':'#9999ff'}, hoverinfo="x+y", hoverlabel={'bgcolor':'#4d4d4d'})
        trace2 = go.Scatter(name = str(name_2), x=data_2.index, y=data_2.values, opacity=0.7, hoverinfo="x+y", hoverlabel={'bgcolor':'#4d4d4d'})
	
		#Plot itself
        return {
                'data':[trace1, trace2],
                'layout': {
                    'yaxis': {'title':'Average Price (USD)'},
                    'legend' : {'x' : 0.015, 'y': 0.975},
                    'title': '<br>Price History Comparison<br>'
                }
            } 
    except:
        return {
                'data':[],
                'layout': {
                    'title': '<br>No Data Available<br>'
                }
            } 	

@app.callback(
    Output(component_id='update_gpu_value', component_property='figure'),
    [Input(component_id='input1', component_property='value'),
	Input(component_id='input2', component_property='value')]
)
def update_gpu_value(input_value1, input_value2):

    #Filter data based on inputs    
    try:    
        result_1 = prices[prices['chipset_id'] == input_value1]
        name_1 = result_1['chipset_name'].values[0]
        data_1 = result_1.groupby(['datetime'])['price'].mean()
	
        result_2 = prices[prices['chipset_id'] == input_value2]
        name_2 = result_2['chipset_name'].values[0]
        data_2 = result_2.groupby(['datetime'])['price'].mean()		
		
        trace1 = go.Scatter(name = str(name_1), x=data_1.index, y=data_1.values, opacity=0.7, marker={'color':'#9999ff'}, hoverinfo="x+y", hoverlabel={'bgcolor':'#4d4d4d'})
        trace2 = go.Scatter(name = str(name_2), x=data_2.index, y=data_2.values, opacity=0.7, hoverinfo="x+y", hoverlabel={'bgcolor':'#4d4d4d'})
	
		#Plot itself
        return {
                'data':[trace1, trace2],
                'layout': {
                    'yaxis': {'title':'Average Price (USD)'},
                    'legend' : {'x' : 0.015, 'y': 0.975},
                    'title': '<br>Price History Comparison<br>'
                }
            } 
    except:
        return {
                'data':[],
                'layout': {
                    'title': '<br>No Data Available<br>'
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