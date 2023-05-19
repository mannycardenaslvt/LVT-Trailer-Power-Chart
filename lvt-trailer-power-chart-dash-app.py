# TODO:
#   Nice-to-have: Save the plot as an HTML file for later reference

import base64
import io

import dash
from dash.dependencies import Input, Output, State
from dash import dcc, html

import plotly.graph_objects as go
from plotly.subplots import make_subplots

import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div([
    html.H3(children='LVT Trailer Power Chart', style={'textAlign': 'center'}),
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '98%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div(
        children=html.I("Expects a CSV file with four columns in this order: Date, Volts, Amps, Watts"),
        style={'textAlign': 'center'}
    ),
    html.Div(id='output-data-upload'),
])


def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')),
                parse_dates=[0]
            )
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(x=df.iloc[:, 0], y=df.iloc[:, 1], name=df.columns[1], marker=dict(color='rgba(66, 133, 244, 1)')),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=df.iloc[:, 0], y=df.iloc[:, 2], name=df.columns[2], marker=dict(color='rgba(234, 67, 53, 1)')),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=df.iloc[:, 0], y=df.iloc[:, 3], name=df.columns[3], marker=dict(color='rgba(251, 188, 4, 1)')),
        secondary_y=True,
    )
    # Set x-axis attributes
    fig.update_xaxes(
        title_text=df.columns[0],
        dtick=1000 * 60 * 60 * 24,  # duration of one day in milliseconds
        tickformat="%Y-%m-%d %I:%M %p"
    )

    # Set y-axes attributes
    fig.update_yaxes(title_text="{} and {}".format(df.columns[1], df.columns[2]), secondary_y=False)
    fig.update_yaxes(title_text=df.columns[3], secondary_y=True)

    return html.Div([
        dcc.Graph(figure=fig,
                  style={'width': '95vw', 'height': '90vh'})
    ])


@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'))
def update_output(list_of_contents, list_of_names):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n) for c, n in
            zip(list_of_contents, list_of_names)]
        return children


if __name__ == '__main__':
    app.run_server(debug=True)
