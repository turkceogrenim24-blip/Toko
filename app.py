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
# MENU # ==========================================
# MENU 2: KASIR MULTI-PRODUK (KERANJANG)
# ==========================================
elif menu == "💰 Kasir & Penjualan":
    st.subheader("🛒 Kasir Penjualan (Multi-Produk)")
    tabel = st.session_state.tabel_toko

    if "keranjang" not in st.session_state:
        st.session_state.keranjang = []

    if tabel.empty:
        st.warning("Inventaris masih kosong. Tambahkan barang terlebih dahulu di menu Kelola Stok.")
    else:
        daftar_barang = tabel["Nama Barang"].tolist()

        # 1. Form tambah item ke keranjang
        with st.form("form_tambah_keranjang", clear_on_submit=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                pilihan_barang = st.selectbox("Pilih Produk", daftar_barang)
            with col2:
                jumlah_beli = st.number_input("Jumlah (pcs)", min_value=1, value=1, step=1)

            tambah_item = st.form_submit_button("➕ Masukkan ke Keranjang")

            if tambah_item:
                stok_tersedia = int(tabel.loc[tabel["Nama Barang"] == pilihan_barang, "Stok"].values[0])
                harga_satuan = float(tabel.loc[tabel["Nama Barang"] == pilihan_barang, "Harga (Rp)"].values[0])

                # Hitung total jumlah item ini yang sudah ada di keranjang
                jumlah_di_keranjang = sum(
                    item["Jumlah"] for item in st.session_state.keranjang if item["Nama Barang"] == pilihan_barang
                )

                if jumlah_di_keranjang + jumlah_beli > stok_tersedia:
                    st.error(
                        f"❌ Stok tidak cukup! Tersedia {stok_tersedia} pcs, di keranjang sudah {jumlah_di_keranjang} pcs."
                    )
                else:
                    # Gabungkan jumlah jika produk sudah ada di keranjang
                    sudah_ada = False
                    for item in st.session_state.keranjang:
                        if item["Nama Barang"] == pilihan_barang:
                            item["Jumlah"] += jumlah_beli
                            item["Subtotal (Rp)"] = item["Jumlah"] * item["Harga Satuan (Rp)"]
                            sudah_ada = True
                            break

                    if not sudah_ada:
                        st.session_state.keranjang.append({
                            "Nama Barang": pilihan_barang,
                            "Harga Satuan (Rp)": harga_satuan,
                            "Jumlah": jumlah_beli,
                            "Subtotal (Rp)": harga_satuan * jumlah_beli
                        })
                    st.success(f"'{pilihan_barang}' ({jumlah_beli} pcs) masuk ke keranjang.")
                    st.rerun()

        # 2. Tampilkan isi keranjang & proses pembayaran
        st.markdown("### 🧾 Daftar Belanja Saat Ini")
        if st.session_state.keranjang:
            df_keranjang = pd.DataFrame(st.session_state.keranjang)
            st.dataframe(df_keranjang, use_container_width=True)

            total_transaksi = float(df_keranjang["Subtotal (Rp)"].sum())
            st.markdown(f"### 💵 Total Tagihan: **Rp {total_transaksi:,.0f}**".replace(",", "."))

            col_bayar, col_batal = st.columns(2)
            with col_bayar:
                if st.button("✅ Selesaikan Pembayaran & Potong Stok", type="primary"):
                    # Validasi ulang stok sebelum potong
                    stok_aman = True
                    for item in st.session_state.keranjang:
                        stok_kini = int(tabel.loc[tabel["Nama Barang"] == item["Nama Barang"], "Stok"].values[0])
                        if item["Jumlah"] > stok_kini:
                            st.error(f"❌ Stok '{item['Nama Barang']}' berubah/kurang (sisa {stok_kini} pcs).")
                            stok_aman = False
                            break

                    if stok_aman:
                        for item in st.session_state.keranjang:
                            idx = tabel["Nama Barang"] == item["Nama Barang"]
                            stok_kini = int(tabel.loc[idx, "Stok"].values[0])
                            tabel.loc[idx, "Stok"] = stok_kini - item["Jumlah"]

                        simpan_data()
                        st.session_state.keranjang = []
                        st.success(
                            f"✅ Transaksi selesai! Total dibayar: **Rp {total_transaksi:,.0f}**".replace(",", ".")
                        )
                        st.rerun()

            with col_batal:
                if st.button("🗑️ Kosongkan Keranjang"):
                    st.session_state.keranjang = []
                    st.rerun()
        else:
            st.info("Keranjang masih kosong. Pilih produk di atas lalu klik *Masukkan ke Keranjang*.")
