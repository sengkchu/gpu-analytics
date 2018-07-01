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
app.layout = html.Div(
  className='container-fluid',
  children=[
                              
    html.Div(className='row', 
             children=[
    
    #Plot dashboard                          
    html.Div(className='col-lg-2 p-3 mb-2 bg-light text-dark', 
             children=[
                     html.Div(dcc.Markdown('### TITLE')),                     
                     html.Div(dcc.Markdown('''---''')),
                     html.Div(dcc.Markdown('''TEXT1''')),
                     html.Div(dcc.Markdown('''TEXT2''')),
                     html.Div(dcc.Markdown('''---''')),                    
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
                     html.Div(dcc.Markdown('''---''')),
                     
                     
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
                     
                     html.Div(dcc.Markdown('''---''')),
                      
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
                     
                     html.Div(dcc.Markdown('''---''')),
                     html.Div(dcc.Markdown('''Note: Use the cursor to interact with the plot. Double-click on the plot to zoom back out.''')),                      
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
    
    
#callbacks
@app.callback(
    Output(component_id='update_gpu_1', component_property='figure'),
    [Input(component_id='input1', component_property='value'),
	Input(component_id='input2', component_property='value'),
	Input(component_id='input3', component_property='value')])
def update_gpu_1(input_value1, input_value2, input_value3):

    #Filter data based on inputs    
    try:    
        result_1 = prices[(prices['chipset_id'] == input_value1) & (prices['merchant_id'].isin(input_value3))]
        name_1 = result_1['chipset_name'].values[0]
        data_1 = result_1.groupby(['datetime'])['price'].mean()
	
        result_2 = prices[(prices['chipset_id'] == input_value2) & (prices['merchant_id'].isin(input_value3))]
        name_2 = result_2['chipset_name'].values[0]
        data_2 = result_2.groupby(['datetime'])['price'].mean()		
		
        trace1 = go.Scatter(name = str(name_1), x=data_1.index, y=data_1.values, opacity=0.7, marker={'color':'#9999ff'}, hoverinfo="x+y", hoverlabel={'bgcolor':'#4d4d4d'})
        trace2 = go.Scatter(name = str(name_2), x=data_2.index, y=data_2.values, opacity=0.7, hoverinfo="x+y", hoverlabel={'bgcolor':'#4d4d4d'})
	
		#Plot itself
        return {
                'data':[trace1, trace2],
                'layout': {
                    'yaxis': {'title':'Average Price (USD)'},
                    'title': '<br>Price History Comparison<br>'
                }
            } 
    except:
        return {
                'data':[],
                'layout': {
                    'yaxis': {'title':'Average Price (USD)'},
                    'title': '<br>Price History Comparison<br>'
                }
            } 	

        
if __name__ == '__main__':
	app.server.run(debug=True, threaded=True)