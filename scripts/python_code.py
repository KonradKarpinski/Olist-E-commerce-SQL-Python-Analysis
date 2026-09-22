#========================
#Loading Data & Libraries
#========================

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
import seaborn as sns
from scipy.stats import pearsonr

customers = pd.read_csv("olist_customers_dataset.csv")
geolocation = pd.read_csv("olist_geolocation_dataset.csv")
order_items = pd.read_csv("olist_order_items_dataset.csv")
order_payments = pd.read_csv("olist_order_payments_dataset.csv")
order_reviews = pd.read_csv("olist_order_reviews_dataset.csv")
orders = pd.read_csv("olist_orders_dataset.csv")
products = pd.read_csv("olist_products_dataset.csv")
sellers = pd.read_csv("olist_sellers_dataset.csv")
category_translation = pd.read_csv("product_category_name_translation.csv")

pd.set_option('display.max_rows', None)      
pd.set_option('display.max_columns', None)   
pd.set_option('display.width', None)         
pd.set_option('display.max_colwidth', None) 

#=======================================
#Task 0: Data Cleaning & Data Validation
#=======================================

#MISSING VALUES - CHECKING

print(customers.isna().any())
print(geolocation.isna().any())
print(order_items.isna().any())
print(order_payments.isna().any())
print(order_reviews.isna().any())
print(orders.isna().any())
print(products.isna().any())
print(sellers.isna().any())
print(category_translation.isna().any())

#INSPECTING ORDERS DATASET

print(orders.isna().sum())
unique_values_order_status = orders['order_status'].unique()
print(unique_values_order_status)

print(orders[orders['order_status'] == 'approved'])
print(orders[orders['order_status'] == 'created'])
print(orders[orders['order_status'] == 'canceled'])
print(orders[orders['order_status'] == 'unavailable'])
print(orders[orders['order_status'] == 'processing'])
print(orders[orders['order_status'] == 'shipped'])
print(orders[orders['order_status'] == 'invoiced'])

#INSPECTING DELIVERED ORDERS

delivered_orders = orders[orders['order_status'] == 'delivered']
print(delivered_orders.isna().any())
print(orders.head())

#DROPPING MISSING VALUES - DELIVERED ORDERS WITH MISSING VALUES (MISSING VALUES IN OTHER ORDER STATUS' ARE ACCEPTABLE)

indexes_to_drop = orders[(orders['order_status'] == 'delivered') & (orders.isna().any(axis=1))].index
orders = orders.drop(indexes_to_drop)
print(orders.isna().sum())

#INSPECTING PRODUCTS DATASET

print(products.head())
print(products.isna().sum())

rows_with_na = products[products['product_weight_g'].isna()]
print(rows_with_na.head())

rows_with_na_2 = products[products['product_name_lenght'].isna()]
print(rows_with_na_2.head())

#FILLING MISSING VALUES - PRODUCT CATEGORY

products['product_category_name'] = products['product_category_name'].fillna('Unknown')
print(products.isna().sum())

#FILLING MISSING VALUES - PRODUCTS' PHYSICAL DIMENSIONS

dimensions = ['product_weight_g', 'product_length_cm', 'product_height_cm', 'product_width_cm']

for col in dimensions:
    products[col] = products[col].fillna(
        products.groupby('product_category_name')[col].transform('median')
    )

    global_median = products[col].median()
    products[col] = products[col].fillna(global_median)

print(products.isna().sum())

#DATA VALIDATION

print(customers.head())

print(geolocation.head())
print((geolocation['geolocation_zip_code_prefix'] < 0).any())

print(order_items.head())
print((order_items['price'] < 0).any())
print((order_items['freight_value'] < 0).any())

print(order_payments.head())
print((order_payments['payment_value'] < 0).any())

print(order_reviews.head())
review_scores = [1, 2, 3, 4, 5]
print((~order_reviews['review_score'].isin(review_scores)).any())

print(orders.head())
print((orders['order_delivered_carrier_date'] > orders['order_delivered_customer_date']).any())
orders_checking = orders['order_delivered_carrier_date'] > orders['order_delivered_customer_date']
print(orders[orders_checking])

print(products.head())
print((products['product_weight_g'] < 0).any())
print((products['product_length_cm'] < 0).any())
print((products['product_height_cm'] < 0).any())
      
print(sellers.head())
print(category_translation.head())

#DROPPING ROWS WITH DATA ANOMALIES

invalid_dates_index = orders[orders['order_delivered_carrier_date'] > orders['order_delivered_customer_date']].index
orders = orders.drop(invalid_dates_index)
print((orders['order_delivered_carrier_date'] > orders['order_delivered_customer_date']).any())

