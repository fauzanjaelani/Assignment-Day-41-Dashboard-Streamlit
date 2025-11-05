import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta


# Konfigurasi halaman
st.set_page_config(
   page_title="Dashboard Analisis Penjualan",
   page_icon="📈",
   layout="wide",
   initial_sidebar_state="expanded"
)


# Load data
@st.cache_data 
def load_data():
   df = pd.read_csv("data/dataset_bee_cycle.csv")
   df['order_date'] = pd.to_datetime(df['order_date'])
   return df


df = load_data()


# SIDEBAR FILTER
st.sidebar.title("Filter Dashboard")


# Filter tanggal
with st.sidebar.expander("Filter Tanggal"):
   start_date = st.date_input(
       "Mulai dari:",
       value=df['order_date'].min(),
       min_value=df['order_date'].min(),
       max_value=df['order_date'].max()
   )
   end_date = st.date_input(
       "Sampai dengan:",
       value=df['order_date'].max(),
       min_value=df['order_date'].min(),
       max_value=df['order_date'].max()
   )


# Filter kategori
kategori_list = df['category'].unique().tolist()
selected_kategori = st.sidebar.multiselect(
   "Pilih Kategori:",
   kategori_list,
   default=kategori_list
)


# Filter produk
produk_list = df['product_name'].unique().tolist()
selected_produk = st.sidebar.selectbox(
   "Pilih Produk:", ["All"] + produk_list
)


# Terapkan semua filter
filtered_df = df[
   (df['order_date'] >= pd.to_datetime(start_date)) &
   (df['order_date'] <= pd.to_datetime(end_date)) &
   (df['category'].isin(selected_kategori))
]


if selected_produk != "All":
   filtered_df = filtered_df[filtered_df['product_name'] == selected_produk]




# MAIN DASHBOARD
st.title("📊🚵🏻 Dashboard Penjualan Bee Cycle")
st.write(f"Menampilkan {len(filtered_df)} transaksi dari {start_date} sampai {end_date}")


# KPI
total_sales = filtered_df['totalprice_rupiah'].sum()
total_orders = filtered_df['order_detail_id'].nunique()
total_quantity = filtered_df['quantity'].sum()
average_order_value = total_sales / total_orders if total_orders else 0


col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Sales (Rp)", f"{total_sales:,.0f}")
col2.metric("Total Orders", total_orders)
col3.metric("Total Quantity", total_quantity)
col4.metric("Avg Order Value (Rp)", f"{average_order_value:,.0f}")


# Trend penjualan per bulan
st.subheader("Trend Penjualan per Bulan")
filtered_df['year_month'] = filtered_df['order_date'].dt.to_period('M').astype(str)
sales_trend = filtered_df.groupby('year_month')['totalprice_rupiah'].sum().reset_index()
fig = px.line(sales_trend, x='year_month', y='totalprice_rupiah', title='Trend Penjualan', markers=True)
st.plotly_chart(fig, use_container_width=True)


# Top produk
st.subheader("Top 10 Produk Terlaris")
top_products = filtered_df.groupby('product_name')['quantity'].sum().sort_values(ascending=False).head(10).reset_index()
fig2 = px.bar(top_products, x='product_name', y='quantity', color='product_name', title='Top 10 Produk', text='quantity')
st.plotly_chart(fig2, use_container_width=True)


# Pie chart gender
st.subheader("Distribusi Customer Berdasarkan Gender")
gender_counts = filtered_df['gender'].value_counts().reset_index()
gender_counts.columns = ['gender', 'count']
fig3 = px.pie(gender_counts, names='gender', values='count', title='Distribusi Gender')
st.plotly_chart(fig3, use_container_width=True)


# Tabel
with st.expander("Lihat Data Transaksi"):
   st.dataframe(filtered_df)
