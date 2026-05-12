"""
Algorithmic Stock Trading Signal App
Uses Yahoo Finance (yfinance) for real stock data.
SMA crossover strategy: Short SMA (20-day) vs Long SMA (50-day).
BUY when short crosses above long, SELL when short crosses below.
"""

import tkinter as tk
from tkinter import messagebox
import threading #This will help fetch stock data without freezing the window
import yfinance as yf #Import yahoo finance for stock data
import pandas as pd #Commonly used for data analysis, imported so I can store and work with stock price data with DataFrames (for rows and columns) and Series.
from datetime import datetime, timedelta


#Custom Functions 

def calculate_sma(prices: pd.Series, window: int) -> pd.Series:
    """
    Calculate Simple Moving Average over a given window.
    """
    #Use panda's imports, rolling(window=window) to create a moving window over the price data, mean() to display the mean.
    return prices.rolling(window=window).mean()


def generate_signals(prices: pd.Series, short_window=20, long_window=50) -> pd.DataFrame:
    """
    Build a DataFrame with SMA columns and crossover signals.
    Signal = 1 means BUY crossover, -1 means SELL crossover.
    """

    
    df = pd.DataFrame({"Close": prices}) #Create a new panda DataFrame with one column called "Close" to store the stock's closing price
    df["SMA_Short"] = calculate_sma(prices, short_window) #Calculate the short simple moving average using the default 20 day window
    df["SMA_Long"] = calculate_sma(prices, long_window) #Similarly calculate the long SMA, using the default 50 day window.
    df["Position"] = 0 #Default that the stock is not bullish
    df.loc[df["SMA_Short"] > df["SMA_Long"], "Position"] = 1 #If short SMA > long SMA, set to bullish.
    df["Signal"] = df["Position"].diff() #Compare the positions and return the 0 and -1 signal
    return df


def get_recommendation(df: pd.DataFrame) -> tuple[str, str]:
    """
    Return a recommendation and description based on the latest SMA values.
    Returns a tuple of (recommendation, description).
    """

    
    latest    = df.dropna().iloc[-1] #Drop any rows with missing values (the beginning of the 50-day average)

    #Store each of the latest values
    short_val = latest["SMA_Short"] 
    long_val = latest["SMA_Long"]
    close_val = latest["Close"]

    #If the short moving average is above the long, the stock is showing bullish
    if short_val > long_val:
        rec = "BUY / HOLD LONG"
        desc = (f"Short SMA ({short_val:.2f}) is above Long SMA ({long_val:.2f}).\n" #F strings to explain buy/hold recommendation
                f"Current price: ${close_val:.2f} — Bullish momentum.")
    
    #If it's the opposite, it's bearish
    elif short_val < long_val:
        rec = "SELL / STAY OUT"
        desc = (f"Short SMA ({short_val:.2f}) is below Long SMA ({long_val:.2f}).\n"
                f"Current price: ${close_val:.2f} — Bearish momentum.")
        
    #If it's equal, it's neutral
    else:
        rec = "NEUTRAL"
        desc = f"Short and Long SMAs are equal. Current price: ${close_val:.2f}."

    return rec, desc


def fetch_and_analyze(ticker: str) -> tuple[str, str]:
    """Download 1 year of stock data and return a recommendation."""

    end = datetime.today() #Set the end as today
    start = end - timedelta(days=365) #Set the beginning as a year prior

    #Download the stock data from yahoo
    data   = yf.download(
        ticker, 
        start=start,
        end=end, 
        auto_adjust=True #adjusts prices for things like stock splits or dividends
    )
    #If no data, the ticker may be invalid.
    if data.empty:
        raise ValueError(f"No data found for '{ticker}'. Check the ticker symbol.")
    
    #Get only the Close column from the downloaded data, squeeze() to ensure the data is panda's Series rather than a dataframe
    prices = data["Close"].squeeze()
    df = generate_signals(prices) #Call our previous signal function with our prices variable
    return get_recommendation(df) #Return with the call of our recommendation function with what we recieved from the signal function

#App start

