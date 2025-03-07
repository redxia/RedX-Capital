import yfinance as yf

def download_data(symbol):
    yf.download(symbol, period="max",progress=False)