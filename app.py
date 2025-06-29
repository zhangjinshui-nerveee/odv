import base64
import io
from datetime import datetime, UTC
import webbrowser
import os

import pandas as pd
from dash import Dash, html, dcc, Input, Output, State, callback
from dash.dependencies import ALL

import main

app = Dash()
app.title = "Oscilloscope Data Viewer"

app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            html,
            body,
            #react-entry-point,
            #root,
            #_dash-app-content {
                height: 100%;
                margin: 0;
                padding: 0;
            }
            .full-height-container {
                display: flex;
                flex-direction: column;
                height: 100%;
            }
            #graph-wrapper {
                flex-grow: 1;
                display: flex;
                justify-content: center;
            }
            #graph {
                width: 80%;
                height: 100%;
            }
            #_dash-global-error-container,
            #_dash-global-error-container > div {
                height: 100%;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""

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
            html.Div([
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
                    ]
                )
            ], style={"flex": "0 0 auto", "marginRight": "40px"}),

            html.Div(
                id="rename-traces-container",
                style={
                    "display": "flex",
                    "justifyContent": "center",
                    "alignItems": "center"
                }
            )
        ],
        style={
            "display": "flex",
            "justifyContent": "center",
            "alignItems": "flex-start",
            "width": "80%",
            "margin": "20px auto"
        }
    ),

    html.Div(
        id="graph-wrapper",
        children=dcc.Graph(id="graph", style={"height": "100%"}),
        className="full-height-container"
    ),

    dcc.Store(id="trace-visibilities-store", data={}),
    dcc.Store(id="data-store"),
    dcc.Store(id="trace-names-store", data={}),
    dcc.Store(id="last-file-upload-time-store")
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
    return {"data": data, "file_upload_time": datetime.now(UTC).isoformat()}

@callback(
    Output("rename-traces-container", "children"),
    Output("trace-names-store", "data"),

    Input("data-store", "data")
)
def make_trace_rename_inputs(data):
    if data is None:
        return [], {}

    df = pd.read_csv(io.StringIO(data.get("data")), skiprows=20, nrows=1)
    trace_names = main.get_channel_columns(df)
    column_names_map = {name: name for name in trace_names}

    table_rows = []
    for trace in trace_names:
        row = html.Div([
            html.Label(
                trace,
                style={
                    "display": "block",
                    "textAlign": "center",
                    "marginBottom": "5px",
                    "fontWeight": "bold"
                }
            ),
            dcc.Input(
                id={"type": "rename-trace", "index": trace},
                type="text",
                value=trace,
                style={
                    "textAlign": "center",
                    "width": "90%"
                }
            )
        ], style={
            "margin": "0 10px",
            "width": "60px"
        })
        table_rows.append(row)

    table = html.Div([
        html.H3("Rename Traces", style={"textAlign": "center", "marginTop": "0", "marginBottom": "15px"}),
        html.Div(
            table_rows,
            style={
                "display": "flex",
                "flexWrap": "wrap",
                "gap": "10px",
                "justifyContent": "center"
            }
        )
    ])

    return table, column_names_map

@callback(
    Output("trace-names-store", "data", allow_duplicate=True),

    Input({"type": "rename-trace", "index": ALL}, "value"),
    State({"type": "rename-trace", "index": ALL}, "id"),
    prevent_initial_call=True
)
def update_trace_names(values, ids):
    return {i["index"]: val for i, val in zip(ids, values)}

@callback(
    Output("graph", "figure"),
    Output("graph", "style"),
    Output("trace-visibilities-store", "data"),
    Output("last-file-upload-time-store", "data"),

    Input("data-store", "data"),
    Input("num-points", "value"),
    Input("plot-mode", "value"),
    Input("graph", "relayoutData"),
    Input("graph", "restyleData"),
    Input("trace-names-store", "data"),
    State("trace-visibilities-store", "data"),
    State("last-file-upload-time-store", "data")
)
def update_graph(
    data,
    num_points,
    plot_mode,
    relayoutData,
    restyleData,
    trace_names_store,
    trace_visibilities_store,
    last_file_upload_time
):
    if data is None:
        return None, {"display": "none"}, None, None

    df = pd.read_csv(io.StringIO(data.get("data")), skiprows=20)
    file_upload_time = data.get("file_upload_time")
    is_new_file = file_upload_time != last_file_upload_time

    if relayoutData and not is_new_file:
        x0 = relayoutData.get("xaxis.range[0]")
        x1 = relayoutData.get("xaxis.range[1]")
        if x0 and x1:
            df = df[(df["TIME"] >= x0) & (df["TIME"] <= x1)]

    df = main.downsample(df, num_points)

    if plot_mode == "combined":
        fig = main.plot_combined(df, show_fig=False)
    else:
        fig = main.plot_split(df, show_fig=False)
    if trace_names_store:
        for trace in fig.data:
            if trace.name in trace_names_store:
                trace.name = trace_names_store[trace.name]

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

    return fig, {"width": "100%", "height": "100%"}, trace_visibilities_store, file_upload_time


if __name__ == "__main__":
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        webbrowser.open("http://127.0.0.1:8050")
    app.run(debug=True)
