import yfinance as yf

def get_quote(symbol: str):
    """Return a small summary quote for a ticker symbol."""
    t = yf.Ticker(symbol)
    info = t.info if hasattr(t, 'info') else {}
    price = None
    try:
        price = t.history(period='1d')['Close'].iloc[-1]
    except Exception:
        price = None
    return {
        'symbol': symbol,
        'shortName': info.get('shortName') or info.get('longName'),
        'currency': info.get('currency'),
        'price': float(price) if price is not None else None,
    }

def get_history(symbol: str, period: str = '1mo'):
    """Return historical close prices for a symbol and period."""
    t = yf.Ticker(symbol)
    hist = t.history(period=period)
    # convert to simple list of date/close
    data = []
    for idx, row in hist.iterrows():
        data.append({'date': idx.strftime('%Y-%m-%d'), 'close': float(row['Close'])})
    return {'symbol': symbol, 'period': period, 'history': data}
