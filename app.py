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

    html.Div(
        [
            html.Label("Plot mode:", style={"marginRight": "10px"}),
            dcc.RadioItems(
                id="plot-mode",
                options=[
                    {"label": "Combined", "value": "combined"},
                    {"label": "Split", "value": "split"}
                ],
                value="combined",
                labelStyle={"display": "inline-block", "marginRight": "5px"}
            )
        ],
        style={
            "display": "flex",
            "justifyContent": "center",
            "alignItems": "center",
            "marginBottom": "20px"
        }
    ),

    dcc.Graph(id="graph"),

    dcc.Store(id="trace-visibilities-store", data={}),
    dcc.Store(id="data-store")
]

@callback(
    Output("data-store", "data"),

    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    State("upload-data", "last_modified")
)
def upload_data(contents, filename, last_modified):
    if contents is None:
        return None

    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)
    data = decoded.decode("utf-8")
    return data

@callback(
    Output("graph", "figure"),
    Output("graph", "style"),
    Output("trace-visibilities-store", "data"),

    Input("data-store", "data"),
    Input("num-points", "value"),
    Input("plot-mode", "value"),
    Input("graph", "relayoutData"),
    Input("graph", "restyleData"),
    State("trace-visibilities-store", "data")
)
def update_graph(
    data,
    num_points,
    plot_mode,
    relayoutData,
    restyleData,
    trace_visibilities_store
):
    if data is None:
        return None, {"display": "none"}, None

    df = pd.read_csv(io.StringIO(data), skiprows=20)

    if relayoutData:
        x0 = relayoutData.get("xaxis.range[0]")
        x1 = relayoutData.get("xaxis.range[1]")
        if x0 and x1:
            df = df[(df["TIME"] >= x0) & (df["TIME"] <= x1)]

    df = main.downsample(df, num_points)

    if plot_mode == "combined":
        fig = main.plot_combined(df, show_fig=False)
    else:
        fig = main.plot_split(df, show_fig=False)

    # Traces have visibility states of True (graphed) or "legendonly" (hidden)
    if trace_visibilities_store is None:
        trace_visibilities_store = {trace.name: True for trace in fig.data}
    if restyleData and "visible" in restyleData[0]:
        changed_visibilities = restyleData[0]["visible"]
        changed_indexes = restyleData[1]
        for visibility_state, i in zip(changed_visibilities, changed_indexes):
            name = fig.data[i].name
            trace_visibilities_store[name] = visibility_state
    for trace in fig.data:
        if trace.name in trace_visibilities_store:
            trace.visible = trace_visibilities_store[trace.name]

    return fig, {"width": "80%", "margin": "auto"}, trace_visibilities_store


if __name__ == "__main__":
    app.run(debug=True)
