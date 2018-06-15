import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import flask
import plotly.graph_objs as go
import os
from random import randint

import pandas as pd
import numpy as np
import sqlite3


#Application object
server = flask.Flask(__name__)
server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))
app = dash.Dash(__name__, server=server)
app.title ='APP TITLE'


#CSS and Javascript
external_css = ["https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css"]
for css in external_css:
    app.css.append_css({"external_url": css})

external_js = ['https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js']
for js in external_js:
    app.scripts.append_script({'external_url': js})
    
	
#Load in data:
def run_query(q):
    with sqlite3.connect(DB) as conn:
        return pd.read_sql(q,conn)
q_test = '''
SELECT 
    s.chipset,
    p.datetime,
    p.price
FROM gpu_specs s
INNER JOIN gpu_prices p ON s.item_id = p.item_id
'''
test_table = run_query(q_test)
test_table['datetime'] = test_table['datetime'].apply(lambda x: time.strftime('%Y-%m-%d', time.localtime(x))) 
ten_eigties = test_table[test_table['chipset'] == 'GeForce GTX 1080 Ti']
grouped = ten_eigties.groupby(['datetime'])['price'].mean()

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
                             options=[
							         {'label': '0', 'value': 0},
                                     {'label': '1', 'value': 1}
							         ],
                             value=0
                             )]
                     ),

                     html.Div(dcc.Markdown('''---''')),
                     
                     
                     html.Div(className='',
                              children=[html.B('RADIO TITLE:'),
                     dcc.RadioItems(
                             inputStyle={'display':'inline-block', 'margin-right':'5px'},
                             labelStyle={'display':'inline-block', 'margin-right':'15px'},
                             id='input2',
                             options=[
                                     {'label': 'RADIO 1', 'value': '0'},
                                     {'label': 'RADIO 2', 'value': '1'}
                                     ],
                             value='1'
                             )]
                     ),
                     
                     html.Div(dcc.Markdown('''---''')),
                      
                     html.Div(className='',
                              children=[html.B('CHECKBOX TITLE:'), 
                     dcc.Checklist(
                             inputStyle={'display':'inline-block', 'margin-right':'5px'},
                             labelStyle={'display':'block', 'margin-right':'5px'},                             
                             id='input3',
                             options=[
                                     {'label': 'LABEL 1', 'value': '0'},
                                     {'label': 'LABEL 2', 'value': '1'},
                                     {'label': 'LABEL 3', 'value': '2'},
                                     {'label': 'LABEL 4', 'value': '3'}                                    
                                     ],
                             values=['1', '2', '3', '4']
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
                             children=[html.Div(dcc.Graph(id='update_gpu_1'), className='col-lg-6'),]
                             ),									   
							]
					),
                   
			]
	)
])    
    
    
#callbacks
@app.callback(
    Output(component_id='update_gpu_1', component_property='figure'),
    [Input(component_id='input1', component_property='value')]
)
def update_gpu_1(input_value1):
    #Filter data based on inputs
    if input_value1 == 0:
        data = grouped
    else:
        data = grouped
    #Plot itself
    trace1 = go.plot(name = 'PLOT NAME', x=data.index, y=data.values, opacity=0.7, marker={'color':'#9999ff'}, hoverinfo="x+y+name", hoverlabel={'bgcolor':'#4d4d4d'})
    return {
            'data':[trace1],
            'layout': {
                'xaxis': {'title':'FILLERX'},
                'yaxis': {'title':'FILLERY'},
                'title': '<br>TITLE_GRAPH<br>HERE'
            }
        } 
            

        
if __name__ == '__main__':
	app.server.run(debug=True, threaded=True)