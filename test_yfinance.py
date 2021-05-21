import yfinance as yf

msft = yf.Ticker("MSFT")

#Prints stock info
print(msft.info)