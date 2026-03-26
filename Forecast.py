import pandas as pd
import numpy as np
# Load dataset
sales_data = pd.read_csv("online_retail_clean.csv", encoding='ISO-8859-1')

# Look at first rows
print(sales_data.head())
# Check structure
print(sales_data.info())
# Summary statistics
print(sales_data.describe())


# Convert date column to datetime format
sales_data['InvoiceDate'] = pd.to_datetime(sales_data['InvoiceDate'])

# Set date as index
sales_data = sales_data.set_index('InvoiceDate')

# Resample to monthly revenue
monthly_sales = sales_data['Revenue'].resample('ME').sum()

print(monthly_sales)

monthly_sales = monthly_sales.reset_index()

# Create time-based features
monthly_sales['time_index'] = range(len(monthly_sales))
monthly_sales['month'] = monthly_sales['InvoiceDate'].dt.month
monthly_sales['year'] = monthly_sales['InvoiceDate'].dt.year

print(monthly_sales.head())

from sklearn.linear_model import LinearRegression

# Input
X = monthly_sales[['time_index', 'month', 'year']]

# Target
y = monthly_sales['Revenue']

# Train model
model = LinearRegression()
model.fit(X, y)

# Creating future sales data

# Number of months to predict
future_steps = 12

# Last date in dataset
last_date = monthly_sales['InvoiceDate'].max()

# Generate future dates
future_dates = pd.date_range(
    start=last_date,
    periods=future_steps + 1,
    freq='ME'
)[1:]

# Create future dataframe
future_sales_data = pd.DataFrame({
    'InvoiceDate': future_dates
})

# Create same features
future_sales_data['time_index'] = range(len(monthly_sales), len(monthly_sales) + future_steps)
future_sales_data['month'] = future_sales_data['InvoiceDate'].dt.month
future_sales_data['year'] = future_sales_data['InvoiceDate'].dt.year

print(future_sales_data)

forecast = model.predict(
    future_sales_data[['time_index', 'month', 'year']]
)

future_sales_data['Forecast'] = forecast

print(future_sales_data)

import matplotlib.pyplot as plt

# Plot historical data
plt.plot(
    monthly_sales['InvoiceDate'],
    monthly_sales['Revenue'],
    label='Actual'
)

# Plot forecast
plt.plot(
    future_sales_data['InvoiceDate'],
    future_sales_data['Forecast'],
    label='Forecast'
)

plt.xlabel('Date')
plt.ylabel('Revenue')
plt.title('Sales Forecast (Linear Regression)')
plt.legend()

plt.show()


from sklearn.ensemble import RandomForestRegressor

# The same data (X, y)
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)

rf_model.fit(X, y)

# Future forecast
rf_forecast = rf_model.predict(
    future_sales_data[X.columns]
)

future_sales_data['RF_Forecast'] = rf_forecast

print("Random Forest predictions:")
print(future_sales_data[['InvoiceDate', 'RF_Forecast']])

# =========================
# PLOT COMPARISON
# =========================

plt.plot(
    monthly_sales['InvoiceDate'],
    monthly_sales['Revenue'],
    label='Actual'
)

plt.plot(
    future_sales_data['InvoiceDate'],
    future_sales_data['Forecast'],
    label='Linear Regression'
)

plt.plot(
    future_sales_data['InvoiceDate'],
    future_sales_data['RF_Forecast'],
    label='Random Forest'
)

plt.xlabel('Date')
plt.ylabel('Revenue')
plt.title('Sales Forecast Comparison')
plt.legend()

plt.show()

product_sales_data = sales_data.groupby('StockCode').agg({
    'Revenue': 'sum',
    'Quantity': 'sum',
    'Invoice': 'count'
}).reset_index()

# Rename columns for clarity
product_sales_data.columns = [
    'StockCode',
    'total_revenue',
    'total_quantity',
    'num_transactions'
]

print(product_sales_data.head())

# Bottom 25% revenue = bad products
threshold = product_sales_data['total_revenue'].quantile(0.25)

product_sales_data['bad_product'] = (
    product_sales_data['total_revenue'] <= threshold
).astype(int)

print(product_sales_data.head())

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

# Features (inputs)
X = product_sales_data[['total_quantity', 'num_transactions']]

# Target (what we predict)
y = product_sales_data['bad_product']

# Split into train and test data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Create model
model = RandomForestClassifier(n_estimators=100, random_state=42)

# Train model
model.fit(X_train, y_train)

# Predictions
y_pred = model.predict(X_test)

# Evaluate
print(classification_report(y_test, y_pred))


importances = model.feature_importances_
features = X.columns

plt.bar(features, importances)
plt.title("Feature Importance")
plt.show()
