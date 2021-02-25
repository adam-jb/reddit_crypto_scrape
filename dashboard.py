import dash # v 1.16.2
import dash_core_components as dcc # v 1.12.1
import dash_bootstrap_components as dbc # v 0.10.3
import dash_html_components as html # v 1.1.1
import pandas as pd
import plotly.express as px # plotly v 4.7.1
import plotly.graph_objects as go
import plotly.io as pio
import numpy as np
import os 
import sys 



# load app
app = dash.Dash(__name__, title='WSB Activity') #, external_stylesheets=[external_stylesheets])
pio.templates.default = "simple_white" # set colour scheme

# load primary dataframe
main_path = os.path.dirname(os.path.abspath(__file__)) + '/'
input_data = main_path + "raw_data/data_for_app.csv"
df = pd.read_csv(input_data)

df['activity_adj'] = df['size'] / df['volume_24h']
dates = pd.unique(df['Date'])


# get latest day only for scatter plot
latest_day = df[df['Date'] == max(dates)]
latest_day = latest_day.reset_index(drop = True)
latest_day['index1'] = latest_day.index


# add index1
df = df.merge(latest_day[['symbol', 'index1']], on = 'symbol')





#line_trend_features = ['activity_adj', 'price', 'anticipation', 'positive']
scatter_size_col_features = ['price', 'anger', 'anticipation', 'disgust', 'fear', 'joy', 'sadness', 
              'surprise', 'trust', 'negative', 'positive']
              
for i in range(len(scatter_size_col_features)):
  di = {}
  di["label"] = scatter_size_col_features[i]
  di["value"] = scatter_size_col_features[i]
  if i == 0:
    scatter_size_col_dict = [di]
  else:
    scatter_size_col_dict = scatter_size_col_dict + [di]
              


app.layout = html.Div([

  

    html.Div([

    		html.Div(
            html.Img(src='/assets/wsj_tracker_icon.jpeg')
            , className='banner2'
            , style={'width': '20%', 'display': 'inline-block'}
        ),

        html.Div([
            
            html.Div([
                html.Label('Point size by'),], 
                style={'font-size': '18px'}),
            
            dcc.Dropdown(
                id='size-set',
                options=scatter_size_col_dict,
                value='positive',  # default
                clearable=False   # forces at least one of the above to be selected

            )], style={'width': '20%', 'display': 'inline-block'}
        ),

        html.Div([
            
            html.Div([
                html.Label('Point colour by'),], 
                style={'font-size': '18px'}),
            
            html.Div([
                dcc.Dropdown(
                    id='colour-set',
                    options=scatter_size_col_dict,
                    value='anticipation',
                    clearable=False,
                    #labelStyle={'float': 'right', 'display': 'inline-block', 'margin-right': 10}
                ),
            ]# style={'width': '30%', 'float': 'right', 'display': 'inline-block'}
            
        )], style={'width': '20%', 'display': 'inline-block'}
    )
    
    ]),
    
    html.Div(style={'padding': 10}),
    
    html.Div([

    	html.Div([
    	#	html.H3('Main plot'),
	        dcc.Graph(
	            id='scatter-plot',        # tells you when the data will need to be called
	            hoverData={'points': [{'customdata': 0}]}   # what data to display on hover (like text in ggplotly)
	        )], style={'float': 'left', 'width': '48%', 'height':'90%'}),

    	
    	html.Div([

    		  html.Div([
    			  dcc.Graph(id='point-plot')
    			]), 
    			
    			html.Div([
    			  dcc.Graph(id='point-plot2')
    			])
    			
    			], style={'float': 'right', 'width': '24%', 'height': '10%'}),
    			
    			
    		html.Div([

    		  html.Div([
    			  dcc.Graph(id='point-plot3')
    			]), 
    			
    			html.Div([
    			  dcc.Graph(id='point-plot4')
    			])
    			
    			], style={'float': 'right', 'width': '24%', 'height': '10%'})
    	
    
    
    ], style={'backgroundColor': 'rgb(255, 255, 255)'})
    
 

])



# callback changes things reactively to selected values
@app.callback(
    dash.dependencies.Output('scatter-plot', 'figure'),
	[
		dash.dependencies.Input('size-set', 'value'),
		dash.dependencies.Input('colour-set', 'value'),
	]
)


def update_graph(size_set, colour_set):

  hover_names = []
  for priceval, symval in zip(latest_day['price'].values, latest_day['symbol'].values):
    	hover_names.append(f'{symval}<br>Value of {priceval}')  # {} inserts values
  					# looks like it creates a list of values to accompany the points, and updates
  					# with each call of update_graph
  					# or updated with every change user makes - @app.callback does this

  fig = px.scatter(
  	latest_day,
  	x=latest_day['price_change24'],    # model is text selection I think here
  	y=latest_day['activity_adj'],
  	opacity=0.8,
  	color_continuous_scale='Viridis',
  	hover_name = hover_names,
  	color = latest_day[colour_set],
  	size = latest_day[size_set]
  )
  fig.update_traces(customdata=latest_day.index)
  fig.update_layout(
  	height = 600,
  	hovermode ='closest',  # something about hovering info beign close to the data point,
  	xaxis_title="Price change last 24 hours",
    yaxis_title="Reddit activity relative to market cap",
  )
  return fig






