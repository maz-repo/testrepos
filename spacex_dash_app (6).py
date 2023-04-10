
# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()


options=[{'label': 'All Sites', 'value': 'ALL'}]
spacex_ls = pd.Series(spacex_df['Launch Site'].unique())
spacex_ls.map(lambda x: options.append({'label':x, 'value':x}))
# print(options)

spacex_df_success = pd.DataFrame(spacex_df[spacex_df['class'] == 1].groupby('Launch Site')['class'].sum()).reset_index()
#print(spacex_df_success) 

outcome = {1: 'Success', 0: 'Failure'}
spacex_df['outcome'] = spacex_df['class'].map(outcome)
spacex_df_stat_sites = pd.DataFrame(spacex_df.groupby(['Launch Site','outcome'])['class'].count()).reset_index()
#print(spacex_df_stat_sites) 

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                dcc.Dropdown(id='site-dropdown',
                                    options=options,
                                    value='ALL',
                                    placeholder="Launch Sites",
                                    searchable=True
                                    ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(id='payload-slider',
                                        min=0, max=10000, step=1000,
                                        marks={0:'0', 100:'100'},
                                        value=[min_payload, max_payload]),
                                html.Br(),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output

# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        fig = px.pie(spacex_df_success, values='class', 
            names='Launch Site', 
            title='All Sites Success Ratio')
        
    else:
        spacex_df_stat_site = spacex_df_stat_sites[spacex_df_stat_sites['Launch Site']==entered_site].reset_index()
        colors=['orange', 'blue'] 
        fig = px.pie(spacex_df_stat_site, values='class', 
            names='outcome',
            color_discrete_sequence=colors, 
            title=(entered_site + ' Success Failure Ratio'))
    
    return fig
    
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output

@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'), Input(component_id="payload-slider", component_property='value')])

def get_scatter_plot(entered_site, entered_range):
    if entered_site == 'ALL':
        filtered_ds_all = spacex_df[(spacex_df['Payload Mass (kg)'] >= entered_range[0]) & (spacex_df['Payload Mass (kg)'] <= entered_range[1])].reset_index()
        fig = px.scatter(filtered_ds_all, x='Payload Mass (kg)', y='class', color='Booster Version', title='All Sites Payload Mass - Launch Outcome') 
    else:
        filtered_ds = spacex_df[(spacex_df['Launch Site']==entered_site) & 
            (spacex_df['Payload Mass (kg)'] >= entered_range[0]) & (spacex_df['Payload Mass (kg)'] <= entered_range[1])].reset_index() 
        fig = px.scatter(filtered_ds, x='Payload Mass (kg)', y='class', color='Booster Version', title=(entered_site + ' Payload Mass - Launch Outcome'))

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
