import pandas as pd
from typing import Dict

import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')
plt.rcParams.update({'font.size': 8})


def graphic_plot(portfolio: pd.DataFrame, market: pd.DataFrame, title: str) -> plt.Figure:
    """Plots the portfolio and market returns over time.

    Args:
        portfolio (pd.DataFrame): A pandas DataFrame containing the portfolio returns.
        market (pd.DataFrame): A pandas DataFrame containing the market returns.
        title (str): The title of the plot.

    Returns:
        plt.Figure: A matplotlib Figure object containing the plot.
    """

    first_date = portfolio.index[0].date()
    last_date = portfolio.index[-1].date()
    
    fig, ax = plt.subplots(figsize=(6, 4), dpi=300) 
    
    ax.plot(portfolio, linewidth=1, label='Portfolio')
    ax.plot(market, linewidth=1, label='Market')
    
    ax.set_title(f"{title} from {first_date} to {last_date}", fontdict={'fontsize':8})
    
    ax.set_xlabel('Date', fontdict={'fontsize':8})
    ax.set_ylabel(title, fontdict={'fontsize':8})
    
    ax.legend()
    plt.close()
    
    return fig


def allocation_plot(title: str, allocation: Dict) -> plt.Figure:
    """Plots a pie chart of the asset allocation for a given year.

    Args:
        title (str): The title of the pie chart.
        allocation (Dict): A dictionary containing the asset allocation weights.

    Returns:
        plt.Figure: A matplotlib Figure object containing the pie chart.
    """
    
    fig, ax = plt.subplots(figsize=(7, 7), dpi=300)
    
    sizes = list(allocation.values())
    sizes.append(1 - sum(sizes))
    labels = list(allocation.keys()) + ['Cash']
    
    ax.pie(sizes, labels=labels, autopct='%.2f%%')
    ax.set_title(title, fontdict={'fontsize':8})
    
    plt.close()
    
    return fig