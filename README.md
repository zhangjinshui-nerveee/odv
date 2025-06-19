# ODV - Oscilloscope Data Viewer

An open-source, web-based viewer for analyzing saved oscilloscope waveform data. This tool provides a simple and interactive way to inspect data files without needing proprietary software.
![demo_odv3](https://github.com/user-attachments/assets/1569ec62-2308-4a5a-aa1c-b65210af6108)

## Overview

The odv project aims to create a free, user-friendly viewer for data captured by oscilloscopes. Built with Python and Dash, it runs locally in your web browser, offering a smooth experience for zooming and inspecting waveform details.

## Key Features
- Interactive Plots: Zoom, pan, and hover over data points to see precise values.
- Drag and Drop: Easily load data files by dragging them onto the application window.
- Adjustable Precision: Control the number of data points displayed to balance between performance and detail.
- Web-Based: No complex software installation needed for users with the executable version.
- Extensible: Designed to easily add support for new oscilloscope models.

## Getting Started

There are two ways to run ODV: by downloading the ready-to-use application (easiest) or by running the code from the source (for developers).

### For Users (Running from Executables)

1. Navigate to the Releases Page of this repository.
2. Download the latest executable file for your operating system (e.g., odv-windows.exe, odv-macos).
3. Double-click the file to run the application. A browser window will open with the viewer ready to use.

### For Developers (Running from Source, Recommended)
#### Prerequisites:

- Python 3.8+
- pip

#### Instructions:

1. Clone the repository:
```
https://github.com/zhangjinshui-nerveee/odv.git
cd odv
```
2. Install the required dependencies:
```
pip install -r requirements.txt
```
3. Run the application:
```
python app.py
```
4. Open the viewer:
A browser window will pop up. If not, open your browser and navigate to the address shown in the terminal, which is typically:
http://127.0.0.1:8050/

## How to Contribute

We welcome contributions, especially to expand support for more data formats!
Reporting Bugs or Suggesting Features

If you encounter a bug or have an idea for a new feature, please open an issue on GitHub. Provide as much detail as possible.

### Adding Support for Your Oscilloscope Data

The main goal of this project is to support as many oscilloscope models as possible. If your data format is not currently supported, we would love to add it!

1. Please open a new issue with the title "Data Support for [Your Oscilloscope Model]".
2. In the issue, describe the oscilloscope model (e.g., "Tektronix MDO3054").
3. Provide a sanitized sample data file that we can use for development. You can attach it to the issue or provide a link.

### Currently Supported Models
- Tektronix MDO3054

## License
This project is licensed under the MIT License. See the LICENSE file for details.
