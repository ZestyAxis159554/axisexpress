from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import asyncio
import aiohttp
import yfinance as yf
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading')

async def fetch_stock(session, ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d", interval="1m")
        if not hist.empty:
            open_price = hist['Open'][0]
            current_price = hist['Close'][-1]
            change = (current_price - open_price) / open_price
            return ticker, change
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
    return ticker, -float('inf')

async def get_top_stock(tickers):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_stock(session, ticker) for ticker in tickers]
        results = await asyncio.gather(*tasks)
        
        best_stock = None
        best_change = -float('inf')
        for ticker, change in results:
            if change > best_change:
                best_change = change
                best_stock = ticker
        return best_stock

tickers = ['AAPL', 'MSFT', 'GOOG', 'AMZN']  # İzlemek istediğiniz hisseleri buraya ekleyin

async def update_stock():
    while True:
        top_stock = await get_top_stock(tickers)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        socketio.emit('update', {'time': now, 'stock': top_stock})
        await asyncio.sleep(1)  # Her saniye güncelleme

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(update_stock())
    socketio.run(app)
