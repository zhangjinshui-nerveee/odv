import base64
import io

import pandas as pd
from dash import Dash, html, dcc, Input, Output, State, callback

import main

app = Dash()
app.title = "Oscilloscope Data Viewer"

app.layout = [
    html.H1("Oscilloscope Data Viewer", style={"textAlign": "center"}),

    dcc.Upload(
        id="upload-data",
        children=html.Div([
            "Drag and Drop or ",
            html.A(
                "Select a CSV File",
                style={"text-decoration": "underline", "cursor": "pointer"}
            )
        ]),
        style={
            "width": "80%",
            "margin": "auto",
            "padding": "20px",
            "borderWidth": "2px",
            "borderStyle": "dashed",
            "textAlign": "center",
        },
        multiple=False
    ),

    html.Div(
        [
            html.Label("Number of data points to show: "),
            dcc.Input(
                id="num-points",
                type="number",
                value=10000,
                min=1,
                step=1
            )
        ],
        style={
            "textAlign": "center",
            "marginTop": "20px",
            "marginBottom": "20px"
        }
    ),

    dcc.Graph(id="graph")
]

@callback(
    Output("graph", "figure"),
    Output("graph", "style"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    State("upload-data", "last_modified"),
    Input("num-points", "value")
)
def update_graph(contents, filename, last_modified, num_points):
    if contents is None:
        return None, {"display": "none"}

    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)
    df = pd.read_csv(io.StringIO(decoded.decode("utf-8")), skiprows=20)
    df = main.downsample(df, num_points)

    fig = main.plot_combined(df, show_fig=False)
    return fig, {"width": "80%", "margin": "auto"}

if __name__ == "__main__":
    app.run(debug=True)
