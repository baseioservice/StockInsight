# Stock Insight

Indian Stock Market Tracker
Track NSE and BSE stocks with real-time data and interactive charts. Enter a stock symbol (e.g., 'GAIL' or 'TCS' for NSE, add '.BO' for BSE stocks)

## Overview

**Stock Insight** is a Streamlit app designed to deliver interactive data analysis and visualization. Built with modern Python tools and libraries, the project leverages capabilities from OpenAI, Pandas, Plotly, and more to create a responsive, dynamic user experience.

## Features

- **Interactive Dashboard:** Utilize Streamlit’s widgets to explore data.
- **Data Analysis & Visualization:** Integrate powerful libraries like Pandas and Plotly for robust analytics.
- **Real-Time Data:** Incorporate live data feeds using yfinance and trafilatura.
- **Modern Python Environment:** Developed with Python ≥3.11 and managed dependencies via Poetry.

## Requirements

- Python version: **>= 3.11, <4**
- Ensure you have [Poetry](https://python-poetry.org/) installed if you choose to manage your dependencies using Poetry.

## Installation

### Using Poetry

1. **Clone the repository:**

   ```bash
   git clone https://github.com/baseioservice/StockInsight.git
   cd StockInsight
   ```

2. **Install dependencies:**

   ```bash
   poetry install
   ```

### Using pip

If you prefer using `pip`, first generate a `requirements.txt` file from your `pyproject.toml` or create one manually with the following dependencies:

- openai>=1.63.2
- pandas>=2.2.3
- plotly>=6.0.0
- pytz>=2025.1
- streamlit>=1.42.2
- trafilatura>=2.0.0
- yfinance>=0.2.54

Then install with:

```bash
pip install -r requirements.txt
```

## Running the App

To launch the Streamlit application, run:

```bash
streamlit run main.py
```

> **Note:** Replace `main.py` with the path to your main application file if it differs.

## Project Configuration

The project is defined in the `pyproject.toml` file with the following settings:

```toml
[project]
name = "repl-nix-workspace"
version = "0.1.0"
description = "Add your description here"
requires-python = ">=3.11, <4"
dependencies = [
    "openai>=1.63.2",
    "pandas>=2.2.3",
    "plotly>=6.0.0",
    "pytz>=2025.1",
    "streamlit>=1.42.2",
    "trafilatura>=2.0.0",
    "yfinance>=0.2.54",
]

[tool.poetry]
package-mode = false
```

## Contributing

Contributions are welcome! If you have ideas for improvements, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Commit your changes and push the branch.
4. Open a pull request detailing your changes.

## License

This project is licensed under the MIT License. 

## Contact

For any questions or support, please open an issue in the GitHub repository or contact the project maintainer.

---

Happy coding!

