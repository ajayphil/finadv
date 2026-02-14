from fastapi.testclient import TestClient
from app.main import app
import app.market as market

client = TestClient(app)


def test_market_quote_and_history(monkeypatch):
    # Monkeypatch market functions to avoid network/yfinance in tests
    monkeypatch.setattr(market, 'get_quote', lambda symbol: {'symbol': symbol, 'price': 123.45, 'shortName': 'Mock Co', 'currency':'USD'})
    monkeypatch.setattr(market, 'get_history', lambda symbol, period='1mo': {'symbol': symbol, 'period': period, 'history':[{'date':'2026-02-01','close':120.0}]})

    r = client.get('/market/quote', params={'symbol':'MOCK'})
    assert r.status_code == 200
    data = r.json()
    assert data['symbol'] == 'MOCK'
    assert data['price'] == 123.45

    r2 = client.get('/market/history', params={'symbol':'MOCK','period':'1mo'})
    assert r2.status_code == 200
    h = r2.json()
    assert h['symbol']=='MOCK'
    assert isinstance(h['history'], list)
    assert h['history'][0]['close'] == 120.0
