from io import BytesIO
import matplotlib.pyplot as plt
import pandas as pd
from helpers_allocation import get_cumulative_returns


def graph_portfolio_market(portfolio: pd.DataFrame, market: pd.DataFrame, title: str) -> BytesIO:
    """Generates a graph of the cumulative returns of a portfolio and a market index.

    Args:
        portfolio (pd.DataFrame): A pandas DataFrame containing the portfolio returns.
        market (pd.DataFrame): A pandas DataFrame containing the market returns.
        title (str): The title of the graph.

    Returns:
        BytesIO: A BytesIO object containing the graph image.
    """

    first_date = portfolio.index[0]
    last_date = portfolio.index[-1]
    
    cum_returns_portfolio = get_cumulative_returns(portfolio)
    cum_returns_market = get_cumulative_returns(market.loc[first_date:last_date])
    
    fig, ax = plt.subplots(figsize=(6, 4), dpi=300) 
    
    ax.plot(cum_returns_portfolio, linewidth=2, label='Portfolio')
    ax.plot(cum_returns_market["Close"], linewidth=2, label='Market')
    
    ax.set_title(title)
    
    ax.set_xlabel('Date')
    ax.set_ylabel('Returns')
    
    ax.legend()
    
    img_stream = BytesIO()
    fig.savefig(img_stream, format='png', dpi=300, bbox_inches='tight')
    img_stream.seek(0)
    plt.close()
    
    return img_stream