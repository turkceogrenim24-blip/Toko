import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Catatan Toko", page_icon="🛒")
st.title("🛒 Aplikasi Pencatatan Toko")

FILE_DATA = "data_penjualan.csv"

# Membuat file CSV jika belum ada
if not os.path.exists(FILE_DATA):
    df_awal = pd.DataFrame(columns=["Tanggal", "Nama Barang", "Jumlah", "Harga Satuan", "Total"])
    df_awal.to_csv(FILE_DATA, index=False)

# Form Input Transaksi
with st.form("form_transaksi", clear_on_submit=True):
    st.subheader("Tambah Transaksi Baru")
    nama_barang = st.text_input("Nama Barang")
    jumlah = st.number_input("Jumlah", min_value=1, step=1)
    harga = st.number_input("Harga Satuan (Rp)", min_value=0, step=500)
    simpan = st.form_submit_button("Simpan Transaksi")

    if simpan and nama_barang:
        tanggal = datetime.now().strftime("%Y-%m-%d %H:%M")
        total = jumlah * harga
        data_baru = pd.DataFrame([[tanggal, nama_barang, jumlah, harga, total]], 
                                 columns=["Tanggal", "Nama Barang", "Jumlah", "Harga Satuan", "Total"])
        data_baru.to_csv(FILE_DATA, mode='a', header=False, index=False)
        st.success(f"Berhasil mencatat {nama_barang}!")

# Menampilkan Data & Total Omzet
st.subheader("📊 Riwayat Penjualan")
df = pd.read_csv(FILE_DATA)

if not df.empty:
    total_omzet = df["Total"].sum()
    st.metric(label="Total Pemasukan", value=f"Rp {total_omzet:,.0f}")
    st.dataframe(df, use_container_width=True)
    
    # Tombol download laporan ke Excel/CSV
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Unduh Laporan (CSV)", data=csv, file_name="laporan_toko.csv", mime="text/csv")
else:
    st.info("Belum ada data transaksi.")
