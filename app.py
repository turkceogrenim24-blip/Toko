import streamlit as st
import pandas as pd
import os

# Konfigurasi Tampilan Halaman
st.set_page_config(page_title="Pencatatan Toko Sederhana", layout="wide")
st.title("📦 Aplikasi Pencatatan & Kasir Toko Sederhana")

# File penyimpanan data lokal
FILE_DATA = "data_toko.csv"

# Inisialisasi Session State & Data
if 'tabel_toko' not in st.session_state:
    if os.path.exists(FILE_DATA):
        st.session_state.tabel_toko = pd.read_csv(FILE_DATA)
    else:
        st.session_state.tabel_toko = pd.DataFrame(columns=["Nama Barang", "Harga (Rp)", "Stok"])

def simpan_data():
    """Fungsi otomatis menyimpan data ke file CSV lokal"""
    st.session_state.tabel_toko.to_csv(FILE_DATA, index=False)

# Navigasi Menu Sidebar
menu = st.sidebar.radio("Pilih Menu:", ["📋 Kelola Stok Barang", "💰 Kasir & Penjualan"])

# ==========================================
# MENU 1: KELOLA STOK BARANG
# ==========================================
if menu == "📋 Kelola Stok Barang":
    st.subheader("Tambah & Kelola Barang Toko")
    
    with st.form("form_tambah_barang"):
        nama_barang = st.text_input("Nama Barang")
        harga_barang = st.number_input("Harga Jual (Rp)", min_value=0, step=500)
        jumlah_stok = st.number_input("Jumlah Stok", min_value=0, step=1)
        submitted = st.form_submit_button("💾 Simpan Barang")
        
        if submitted and nama_barang:
            tabel = st.session_state.tabel_toko
            if not tabel.empty and nama_barang in tabel["Nama Barang"].values:
                # Update stok jika barang sudah ada
                tabel.loc[tabel["Nama Barang"] == nama_barang, "Stok"] += jumlah_stok
                tabel.loc[tabel["Nama Barang"] == nama_barang, "Harga (Rp)"] = harga_barang
                st.success(f"Stok barang '{nama_barang}' berhasil diperbarui!")
            else:
                # Tambah baris baru jika belum ada
                barang_baru = pd.DataFrame([{"Nama Barang": nama_barang, "Harga (Rp)": harga_barang, "Stok": jumlah_stok}])
                st.session_state.tabel_toko = pd.concat([tabel, barang_baru], ignore_index=True)
                st.success(f"Barang baru '{nama_barang}' berhasil ditambahkan!")
            simpan_data()

    st.markdown("### 📊 Daftar Inventaris Toko")
    if not st.session_state.tabel_toko.empty:
        # Tabel interaktif yang bisa langsung diedit
        tabel_terupdate = st.data_editor(st.session_state.tabel_toko, num_rows="dynamic", use_container_width=True)
        st.session_state.tabel_toko = tabel_terupdate
        simpan_data()
        
        st.download_button(
            label="📥 Download Data Toko (.csv)",
            data=st.session_state.tabel_toko.to_csv(index=False).encode('utf-8'),
            file_name="data_toko.csv",
            mime="text/csv"
        )
    else:
        st.info("Belum ada data barang. Silakan tambahkan barang di atas.")

# ==========================================
# MENU 2: KASIR & PENJUALAN
# ==========================================
elif menu == "💰 Kasir & Penjualan":
    st.subheader("Transaksi Penjualan Kasir")
    tabel = st.session_state.tabel_toko
    
    if tabel.empty:
        st.warning("Inventaris masih kosong. Tambahkan barang terlebih dahulu di menu Kelola Stok.")
    else:
        with st.form("form_kasir"):
            pilihan_barang = st.selectbox("Pilih Barang yang Dibeli", tabel["Nama Barang"].tolist())
            jumlah_beli = st.number_input("Jumlah Beli (pcs)", min_value=1, value=1, step=1)
            proses_bayar = st.form_submit_button("💰 Bayar & Kurangi Stok")
            
            if proses_bayar:
                stok_saat_ini = int(tabel.loc[tabel["Nama Barang"] == pilihan_barang, "Stok"].values[0])
                harga_satuan = float(tabel.loc[tabel["Nama Barang"] == pilihan_barang, "Harga (Rp)"].values[0])
                
                if jumlah_beli > stok_saat_ini:
                    st.error(f"❌ Stok tidak cukup! Sisa stok '{pilihan_barang}' tinggal {stok_saat_ini} pcs.")
                else:
                    # Kurangi stok
                    tabel.loc[tabel["Nama Barang"] == pilihan_barang, "Stok"] = stok_saat_ini - jumlah_beli
                    simpan_data()
                    
                    total_bayar = harga_satuan * jumlah_beli
                    st.success(f"✅ Transaksi Berhasil!\n\n**Total yang harus dibayar:** Rp {total_bayar:,.0f}".replace(",", "."))
                    st.rerun()
