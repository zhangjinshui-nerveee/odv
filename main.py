import pandas as pd
# import matplotlib.pyplot as plt

'''
MILESTONES
- [x] read data with pandas
- [ ] plot data out, adjust the format to match the appearance of oscilloscope, show only 10,000 data points (equally spreaded)
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

if __name__ == "__main__":
    df = read_data("tek5494.csv")
    print(df.head())

    print()

    df = downsample(df, 10_000)
    print(df.head())
    print(len(df))
