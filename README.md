# PortFin

## Project Overview

PortFin is a project designed to compare the performance of dynamically allocated investment portfolios with the market. It leverages historical data to generate new portfolios each year and allocates assets accordingly.

## Usage

You can run the script `main.py` with the following command line options:

- `-h, --help`: Show the help message and exit.

- `-y YEARS, --years YEARS`: Number of years of data to download.

- `-w WINDOW, --window WINDOW`: Number of years needed to backtest the stock.

- `-o OPTIMIZER, --optimizer OPTIMIZER`: The optimizer to use, choose from `max_sharpe` or `min_volatility`. The default is `max_sharpe`.

- `-g GAMMA, --gamma GAMMA`: The regularization parameter. The default is 0.1.

- `-m MONEY, --money MONEY`: The initial investment amount. The default is 1000.

- `-n NAME, --name NAME`: The name of the PDF report. The default is `report.pdf`.

- `-f, --full`: Whether to generate a full report or not. Default is `False`.

## Example Usage

```bash
python main.py -y 5 -w 2 -o max_sharpe -g 0.2 -m 5000 -n my_portfolio_report.pdf -f
```
