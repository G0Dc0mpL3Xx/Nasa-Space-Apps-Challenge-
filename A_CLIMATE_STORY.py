import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import requests
import io

# URL of the data file
url = 'https://gml.noaa.gov/aftp/data/trace_gases/co2/pfp/aircraft/txt/co2_aao_aircraft-pfp_1_ccgg_event.txt'

# Fetch data from the URL
response = requests.get(url)

# Load the content into a DataFrame using the appropriate delimiter and skipping metadata
# The first few lines might not be part of the data, hence, we skip them
data = io.StringIO(response.text)
df = pd.read_csv(data, sep='\s+', comment='#')  # Using whitespace as delimiter

# Display the first few rows of the DataFrame
print(df.head())

# Clean the DataFrame: rename columns for easier access
df.columns = [
    'site_code', 'year', 'month', 'day', 'hour', 'minute', 'second',
    'datetime', 'time_decimal', 'air_sample_container_id', 'value',
    'latitude', 'longitude', 'altitude', 'elevation', 'intake_height',
    'method', 'event_number', 'instrument', 'analysis_datetime', 'qcflag'
]

# Convert 'datetime' to pandas datetime format
df['datetime'] = pd.to_datetime(df['datetime'])

# Initialize the Dash app
app = dash.Dash(_name_, external_stylesheets=['https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css'])

app.layout = html.Div([
    html.H1("CO2 Emissions Dashboard", style={'text-align': 'center'}),

    # Dropdown for air sample container selection
    html.Label("Select Air Sample Container:"),
    dcc.Dropdown(
        id='container-dropdown',
        options=[{'label': container, 'value': container} for container in df['air_sample_container_id'].unique()],
        value=df['air_sample_container_id'].unique()[0]
    ),

    # Display selected container summary
    html.Div(id='summary-output', style={'padding': '20px'}),

    # Display the related chart
    dcc.Graph(id='co2-chart'),
])

# Callback to update the summary and chart based on selected inputs
@app.callback(
    [Output('summary-output', 'children'), Output('co2-chart', 'figure')],
    [Input('container-dropdown', 'value')]
)
def update_dashboard(selected_container):
    # Filter data for the selected air sample container
    container_data = df[df['air_sample_container_id'] == selected_container]

    # Create a summary string
    summary = f"Container {selected_container}: CO2 value is {container_data['value'].values[0]} ppm at coordinates ({container_data['latitude'].values[0]}, {container_data['longitude'].values[0]})."

    # Create a line chart for CO2 values over time
    fig = px.line(container_data, x='datetime', y='value', title=f'CO2 Levels for {selected_container}')

    return summary, fig

# Run the app
if _name_ == '_main_':
    app.run_server(debug=True)