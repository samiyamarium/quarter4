import requests

BINANCE_ALL_PRICES_URL = "https://api.binance.com/api/v3/ticker/price"
BINANCE_SINGLE_PRICE_URL = "https://api.binance.com/api/v3/ticker/price?symbol="

def get_all_prices():
    try:
        response = requests.get(BINANCE_ALL_PRICES_URL)
        response.raise_for_status()
        data = response.json()

        print("\nTop 10 Crypto Prices:")
        for coin in data[:10]:
            print(f"{coin['symbol']}: {coin['price']} USD")
    except requests.RequestException as e:
        print(f"Error fetching all prices: {e}")

def get_single_price(symbol):
    try:
        url = BINANCE_SINGLE_PRICE_URL + symbol.upper()
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        print(f"\nLive Price of {symbol.upper()}: {data['price']} USD")
    except requests.RequestException as e:
        print(f"Error fetching price for {symbol}: {e}")
    except KeyError:
        print(f"Invalid symbol or no data found for {symbol}.")

def main():
    print("📊 Welcome to the Crypto Price Agent (Binance API)")
    get_all_prices()

    while True:
        symbol = input("\nEnter a coin symbol (like BTCUSDT) to get live price (or 'exit' to quit): ")
        if symbol.lower() == 'exit':
            print("Goodbye!")
            break
        get_single_price(symbol)

if __name__ == "__main__":
    main()
