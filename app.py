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

# =================# ==========================================
# MENU 1: KELOLA STOK BARANG + TOTAL HARGA STOK
# ==========================================
if menu == "📋 Kelola Stok Barang":
    st.subheader("Tambah & Kelola Barang Toko")
    
    with st.form("form_tambah_barang"):
        nama_barang = st.text_input("Nama Barang")
        harga_barang = st.number_input("Harga Satuan (Rp)", min_value=0, step=500)
        jumlah_stok = st.number_input("Jumlah Stok", min_value=0, step=1)
        submitted = st.form_submit_button("💾 Simpan Barang")
        
        if submitted and nama_barang:
            tabel = st.session_state.tabel_toko
            if not tabel.empty and nama_barang in tabel["Nama Barang"].values:
                tabel.loc[tabel["Nama Barang"] == nama_barang, "Stok"] += jumlah_stok
                tabel.loc[tabel["Nama Barang"] == nama_barang, "Harga (Rp)"] = harga_barang
                st.success(f"Stok barang '{nama_barang}' berhasil diperbarui!")
            else:
                barang_baru = pd.DataFrame([{
                    "Nama Barang": nama_barang,
                    "Harga (Rp)": harga_barang,
                    "Stok": jumlah_stok
                }])
                st.session_state.tabel_toko = pd.concat([tabel, barang_baru], ignore_index=True)
                st.success(f"Barang baru '{nama_barang}' berhasil ditambahkan!")
            simpan_data()

    st.markdown("### 📊 Daftar Inventaris & Total Nilai Stok")
    if not st.session_state.tabel_toko.empty:
        df_tampil = st.session_state.tabel_toko.copy()
        df_tampil["Harga (Rp)"] = pd.to_numeric(df_tampil["Harga (Rp)"], errors="coerce").fillna(0)
        df_tampil["Stok"] = pd.to_numeric(df_tampil["Stok"], errors="coerce").fillna(0)
        
        # Hitung total harga per barang dan keseluruhan stok
        df_tampil["Total Harga Stok (Rp)"] = df_tampil["Harga (Rp)"] * df_tampil["Stok"]
        total_semua_stok = df_tampil["Total Harga Stok (Rp)"].sum()
        total_unit_barang = int(df_tampil["Stok"].sum())

        col1, col2 = st.columns(2)
        col1.metric("💰 Total Nilai Seluruh Stok", f"Rp {total_semua_stok:,.0f}".replace(",", "."))
        col2.metric("📦 Total Unit Barang Tersedia", f"{total_unit_barang} pcs")

        # Tampilkan tabel (kolom Total Harga Stok dihitung otomatis sebelum disimpan)
        tabel_edit = st.data_editor(
            df_tampil[["Nama Barang", "Harga (Rp)", "Stok", "Total Harga Stok (Rp)"]],
            num_rows="dynamic",
            disabled=["Total Harga Stok (Rp)"],
            use_container_width=True
        )
        
        # Simpan kembali hanya kolom utama agar struktur CSV tetap bersih
        tabel_edit["Total Harga Stok (Rp)"] = pd.to_numeric(tabel_edit["Harga (Rp)"], errors="coerce").fillna(0) * pd.to_numeric(tabel_edit["Stok"], errors="coerce").fillna(0)
        st.session_state.tabel_toko = tabel_edit[["Nama Barang", "Harga (Rp)", "Stok"]].copy()
        simpan_data()
        
        st.download_button(
            label="📥 Download Data Toko (.csv)",
            data=tabel_edit.to_csv(index=False).encode('utf-8'),
            file_name="data_toko.csv",
            mime="text/csv"
        )
    else:
        st.info("Belum ada data barang. Silakan tambahkan barang di atas.")
# =========================================
# MENU 2: KASIR & PENJUALAN DENGAN TOTAL HARGA
# ==========================================
elif menu == "💰 Kasir & Penjualan":
    st.subheader("💰 Transaksi Kasir & Hitung Total Harga")
    tabel = st.session_state.tabel_toko
    
    if tabel.empty:
        st.warning("Inventaris masih kosong. Tambahkan barang terlebih dahulu di menu Kelola Stok.")
    else:
        with st.form("form_kasir"):
            # 1. Pilih Barang
            pilihan_barang = st.selectbox("Pilih Barang yang Dibeli", tabel["Nama Barang"].tolist())
            
            # Ambil harga satuan barang yang sedang dipilih dari tabel stok
            harga_satuan = float(tabel.loc[tabel["Nama Barang"] == pilihan_barang, "Harga (Rp)"].values[0])
            st.info(f"🏷️ Harga Satuan: **Rp {harga_satuan:,.0f}** per pcs".replace(",", "."))
            
            # 2. Input Jumlah Beli
            jumlah_beli = st.number_input("Jumlah Beli (pcs)", min_value=1, value=1, step=1)
            
            # 3. HITUNG TOTAL HARGA SECARA OTOMATIS
            total_harga = harga_satuan * jumlah_beli
            
            # Tampilkan pratinjau total harga sebelum tombol bayar ditekan
            st.markdown(f"### 💵 Total yang Harus Dibayar: **Rp {total_harga:,.0f}**".replace(",", "."))
            
            proses_bayar = st.form_submit_button("✅ Konfirmasi Pembayaran & Kurangi Stok")
            
            if proses_bayar:
                stok_saat_ini = int(tabel.loc[tabel["Nama Barang"] == pilihan_barang, "Stok"].values[0])
                
                if jumlah_beli > stok_saat_ini:
                    st.error(f"❌ Stok tidak cukup! Sisa stok '{pilihan_barang}' tinggal {stok_saat_ini} pcs.")
                else:
                    # Kurangi stok di tabel
                    tabel.loc[tabel["Nama Barang"] == pilihan_barang, "Stok"] = stok_saat_ini - jumlah_beli
                    simpan_data()
                    
                    st.success(f"✅ Transaksi Berhasil!\n\nBarang: {pilihan_barang} ({jumlah_beli} pcs)\n**Total Bayar:** Rp {total_harga:,.0f}".replace(",", "."))
                    st.rerun()