class StockApp:
    
    """
    This class creates the tkinter stock trading signal app.

    It builds the window, collects the ticker symbol from the user,
    runs the stock analysis, and displays the result.
    """
    
    #Define our main window and all the widgets inside
    def __init__(self, root):
        self.root = root #Store the main tkinter window so other methods can use it
        self.root.title("Stock Signal App") #Set the title

        #Create a label that tells the user where to enter the ticker symbol
        tk.Label(root, text="Ticker Symbol:").grid(
            row=0, 
            column=0, 
            padx=10, 
            pady=10
        )
       
        self.ticker_entry = tk.Entry(root, width=12) #Create an entry box where the user types a stock ticker
        
        #Place the entry box in the first row of the second column
        self.ticker_entry.grid(
            row=0, 
            column=1, 
            padx=5, 
            pady=10
        )

        self.ticker_entry.insert(0, "AAPL") #Use AAPL as a default for the entry box so the app has an example ticker

        #Analyze button
        tk.Button(
            root, 
            text="Analyze", 
            command=self._run).grid( #If the user clicks, run the _run method, and display the following in the window
            row=0, 
            column=2, 
            padx=10, 
            pady=10
        )

        #Label to display the main  recommendation (our previously made BUY / HOLD variables we returned)
        self.rec_label = tk.Label(
            root, 
            text="", 
            font=("TkDefaultFont", 14, "bold")
        )
        
        #Place the recommendation label underneath the input row
        self.rec_label.grid(
            row=1, 
            column=0, 
            columnspan=3, #Use so the text properly spans the box
            pady=(10, 4)
        )
        
        #Place the explanation for the recommendation
        self.desc_label = tk.Label(
            root, 
            text="", 
            justify="center"
        )
        
        #Place the description label below the recommendation label
        self.desc_label.grid(
            row=2, 
            column=0, 
            columnspan=3, 
            pady=(0, 10)
        )
        
        #Give the user status updates (the text is to be changed using .config())
        self.status_label = tk.Label(
            root, 
            text="Enter a ticker and click Analyze."
        
        )
        
        #And finally, we have the status label at the very bottom
        self.status_label.grid(
            row=3, 
            column=0, 
            columnspan=3, 
            pady=(0, 10)
        )

    def _run(self):
        """
        This method runs when the user clicks the Analyze button.

        It gets the ticker symbol, checks that something was entered,
        clears old results, and starts the analysis in a separate thread.
        """

        ticker = self.ticker_entry.get().strip().upper() #Get the ticker from the entry box, strip() to remove extra spaces, and convert it to uppercase.

        #Default case if the user enters nothing
        if not ticker:
            messagebox.showerror("Error", "Please enter a ticker symbol.") #Use specially imported messagebox to use showerror
            return
        
        self.status_label.config(text="Fetching data...") #Inform the user that the app is fetching the data

        #Clear any old text
        self.rec_label.config(text="") 
        self.desc_label.config(text="")
        
        #Use the imported "threading" to begin a new background thread to run the stock analysis
        #I wanted to use this to stop the window from freezing while the data downloads
        threading.Thread(
            target=self._analyze, 
            args=(ticker,), 
            daemon=True).start() #Close automatically when the app closes

    def _analyze(self, ticker):
        """
        This method performs the stock analysis.

        It is run in a background thread so the app stays responsive.
        """

        #Because we fetch real data from yfinance, we use a try/except here, as when you depend on outside data a lot can go wrong.
        try:
            rec, desc = fetch_and_analyze(ticker) #Download the stock data and get the recommendation with our created function
            #Schedule the function to run as soon as tkinter gets the chance, don't delay it, and use
            #lambda to ensure the function does not immediately run and stop more important processes
            self.root.after(0, lambda: self._show_result(rec, desc)) 
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e))) #If anything goes wrong, show the error in a popup message instead using messagebox
            self.root.after(0, lambda: self.status_label.config(text="Ready.")) #Also change the status label back to ready

    def _show_result(self, rec, desc):
        self.rec_label.config(text=rec) #Show the recommendation, such as BUY / HOLD LONG
        self.desc_label.config(text=desc) #Show the explanation
        self.status_label.config(text="Done.") #And tell the user that the analysis is done

#If the file is being run directly, create the app window.
if __name__ == "__main__":
    root = tk.Tk()
    StockApp(root) #Create an instance of the StockApp class class and pass it the main window
    root.mainloop() #Start the tkinter loop
