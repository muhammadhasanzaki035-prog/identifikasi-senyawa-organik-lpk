import streamlit as st
import time

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Simulasi & Post Test Gugus Fungsi", layout="centered")

# --- INITIAL STATE MANAGEMENT ---
if "reaksi_berjalan" not in st.session_state:
    st.session_state.reaksi_berjalan = False
if "reset_reaksi" not in st.session_state:
    st.session_state.reset_reaksi = False
if "skor_post_test" not in st.session_state:
    st.session_state.skor_post_test = None

# --- CSS UNTUK VISUALISASI TABUNG REAKSI ---
st.markdown("""
<style>
.test-tube-container {
    display: flex;
    justify-content: center;
    margin: 20px 0;
}

/* MODIFIKASI: Mengubah latar belakang kaca menjadi agak gelap agar warna putih terlihat kontras */
.test-tube {
    width: 80px;
    height: 250px;
    border: 4px solid #cbd5e1;
    border-radius: 0 0 40px 40px;
    position: relative;
    background: rgba(15, 23, 42, 0.15); /* Efek kaca smoky gelap */
    overflow: hidden;
    box-shadow: inset 0 0 12px rgba(0,0,0,0.2);
}

/* Warna Cairan Standar (Bening) */
.liquid-base {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 120px;
    background-color: rgba(200, 230, 255, 0.25);
    transition: all 1s ease;
}

/* Efek Perubahan Warna / Endapan Cermin Perak */
.cermin-perak {
    background: linear-gradient(to right, #94a3b8, #f1f5f9, #cbd5e1) !important;
    border-top: 2px solid #64748b;
}

/* MODIFIKASI: Menambahkan box-shadow gelap di atas endapan putih agar batasnya terlihat sangat jelas */
.endapan-putih-padat {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 45px;
    background: linear-gradient(to top, #ffffff 0%, #f8fafc 70%, #e2e8f0 100%) !important;
    border-top: 2px solid #94a3b8;
    box-shadow: 0 -3px 6px rgba(0, 0, 0, 0.15); /* Mempertegas bentuk endapan */
    opacity: 1.0 !important;
}

.keruh-instan {
    background-color: rgba(255, 255, 255, 0.95) !important;
}

.keruh-lambat {
    background-color: rgba(241, 245, 249, 0.6) !important;
}
</style>
""", unsafe_allow_html=True) # Diubah ke unsafe_allow_html=True karena unsafe_allow_index=True sudah deprecated

# --- NAVIGATION TABS ---
tab1, tab2 = st.tabs(["🧪 Simulasi Reaksi", "📝 Post Test Golongan"])