#CHECKING FOR DATA DUPLICATES

print("Customers:", customers.duplicated().sum())
print("Geolocation:", geolocation.duplicated().sum())
print("Order Items:", order_items.duplicated().sum())
print("Order Payments:", order_payments.duplicated().sum())
print("Order Reviews:", order_reviews.duplicated().sum())
print("Orders:", orders.duplicated().sum())
print("Products:", products.duplicated().sum())
print("Sellers:", sellers.duplicated().sum())
print("Category Translation:", category_translation.duplicated().sum())

#DROPPING DUPLICATES

geolocation = geolocation.drop_duplicates()

#UPLOADING UPDATED PYTHON DATABASE TO SQL
 
engine = create_engine('sqlite:///olist_cleaned.db')

orders.to_sql('olist_orders_dataset', con=engine, if_exists='replace', index=False)
products.to_sql('olist_products_dataset', con=engine, if_exists='replace', index=False)
customers.to_sql('olist_customers_dataset', con=engine, if_exists='replace', index=False)
order_items.to_sql('olist_order_items_dataset', con=engine, if_exists='replace', index=False)
order_payments.to_sql('olist_order_payments_dataset', con=engine, if_exists='replace', index=False)
order_reviews.to_sql('olist_order_reviews_dataset', con=engine, if_exists='replace', index=False)
geolocation.to_sql('olist_geolocation_dataset', con=engine, if_exists='replace', index=False)
sellers.to_sql('olist_sellers_dataset', con=engine, if_exists='replace', index=False)
category_translation.to_sql('product_category_name_translation', con=engine, if_exists='replace', index=False)

#EXPORTING UPDATED DATA FILES FOR EXCEL AND EXCEL POWER QUERY ANALYSIS

orders.to_csv('olist_orders_cleaned.csv', index=False)
order_payments.to_csv('olist_order_payments_cleaned.csv', index=False)
order_items.to_csv('olist_order_items_cleaned.csv', index=False)
customers.to_csv('olist_customers_cleaned.csv', index=False)

#============================================================
#Task 1: Revenue & Sales Trend / Step B: Smoothed Sales Trend
#============================================================

dataframe_merged = pd.merge(orders, order_items, how='left', on='order_id')

dataframe_merged['daily_sale'] = dataframe_merged['price'] + dataframe_merged['freight_value']
dataframe_merged['order_purchase_timestamp'] = pd.to_datetime(dataframe_merged['order_purchase_timestamp'])
dataframe_merged['order_date'] = dataframe_merged['order_purchase_timestamp'].dt.date

dataframe_merged_grouped = (dataframe_merged.groupby('order_date').agg({'daily_sale': 'sum'}).sort_values(by=['order_date'], ascending=[True]))
dataframe_merged_grouped['rolling_mean_7d'] = dataframe_merged_grouped['daily_sale'].rolling(window=7).mean()

p6 = sns.relplot(
    data=dataframe_merged_grouped,
    x='order_date',
    y='rolling_mean_7d',
    kind='line',       
)

p6.fig.suptitle('Store Sales Trend (7-Day Rolling Average)', y=0.99)
p6.set_axis_labels('Order Date', 'Sale')
plt.xticks(rotation=45)
plt.show()

#==================================================================
#Task 2: Product portfolio & Profitability / Step B: Margin killers 
#==================================================================

merged_df = pd.merge(orders, order_reviews, how='left', on='order_id')
merged_df = pd.merge(merged_df, order_items, how='left', on='order_id')
merged_df = pd.merge(merged_df, products, how='left', on='product_id')
merged_df = pd.merge(merged_df, category_translation, how='left', on='product_category_name')

merged_df['revenue'] = merged_df['price'] + merged_df['freight_value']
merged_df_grouped = (merged_df.groupby('product_category_name_english').agg({'revenue':'sum','review_score':'mean'})                )
top_20_revenue = merged_df_grouped.nlargest(20, 'revenue')
merged_df_grouped_top10 = top_20_revenue.nsmallest(10, 'review_score')
print(merged_df_grouped_top10)

p5 = sns.catplot(
    x='product_category_name_english', 
    y='revenue', 
    data=merged_df_grouped_top10, 
    kind='bar', 
    hue='review_score',
)

p5.fig.suptitle('Product categories with the highest revenue and worst reviews', y=0.99)
p5.set_axis_labels('Product category', 'Revenue per product category [mln]')
plt.xticks(rotation=45, ha='right')
plt.subplots_adjust(bottom=0.3)
plt.show()

