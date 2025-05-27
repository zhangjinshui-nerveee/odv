import os

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

'''
MILESTONES
- [x] read data with pandas
- [x] plot data out, adjust the format to match the appearance of oscilloscope, show only 10,000 data points (equally spreaded)
- [ ] use packages of tkinter or dash to embed the plot in a user-interfacing frame
- [ ] add button to allow spread signals into different channels, e.g. we have three signals in tek5494, the toggle button to allow show them on the same plot or three separate ones
- [ ] add function to allow select x-axis range
- [ ] change the input approach of selecting x-range to mouse-dragging
'''

def read_data(file_name: str) -> pd.DataFrame:
    """Read data from CSV file and return as DataFrame"""
    df = pd.read_csv(file_name, skiprows=20)
    return df

def downsample(df: pd.DataFrame, n: int) -> pd.DataFrame:
    """Downsample df to include only n data points that are equally spread out"""
    total_rows = len(df)

    # If requesting more points than there are in total
    if n >= total_rows:
        return df

    step = total_rows / n
    indices = [int(i * step + step / 2) for i in range(n)]

    downsampled_df = df.iloc[indices]
    return downsampled_df

def get_channel_columns(df: pd.DataFrame) -> list[str]:
    """Detect columns that should be treated as channels"""
    columns = df.columns
    channel_columns = [
        c for c in columns if c.startswith("CH") or c.startswith("REF")
    ]
    return channel_columns

def plot_combined(df: pd.DataFrame, show_fig: bool):
    """Plot the given df such that all channels are combined in one plot"""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["TIME"],
        y=df["CH1"],
        mode="lines",
        name="CH1",
        line=dict(color="yellow")
    ))
    fig.add_trace(go.Scatter(
        x=df["TIME"],
        y=df["CH2"],
        mode="lines",
        name="CH2",
        line=dict(color="cyan")
    ))
    fig.add_trace(go.Scatter(
        x=df["TIME"],
        y=df["CH4"],
        mode="lines",
        name="CH4",
        line=dict(color="lime")
    ))

    fig.update_layout(
        template="plotly_dark",
        title=dict(text="Oscilloscope Data"),
        xaxis=dict(
            griddash="dot",
            zeroline=False
        ),
        yaxis=dict(
            griddash="dot",
            zeroline=False
        ),
    )

    if show_fig:
        fig.show()
    return fig

def plot_split(df: pd.DataFrame, show_fig: bool):
    """Plot the given df with each channel in a separate subplot"""
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                        subplot_titles=["CH1", "CH2", "CH4"])

    fig.add_trace(go.Scatter(
        x=df["TIME"],
        y=df["CH1"],
        mode="lines",
        name="CH1",
        line=dict(color="yellow")
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=df["TIME"],
        y=df["CH2"],
        mode="lines",
        name="CH2",
        line=dict(color="cyan")
    ), row=2, col=1)
    fig.add_trace(go.Scatter(
        x=df["TIME"],
        y=df["CH4"],
        mode="lines",
        name="CH4",
        line=dict(color="lime")
    ), row=3, col=1)

    fig.update_layout(
        template="plotly_dark",
        title=dict(text="Oscilloscope Data")
    )
    fig.update_xaxes(griddash="dot", zeroline=False)
    fig.update_yaxes(griddash="dot", zeroline=False)

    if show_fig:
        fig.show()
    return fig

if __name__ == "__main__":
    df = read_data(os.path.join("MDO3054", "tek5494.csv"))
    print(df.head())

    print()

    df = downsample(df, 10_000)
    print(df.head())
    print(len(df))

    plot_combined(df, show_fig=True)
    plot_split(df, show_fig=True)

    print(get_channel_columns(df))