@app.callback(
    dash.dependencies.Output('point-plot', 'figure'),
	[
		dash.dependencies.Input('scatter-plot', 'hoverData')   # could use hoverData / clickData
	]
)

def update_point_plot(hoverData):   # the hoverdata input means it will update whenever the thing hovered over changes

	index_value = hoverData['points'][0]['pointIndex']
	#print(hoverData['points'])
	index = df['index1'] == index_value
	#print('index', index)
	coin_name = df['symbol'][index]
	dates_timeline =  pd.Series(df['Date'][index])
	y_vals = pd.Series(df['price'][index])
	title = f'For {coin_name}'   # "Customer %s" % index
	
	fig = px.line(x = dates_timeline, y = y_vals)
	fig.update_layout(
	#	barmode = 'group',
		height = 300,
		margin={'l': 20, 'b': 30, 'r':10, 't':2},    # defines blank space around a plot
		xaxis_title="Date",
    yaxis_title="Price"
	)
	
	#fig.update_yaxes(range=[0, max_val])    # set y lim
	
	return fig





@app.callback(
    dash.dependencies.Output('point-plot2', 'figure'),
	[
		dash.dependencies.Input('scatter-plot', 'hoverData')   # could use hoverData / clickData
	]
)

def update_point_plot2(hoverData):   # the hoverdata input means it will update whenever the thing hovered over changes

	index_value = hoverData['points'][0]['pointIndex']
	#print(hoverData['points'])
	index = df['index1'] == index_value
	#print('index', index)
	coin_name = df['symbol'][index]
	dates_timeline =  pd.Series(df['Date'][index])
	y_vals = pd.Series(df['activity_adj'][index])
	title = f'For {coin_name}'   # "Customer %s" % index
	
	fig = px.line(x = dates_timeline, y = y_vals)
	fig.update_layout(
	#	barmode = 'group',
		height = 300,
		margin={'l': 20, 'b': 30, 'r':10, 't':2},    # defines blank space around a plot
		xaxis_title="Date",
    yaxis_title="Activity scaled by market cap"
	)
	
	#fig.update_yaxes(range=[0, max_val])    # set y lim
	
	return fig




@app.callback(
    dash.dependencies.Output('point-plot3', 'figure'),
	[
		dash.dependencies.Input('scatter-plot', 'hoverData')   # could use hoverData / clickData
	]
)

def update_point_plot3(hoverData):   # the hoverdata input means it will update whenever the thing hovered over changes

	index_value = hoverData['points'][0]['pointIndex']
	#print(hoverData['points'])
	index = df['index1'] == index_value
	#print('index', index)
	coin_name = df['symbol'][index]
	dates_timeline =  pd.Series(df['Date'][index])
	y_vals = pd.Series(df['anticipation'][index])
	title = f'For {coin_name}'   # "Customer %s" % index
	
	fig = px.line(x = dates_timeline, y = y_vals)
	fig.update_layout(
	#	barmode = 'group',
		height = 300,
		margin={'l': 20, 'b': 30, 'r':10, 't':2},    # defines blank space around a plot
		xaxis_title="Date",
    yaxis_title="Anticipation (based on text)"
	)
	
	#fig.update_yaxes(range=[0, max_val])    # set y lim
	
	return fig



@app.callback(
    dash.dependencies.Output('point-plot4', 'figure'),
	[
		dash.dependencies.Input('scatter-plot', 'hoverData')   # could use hoverData / clickData
	]
)

def update_point_plot4(hoverData):   # the hoverdata input means it will update whenever the thing hovered over changes

	index_value = hoverData['points'][0]['pointIndex']
	#print(hoverData['points'])
	index = df['index1'] == index_value
	#print('index', index)
	coin_name = df['symbol'][index]
	dates_timeline =  pd.Series(df['Date'][index])
	y_vals = pd.Series(df['positive'][index])
	title = f'For {coin_name}'   # "Customer %s" % index
	
	fig = px.line(x = dates_timeline, y = y_vals)
	fig.update_layout(
	#	barmode = 'group',
		height = 300,
		margin={'l': 20, 'b': 30, 'r':10, 't':2},    # defines blank space around a plot
		xaxis_title="Date",
    yaxis_title="Positivity (based on text)"
	)
	
	#fig.update_yaxes(range=[0, max_val])    # set y lim
	
	return fig




if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_ui=False)  # switches off error messages in code
    
    
    
  
  
  