#=======================================================================
#Task 3: Logistics & Delivery Performance / Step C: Delivery Bottlenecks
#=======================================================================

print(orders.head())
print(customers.head())
print(geolocation.head())

df_merged = pd.merge(orders, customers, how='inner', on='customer_id')
print(df_merged.shape)
df_merged['order_delivered_customer_date'] = pd.to_datetime(df_merged['order_delivered_customer_date'])
df_merged['order_delivered_carrier_date'] = pd.to_datetime(df_merged['order_delivered_carrier_date'])
df_merged['delivery_time_days'] = (df_merged['order_delivered_customer_date'] - df_merged['order_delivered_carrier_date']).dt.days
print(df_merged['delivery_time_days'].head())

five_worst_states = df_merged.groupby('customer_state')['delivery_time_days'].mean().sort_values(ascending=False).head(5)
print(five_worst_states)
worst_states_names = five_worst_states.index
df_top_5_states = df_merged[df_merged['customer_state'].isin(worst_states_names)]

#BOXPLOT 1 - DELIVERY TIME DISTRIBUTION ACROSS 5 WORST STATES

p1 = sns.catplot(
    data=df_top_5_states, 
    x='customer_state', 
    y='delivery_time_days', 
    kind='box',
    order=worst_states_names 
)

p1.fig.suptitle('Delivery time distribution across 5 worst states', y=0.99)
p1.set_axis_labels('State', 'Delivery time (days)')
plt.show()

print(orders.head())

#SCATTERPLOT 1 - CORRELATION BETWEEN FREIGHT VALUE AND DELIVERY TIME

print(order_items.head())

df_merged = pd.merge(df_merged, order_items[['order_id', 'freight_value', 'seller_id']], on='order_id', how='left')

p2 = sns.relplot(
    data=df_merged, 
    x='freight_value', 
    y='delivery_time_days',
    kind = 'scatter')

p2.fig.suptitle('Correlation between freight value and delivery time', y=0.99)
p2.set_axis_labels('Freight value', 'Delivery time (days)')
plt.show()

df_clean = df_merged.dropna(subset=['freight_value', 'delivery_time_days'])
correlation, p_value = pearsonr(df_clean['freight_value'], df_clean['delivery_time_days'])
print(f"Correlation coefficient: {round(correlation, 3)}")
print(f"P-value: {round(p_value, 5)}")

#BOXPLOT 2 - DELIVERY TIME: LOCAL VS INTERSTATE

df_merged = pd.merge(df_merged, sellers[['seller_id', 'seller_state']], on='seller_id', how='left')

df_merged['is_local'] = df_merged['customer_state'] == df_merged['seller_state']

p3 = sns.catplot(
    data=df_merged, 
    x='is_local', 
    y='delivery_time_days', 
    kind='box'
)

p3.fig.suptitle('Delivery time: Local (True) vs Interstate (False)', y=0.99)
p3.set_axis_labels('Is delivery local?', 'Delivery time (days)')
plt.show()

#==========================================================================
#Task 4: Customer Retention & Lifecycle / Step B: Customer Retention Window
#==========================================================================

print(customers.head())

df_retention = pd.merge(orders, customers, how='inner', on='customer_id')

returning_customers = df_retention[df_retention.groupby('customer_unique_id')['customer_id'].transform('count') >= 2]
returning_customers['order_purchase_timestamp'] = pd.to_datetime(returning_customers['order_purchase_timestamp'])

returning = returning_customers.sort_values(by='order_purchase_timestamp')
returning = returning.set_index('customer_unique_id')

date_of_first_purchase = returning.groupby('customer_unique_id')['order_purchase_timestamp'].nth(0)
date_of_second_purchase = returning.groupby('customer_unique_id')['order_purchase_timestamp'].nth(1)

customer_retention_window = (date_of_second_purchase - date_of_first_purchase).dt.days
print(customer_retention_window.head())

customer_retention_window_days = customer_retention_window.reset_index(name='days till second purchase')
customer_retention_window_days = customer_retention_window_days[customer_retention_window_days['days till second purchase'] > 0]
print(customer_retention_window_days)

most_common_customer_retention_window = customer_retention_window_days['days till second purchase'].value_counts().head(5)

print("Top 5 most common customer retention windows (days):")
print(most_common_customer_retention_window)

p4 = sns.histplot(
    data=customer_retention_window_days, 
    x='days till second purchase', 
    binwidth=7,            
    binrange=(1, 365),     
    kde=True               
)

plt.title('Time between first and second purchase of a customer', y = 0.99)
plt.xlabel('Time till second purchase (days)')
plt.ylabel('Number of clients')
plt.xlim(1, 365) 
plt.show()
