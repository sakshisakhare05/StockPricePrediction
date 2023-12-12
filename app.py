# Import necessary libraries
import joblib
import yfinance as yf
import numpy as np
import pandas as pd
from datetime import date
import streamlit as st
import plotly.express as px
import sqlite3
from passlib.hash import pbkdf2_sha256

ticker = 'AAPL'
model = joblib.load(r'C:\Users\Dell\Stock_Price\linear_regression_model.pkl')

# # Function to predict stock prices
# def predict_stock_prices(open_price, volume):
#     # Assume that the model takes open price and volume as features
#     features = np.array([[open_price, volume]])

#     # Make predictions using the loaded linear regression model
#     predicted_price = model.predict(features)

#     return predicted_price[0]

# Function to fetch historical stock data
def get_stock_history(ticker, start_date, end_date):
    stock_data = yf.download(ticker, start=start_date, end=end_date)
    return stock_data

# Function to create a table for users if it doesn't exist
def create_users_table():
    conn = sqlite3.connect("user_database.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()

    # Function to register a new user
def register_user(username, password):
    conn = sqlite3.connect("user_database.db")
    cursor = conn.cursor()

    # Hash the password before storing it in the database
    hashed_password = pbkdf2_sha256.hash(password)

    cursor.execute('''
        INSERT INTO users (username, password)
        VALUES (?, ?)
    ''', (username, hashed_password))

    conn.commit()
    conn.close()

# Function to authenticate the user
def authenticate(username, password):
    conn = sqlite3.connect("user_database.db")
    cursor = conn.cursor()
    cursor.execute('''
        SELECT password FROM users
        WHERE username = ?
    ''', (username,))

    result = cursor.fetchone()

    conn.close()

    if result and pbkdf2_sha256.verify(password, result[0]):
        return True
    else:
        return False

# Streamlit app code
def main():
    # Set the title of the app
     st.sidebar.subheader('Query parameters')  
     start_date = st.sidebar.date_input("Start date")
     end_date = st.sidebar.date_input("End date")
     st.title("Stock Price Prediction")

     create_users_table()

     page = st.sidebar.radio("Choose your action", ["Login", "Register"])

     if page == "Register":
        st.subheader("Register")
        new_username = st.text_input("Username")
        new_password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        if st.button("Register"):
            if new_password == confirm_password:
                register_user(new_username, new_password)
                st.success("Registration successful! Please log in.")
            else:
                st.error("Passwords do not match. Please try again.")

     elif page == "Login":
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if authenticate(username, password):
                st.success(f"Welcome, {username}!")
            else:
                st.error("Invalid username or password. Please try again.")


   
     

     # User input for company name
     ticker = st.text_input("Enter Company Name and Press Enter:")
     if not ticker:
        st.warning("Please enter a valid stock ticker.")
        st.stop()

    # Fetch historical stock data
     try:
        stock_history = get_stock_history(ticker, start_date, end_date)
     except Exception as e:
        st.error(f"Error fetching stock data: {e}")
        st.stop()

    # Display the historical stock data
     st.subheader(f"Historical Stock Data for {ticker}")
     st.write(stock_history)

    # Plot historical stock prices
     st.subheader(f"Historical Stock Prices for {ticker}")
     fig = px.line(stock_history, x=stock_history.index, y='Close', title=f'Historical Stock Prices for {ticker}')
     st.plotly_chart(fig)

    #  fig1 = px.scatter(stock_history, close='Close', predicted='Predicted', trendline="ols", 
    #                      labels={'Close': 'Actual Price', 'Predicted': 'Predicted Price'},
    #                      title=f'Actual vs. Predicted Stock Prices for {ticker}')
    #  st.plotly_chart(fig1)


    
if __name__ == "__main__":
    main()
