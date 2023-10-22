import pandas as pd
import ta
from pycoingecko import CoinGeckoAPI
import streamlit as st

# Initialize CoinGecko API client
cg = CoinGeckoAPI()

def get_historical_data(crypto):
    try:
        data = cg.get_coin_market_chart_by_id(crypto, vs_currency='usd', days=30)
        df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        return df
    except:
        st.warning(f"Failed to fetch data for {crypto}.")
        return None

def calculate_indicators(data):
    data['SMA'] = ta.trend.sma_indicator(data['price'], window=14)
    data['RSI'] = ta.momentum.RSIIndicator(data['price']).rsi()
    data['MACD'] = ta.trend.MACD(data['price']).macd()
    data['MACD Signal'] = ta.trend.MACD(data['price']).macd_signal()
    return data

def trading_signals(data):
    signals = []
    for i in range(len(data)):
        if i == 0:
            signals.append('Hold')
        elif data['MACD'][i] > data['MACD Signal'][i] and data['MACD'][i - 1] <= data['MACD Signal'][i - 1]:
            signals.append('Buy')
        elif data['MACD'][i] < data['MACD Signal'][i] and data['MACD'][i - 1] >= data['MACD Signal'][i - 1]:
            signals.append('Sell')
        else:
            signals.append('Hold')
    data['Signal'] = signals
    return data

def main():
    st.title("Crypto Trading Bot")

    # Get historical data
    crypto_choice = st.selectbox("Select Cryptocurrency", ["bitcoin", "ethereum", "litecoin"])
    data = get_historical_data(crypto_choice)

    if data is not None:
        # Calculate indicators
        data = calculate_indicators(data)

        # Determine trading signals
        data = trading_signals(data)

        # Display data and signals
        st.write(data)

        # Plot price, SMA, and MACD
        st.header("Price and SMA")
        st.line_chart(data[['price', 'SMA']])
        st.header("MACD and MACD Signal")
        st.line_chart(data[['MACD', 'MACD Signal']])

if __name__ == "__main__":
    main()

