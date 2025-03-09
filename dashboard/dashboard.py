import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Konfigurasi halaman
st.set_page_config(page_title="E-Commerce Dashboard", page_icon="📊", layout="wide")

def create_category_sales_df(df):
    category_sales_df = df.groupby('product_category_name_english').size().sort_values(ascending=False).reset_index()
    category_sales_df.columns = ['product_category', 'total_sales']
    return category_sales_df

def create_payment_type_df(df):
    payment_type_df = df.groupby(['payment_type', 'product_category_name']).agg(
        total_items=('order_item_id_x', 'sum')   
    ).reset_index()
    return payment_type_df

def create_top_categories_df(df, top_n=10):
    top_categories_df = df['product_category_name_english'].value_counts().head(top_n).reset_index()
    top_categories_df.columns = ['product_category', 'order_count']
    return top_categories_df

def create_monthly_orders_df(df):
    df['month'] = df['order_purchase_timestamp'].dt.to_period('M')  
    monthly_orders_df = df.groupby('month').size().reset_index(name='order_count')
    monthly_orders_df.to_csv("monthly_orders.csv", index=False)
    return monthly_orders_df

def create_top_categories_by_state_df(df, top_n=5):
    top_categories = df.groupby('product_category_name_english').size().nlargest(top_n).index.tolist()
    filtered_df = df[df['product_category_name_english'].isin(top_categories)]
    top_categories_by_state_df = filtered_df.groupby(['customer_state', 'product_category_name_english']).agg(
        order_count=("order_id", "count")  
    ).reset_index()
    top_categories_by_state_df.to_csv("top_categories_by_state.csv", index=False)
    return top_categories_by_state_df

main_df = pd.read_csv("dashboard/Main_data.csv")


# Konversi format datetime
if "order_purchase_timestamp" in main_df.columns:
    main_df["order_purchase_timestamp"] = pd.to_datetime(main_df["order_purchase_timestamp"], errors='coerce')


main_df = main_df.dropna(subset=["order_purchase_timestamp"])

# Setel index menjadi order_purchase_timestamp
main_df.set_index("order_purchase_timestamp", inplace=True)

with st.sidebar:

    st.image("icons.jpeg", width=200)
    
    st.title("Informasi:")
    st.markdown("### Nama : Reynaldy Simanungkalit")
    st.title("⚙️ Filter Dashboard")

    # Rentang tanggal untuk filter
    min_date = main_df.index.min().date()
    max_date = main_df.index.max().date()

    st.subheader("Filter Berdasarkan Waktu")
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Filter data berdasarkan rentang tanggal
filtered_main_df = main_df
if start_date and end_date:
    start_date, end_date = pd.to_datetime(start_date), pd.to_datetime(end_date)
    mask_main = (main_df.index >= start_date) & (main_df.index <= end_date)
    filtered_main_df = main_df[mask_main]

    st.sidebar.success(f"Menampilkan data dari {start_date.date()} hingga {end_date.date()}")


#======================== Tampilaln untuk  DASHBOARD ===========================#
st.title("E-Commerce Dashboard")



st.subheader("Kategori Produk Terlaris")
kategori_terlaris = filtered_main_df["product_category_name_english"].value_counts().head(10)
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(
    y=kategori_terlaris.index, 
    x=kategori_terlaris.values,
    palette="colorblind",
    ax=ax
)
ax.set_title("10 Kategori Produk Terlaris", fontsize=15)
ax.set_xlabel("Jumlah Pesanan", fontsize=12)
ax.set_ylabel("Kategori Produk", fontsize=12)
ax.tick_params(axis='y', labelsize=12)
st.pyplot(fig)


st.subheader("Distribusi Metode Pembayaran")
metod_pembayaran = filtered_main_df.groupby('payment_type')["order_id"].count().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(
    x=metod_pembayaran.index, 
    y=metod_pembayaran.values,
    palette="viridis",
    ax=ax
)
ax.set_title("Metode Pembayaran yang Paling Banyak Digunakan", fontsize=15)
ax.set_xlabel("Metode Pembayaran")
ax.set_ylabel(None)
ax.tick_params(axis='x', labelsize=12, rotation=45)
st.pyplot(fig)


st.subheader("Tren Penjualan ")
monthly_sales = (
    filtered_main_df.resample('M')
    .size()
    .reset_index(name='total_orders')
)

fig, ax = plt.subplots(figsize=(14, 6))
sns.lineplot(
    x='order_purchase_timestamp', 
    y='total_orders', 
    data=monthly_sales, 
    marker='o', 
    color='b'
)
ax.set_title("Tren Penjualan dari Waktu ke Waktu", loc="center", fontsize=15)
ax.set_xlabel("Waktu (Bulan-Tahun)")
ax.set_ylabel("Jumlah Pesanan")
st.pyplot(fig)


st.subheader("5 Kategori Produk Terlaris Berdasarkan Lokasi Pelanggan")
top5_categories = filtered_main_df.groupby('product_category_name_english').size().nlargest(5).index.tolist()
filter_df = filtered_main_df[filtered_main_df['product_category_name_english'].isin(top5_categories)]

kategori_terlaris_lokasi = filter_df.groupby(['customer_state', 'product_category_name_english']).agg(order_count=("order_id", "count")).reset_index()

fig, ax = plt.subplots(figsize=(14, 8))
sns.barplot(
    x='order_count', 
    y='customer_state', 
    hue='product_category_name_english', 
    data=kategori_terlaris_lokasi, 
    palette="viridis",
    ax=ax
)
ax.set_title("5 Kategori Produk Terlaris Berdasarkan Lokasi Pelanggan", fontsize=16)
ax.set_xlabel("Jumlah Pesanan", fontsize=12)
ax.set_ylabel("Negara Bagian", fontsize=12)
ax.tick_params(axis='y', labelsize=12)
st.pyplot(fig)