# ==========================================
# TAB 1: SIMULASI REAKSI (GOLONGAN SENYAWA)
# ==========================================
with tab1:
    st.header("Simulasi Identifikasi Gugus Fungsi")
    st.write("Pilih golongan senyawa reaktan dan reagen uji untuk melihat karakteristik makroskopisnya.")
    
    col1, col2 = st.columns(2)
    with col1:
        golongan_reaktan = st.selectbox(
            "Pilih Golongan Reaktan:",
            ["Alkohol Primer", "Alkohol Sekunder", "Alkohol Tersier", "Aldehida (Alkanal)", "Keton (Alkanon)"],
            disabled=st.session_state.reaksi_berjalan,
            key="sim_reaktan"
        )
    with col2:
        reagen_uji = st.selectbox(
            "Pilih Reagen Uji:",
            ["Reagen Tollens", "Reagen Lucas"],
            disabled=st.session_state.reaksi_berjalan,
            key="sim_reagen"
        )

    # Logika Penentuan Efek Visual & Hasil Teori
    css_cairan = "liquid-base"
    efek_endapan = ""
    teks_hasil = "Tidak ada reaksi perubahan yang teramati. Larutan tetap bening."

    if reagen_uji == "Reagen Tollens":
        if golongan_reaktan == "Aldehida (Alkanal)":
            css_cairan = "liquid-base cermin-perak"
            teks_hasil = "🟢 **Hasil Positif:** Terbentuk lapisan **Cermin Perak** pada dinding tabung. Golongan aldehida berhasil dioksidasi menjadi asam karboksilat."
        else:
            teks_hasil = "❌ **Hasil Negatif:** Tidak terbentuk cermin perak. Golongan senyawa ini tidak dapat dioksidasi oleh reagen Tollens."
            
    elif reagen_uji == "Reagen Lucas":
        if golongan_reaktan == "Alkohol Tersier":
            css_cairan = "liquid-base keruh-instan"
            efek_endapan = '<div class="endapan-putih-padat"></div>'
            teks_hasil = "🟢 **Hasil Positif Cepat:** Larutan **langsung keruh seketika** dan membentuk endapan putih padat di dasar tabung. Karakteristik utama dari Alkohol Tersier."
        elif golongan_reaktan == "Alkohol Sekunder":
            css_cairan = "liquid-base keruh-lambat"
            teks_hasil = "🟡 **Hasil Positif Lambat:** Larutan mulai mengeruh secara perlahan setelah beberapa menit. Karakteristik dari Alkohol Sekunder."
        else:
            teks_hasil = "❌ **Hasil Negatif:** Larutan tetap jernih/bening. Alkohol primer tidak bereaksi dengan reagen Lucas pada suhu kamar."

    st.write("---")
    btn_col1, btn_col2 = st.columns(2)
    
    with btn_col1:
        if st.button("▶️ Mulai Reaksikan", use_container_width=True, disabled=st.session_state.reaksi_berjalan, key="btn_start"):
            st.session_state.reaksi_berjalan = True
            st.session_state.reset_reaksi = False
            st.rerun()
            
    with btn_col2:
        if st.button("⏹️ Stop & Ganti Reaktan", use_container_width=True, disabled=not st.session_state.reaksi_berjalan, key="btn_stop"):
            st.session_state.reaksi_berjalan = False
            st.session_state.reset_reaksi = True
            st.rerun()

    # Tampilan Visual Tabung Reaksi
    if st.session_state.reaksi_berjalan and not st.session_state.reset_reaksi:
        st.info("Reaksi sedang berlangsung... Mengamati perubahan makroskopis.")
        st.markdown(f"""
        <div class="test-tube-container">
            <div class="test-tube">
                <div class="{css_cairan}"></div>
                {efek_endapan}
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.subheader("Analisis Hasil Uji:")
        st.info(teks_hasil)
    else:
        st.markdown("""
        <div class="test-tube-container">
            <div class="test-tube">
                <div class="liquid-base"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.caption("<center>Pilih komponen di atas lalu klik 'Mulai Reaksikan'.</center>", unsafe_allow_html=True)

# ==========================================
# TAB 2: POST TEST (EVALUASI GOLONGAN)
# ==========================================
with tab2:
    st.header("Post Test: Karakteristik Golongan Senyawa")
    st.write("Uji pemahamanmu mengenai prinsip identifikasi golongan senyawa organik di bawah ini.")
    
    with st.form("form_post_test"):
        q1 = st.radio(
            "1. Suatu sampel tidak dikenal direaksikan dengan reagen Tollens dan menghasilkan lapisan cermin perak pada dinding tabung reaksi. Golongan senyawa apakah sampel tersebut?",
            ["Alkohol Primer", "Keton (Alkanon)", "Aldehida (Alkanal)", "Asam Karboksilat"],
            index=None
        )
        
        q2 = st.radio(
            "2. Ketika ditetesi reagen Lucas, sebuah larutan menunjukkan reaksi instan berupa kekeruhan yang pekat dan terbentuk endapan putih padat di dasar tabung tanpa pemanasan. Hal ini menandakan adanya golongan...",
            ["Alkohol Primer", "Alkohol Sekunder", "Alkohol Tersier", "Golongan Ester"],
            index=None
        )
        
        submit_test = st.form_submit_button("Kirim Jawaban")
        
        if submit_test:
            if q1 is None or q2 is None:
                st.warning("Mohon jawab semua pertanyaan sebelum mengirimkan hasil!")
            else:
                skor = 0
                if q1 == "Aldehida (Alkanal)":
                    skor += 50
                if q2 == "Alkohol Tersier":
                    skor += 50
                st.session_state.skor_post_test = skor

        # Menampilkan Nilai Evaluasi
        if st.session_state.skor_post_test is not None:
            st.write("---")
            st.subheader("Hasil Evaluasi Anda:")
            if st.session_state.skor_post_test == 100:
                st.success(f"🎉 Selamat! Nilai Anda: {st.session_state.skor_post_test}/100. Anda memahami prinsip identifikasi golongan dengan sangat baik!")
            else:
                st.warning(f"📝 Nilai Anda: {st.session_state.skor_post_test}/100. Pelajari kembali perbedaan reaktivitas antar golongan fungsi pada menu Simulasi.")
