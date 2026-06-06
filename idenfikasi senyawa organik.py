import streamlit as st
import time

# ==============================================================================
# 1. KONFIGURASI HALAMAN
# ==============================================================================
st.set_page_config(
    page_title="OrganicChem | Platform Edu-Lab",
    page_icon="🧪",
    layout="wide"
)

# ==============================================================================
# 2. CUSTOM CSS INTERAKTIF
# ==============================================================================
st.markdown("""
    <style>
    /* Desain Kotak Hasil Analisis yang Unik & Modern */
    .kotak-analisis {
        border-left: 6px solid #2ecc71;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        background-color: #f5fbf7;
        box-shadow: 0 4px 6px rgba(0,0,0,0.04);
    }
    .label-analisis {
        font-weight: bold;
        color: #27ae60;
        font-size: 1.15em;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    /* Desain Banner Gradasi untuk Halaman Utama - WARNA BIRU */
    .banner-utama {
        background: linear-gradient(135deg, #1e3c72, #2a5298);
        padding: 35px;
        border-radius: 12px;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 4px 15px rgba(42, 82, 152, 0.2);
    }
    /* CSS UNTUK TABUNG REAKSI 2D */
    .tube-wrap { display: flex; justify-content: center; height: 350px; padding-top: 20px;}
    .tube-glass { 
        width: 80px; 
        height: 300px; 
        border: 4px solid #cbd5e1; 
        border-top: none; 
        border-radius: 0 0 40px 40px; 
        position: relative; 
        overflow: hidden;
        background: transparent;
    }
    .tube-liquid { 
        position: absolute; 
        bottom: 0; left: 0; right: 0; 
        transition: height 1.2s ease, background 1.2s ease; 
    }
    .precipitate-layer { position: absolute; bottom: 0; left: 0; right: 0; height: 40px; background-color: rgba(0,0,0,0.4); }
    .cloudy-layer { position: absolute; top: 0; bottom: 0; left: 0; right: 0; background-color: rgba(255,255,255,0.5); }
    .bubble-fx { position: absolute; background: rgba(255,255,255,0.4); border-radius: 50%; width: 8px; height: 8px; animation: floatUp 1.8s infinite ease-in; }
    @keyframes floatUp { 0% { bottom: 0px; opacity: 1; } 100% { bottom: 250px; opacity: 0; } }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. FUNGSI HELPER & SIMULASI TABUNG
# ==============================================================================
def force_rerun():
    if hasattr(st, 'rerun'):
        st.rerun()
    elif hasattr(st, 'experimental_rerun'):
        st.experimental_rerun()
    else:
        st.warning("⚠️ Versi Streamlit usang. Silakan refresh halaman secara manual (F5).")

def render_tube(tinggi, warna, efek):
    e_html = ""
    if efek == "endapan":
        e_html = "<div class='precipitate-layer'></div>"
    elif efek == "keruh":
        e_html = "<div class='cloudy-layer'></div>"
    elif efek == "gelembung":
        e_html = "<div class='bubble-fx' style='left:20px;'></div><div class='bubble-fx' style='left:50px; animation-delay:0.5s;'></div>"
        
    return f"<div class='tube-wrap'><div class='tube-glass'><div class='tube-liquid' style='height:{tinggi}; background:{warna};'>{e_html}</div></div></div>"

reagen_colors = {
    "Ceric Nitrat": "#facc15", 
    "Pereaksi Jones": "#f97316", 
    "Pereaksi Lucas": "#f8fafc", 
    "Pereaksi Lucas (Panas)": "#f8fafc", 
    "Na-Bisulfit": "#f8fafc", 
    "Pereaksi Fehling": "#3b82f6", 
    "Pereaksi Schiff": "#f8fafc",
    "Uji Iodoform": "#f8fafc",
    "Hidroksilamin (Uji Ester)": "#f8fafc",
    "Uji Barit (NaHCO3)": "#f8fafc"
}

flowchart_paths = {
    "1-Butanol": ["Ceric Nitrat", "Pereaksi Jones", "Pereaksi Lucas (Panas)"],
    "2-Butanol": ["Ceric Nitrat", "Pereaksi Jones", "Pereaksi Lucas (Panas)", "Uji Iodoform"],
    "t-Butil Alkohol": ["Ceric Nitrat", "Pereaksi Jones", "Pereaksi Lucas"],
    "Formaldehida": ["Ceric Nitrat", "Na-Bisulfit", "Pereaksi Fehling", "Pereaksi Schiff"],
    "Aseton": ["Ceric Nitrat", "Na-Bisulfit", "Pereaksi Fehling", "Uji Iodoform"],
    "Etil Asetat": ["Ceric Nitrat", "Na-Bisulfit", "Hidroksilamin (Uji Ester)"],
    "Asam Asetat": ["Ceric Nitrat", "Na-Bisulfit", "Hidroksilamin (Uji Ester)", "Uji Barit (NaHCO3)"],
    "Heksana": ["Ceric Nitrat", "Na-Bisulfit", "Hidroksilamin (Uji Ester)", "Uji Barit (NaHCO3)"]
}

database_reaksi = {
    "1-Butanol": {
        "Ceric Nitrat": {
            "hasil": "(+) Merah Ceri", 
            "reaksi": r"\text{R-OH} + [\text{Ce(NO}_3)_6]^{2-} \rightarrow [\text{Ce(OR)(NO}_3)_5]^{2-} + \text{HNO}_3", 
            "alasan": "Gugus -OH bebas dari 1-butanol bereaksi menggantikan ligan nitrat pada ion Cerium(IV) membentuk senyawa kompleks koordinasi yang berwarna merah ceri.", 
            "warna_akhir": "#ef4444", "efek": "tidak_ada"
        },
        "Pereaksi Jones": {
            "hasil": "(+) Hijau", 
            "reaksi": r"3\text{R-CH}_2\text{-OH} + 2\text{CrO}_3 + 3\text{H}_2\text{SO}_4 \rightarrow 3\text{R-COOH} + \text{Cr}_2(\text{SO}_4)_3 + 6\text{H}_2\text{O}", 
            "alasan": "1-butanol adalah alkohol primer yang memiliki atom hidrogen alfa. Gugus -OH dioksidasi kuat menjadi asam karboksilat, sedangkan Kromium(VI) jingga tereduksi menjadi Kromium(III) hijau.", 
            "warna_akhir": "#10b981", "efek": "tidak_ada"
        },
        "Pereaksi Lucas (Panas)": {
            "hasil": "(-) Bening", 
            "reaksi": r"\text{R-CH}_2\text{-OH} + \text{HCl} \xrightarrow{\text{ZnCl}_2, \Delta} \text{Tidak terjadi reaksi / endapan}", 
            "alasan": "Karbokation primer sangat tidak stabil. Reaksi substitusi nukleofilik (SN1) tidak berjalan membentuk alkil klorida yang tak larut, bahkan setelah dibantu pemanasan.", 
            "warna_akhir": "#f8fafc", "efek": "tidak_ada"
        }
    },
    "2-Butanol": {
        "Ceric Nitrat": {
            "hasil": "(+) Merah Ceri", 
            "reaksi": r"\text{R-OH} + [\text{Ce(NO}_3)_6]^{2-} \rightarrow [\text{Ce(OR)(NO}_3)_5]^{2-} + \text{HNO}_3", 
            "alasan": "Ikatan koordinasi terbentuk antara atom oksigen pada gugus hidroksil sekunder dengan logam Cerium pusat, menghasilkan warna merah.", 
            "warna_akhir": "#ef4444", "efek": "tidak_ada"
        },
        "Pereaksi Jones": {
            "hasil": "(+) Hijau", 
            "reaksi": r"3\text{R}_2\text{CH-OH} + 2\text{CrO}_3 + 3\text{H}_2\text{SO}_4 \rightarrow 3\text{R}_2\text{C}=\text{O} + \text{Cr}_2(\text{SO}_4)_3 + 6\text{H}_2\text{O}", 
            "alasan": "2-butanol dioksidasi oleh reagen Jones menjadi keton. Cr(VI) (jingga) tereduksi ke Cr(III) (hijau).", 
            "warna_akhir": "#10b981", "efek": "tidak_ada"
        },
        "Pereaksi Lucas (Panas)": {
            "hasil": "(+) Emulsi Putih", 
            "reaksi": r"\text{R}_2\text{CH-OH} + \text{HCl} \xrightarrow{\text{ZnCl}_2} \text{R}_2\text{CH-Cl}\downarrow + \text{H}_2\text{O}", 
            "alasan": "Karbokation sekunder memiliki stabilitas menengah. Reaksi butuh pemanasan untuk mempercepat substitusi menjadi alkil klorida yang mengeruhkan larutan.", 
            "warna_akhir": "#e2e8f0", "efek": "keruh"
        },
        "Uji Iodoform": {
            "hasil": "(+) Endapan Kuning", 
            "reaksi": r"\text{R-CH(OH)-CH}_3 + 4\text{I}_2 + 6\text{NaOH} \rightarrow \text{CHI}_3\downarrow + \text{R-COONa} + 5\text{NaI} + 5\text{H}_2\text{O}", 
            "alasan": "2-Butanol adalah metil karbinol yang dioksidasi iodin menjadi metil keton. Gugus metilnya tersubstitusi menjadi kristal iodoform kuning.", 
            "warna_akhir": "#fef08a", "efek": "endapan"
        }
    },
    "t-Butil Alkohol": {
        "Ceric Nitrat": {
            "hasil": "(+) Merah Ceri", 
            "reaksi": r"\text{R-OH} + [\text{Ce(NO}_3)_6]^{2-} \rightarrow [\text{Ce(OR)(NO}_3)_5]^{2-} + \text{HNO}_3", 
            "alasan": "Terdapat gugus -OH bebas yang dapat berikatan koordinasi membentuk kompleks merah.", 
            "warna_akhir": "#ef4444", "efek": "tidak_ada"
        },
        "Pereaksi Jones": {
            "hasil": "(-) Tetap Jingga", 
            "reaksi": r"\text{R}_3\text{C-OH} + \text{CrO}_3 + \text{H}^+ \rightarrow \text{Tidak bereaksi}", 
            "alasan": "Alkohol tersier tidak memiliki atom hidrogen alfa, sehingga sangat kebal dan tidak bisa dioksidasi.", 
            "warna_akhir": "#f97316", "efek": "tidak_ada"
        },
        "Pereaksi Lucas": {
            "hasil": "(+) Emulsi Putih (Seketika)", 
            "reaksi": r"\text{R}_3\text{C-OH} + \text{HCl} \xrightarrow{\text{ZnCl}_2} \text{R}_3\text{C-Cl}\downarrow + \text{H}_2\text{O}", 
            "alasan": "Membentuk karbokation tersier yang sangat stabil. Reaksi (SN1) terjadi seketika menghasilkan endapan alkil klorida.", 
            "warna_akhir": "#94a3b8", "efek": "keruh"
        }
    },
    "Formaldehida": {
        "Ceric Nitrat": {
            "hasil": "(-) Kuning", 
            "reaksi": r"\text{HCHO} + [\text{Ce(NO}_3)_6]^{2-} \rightarrow \text{Tidak bereaksi}", 
            "alasan": "Formaldehida merupakan aldehid dan tidak memiliki gugus hidroksil bebas untuk bereaksi dengan Cerium.", 
            "warna_akhir": "#facc15", "efek": "tidak_ada"
        },
        "Na-Bisulfit": {
            "hasil": "(+) Endapan Putih", 
            "reaksi": r"\text{H-CHO} + \text{NaHSO}_3 \rightarrow \text{H}_2\text{C(OH)SO}_3\text{Na}\downarrow", 
            "alasan": "Nukleofil bisulfit menyerang karbonil yang miskin elektron, membentuk garam padatan kristal.", 
            "warna_akhir": "#ffffff", "efek": "endapan"
        },
        "Pereaksi Fehling": {
            "hasil": "(+) Merah Bata", 
            "reaksi": r"\text{H-CHO} + 2\text{Cu}^{2+} + 5\text{OH}^- \rightarrow \text{H-COO}^- + \text{Cu}_2\text{O}\downarrow + 3\text{H}_2\text{O}", 
            "alasan": "Aldehid adalah reduktor kuat. Ia mereduksi Tembaga(II) sulfat biru menjadi endapan Tembaga(I) oksida (merah bata).", 
            "warna_akhir": "#b91c1c", "efek": "endapan"
        },
        "Pereaksi Schiff": {
            "hasil": "(+) Ungu / Magenta", 
            "reaksi": r"\text{Aldehida} + \text{Reagen Schiff} \rightarrow \text{Kompleks warna magenta}", 
            "alasan": "Reaksi adisi spesifik yang memulihkan pewarna p-rosanilin hidroklorida.", 
            "warna_akhir": "#d946ef", "efek": "tidak_ada"
        }
    },
    "Aseton": {
        "Ceric Nitrat": {
            "hasil": "(-) Kuning", 
            "reaksi": r"\text{CH}_3\text{COCH}_3 + [\text{Ce(NO}_3)_6]^{2-} \rightarrow \text{Tidak bereaksi}", 
            "alasan": "Keton tidak memiliki gugus hidroksil alkoholik.", 
            "warna_akhir": "#facc15", "efek": "tidak_ada"
        },
        "Na-Bisulfit": {
            "hasil": "(+) Endapan Putih", 
            "reaksi": r"\text{CH}_3\text{-CO-CH}_3 + \text{NaHSO}_3 \rightarrow (\text{CH}_3)_2\text{C(OH)SO}_3\text{Na}\downarrow", 
            "alasan": "Aseton masih memiliki halangan sterik rendah, sehingga bisa mengalami reaksi adisi membentuk garam bisulfit.", 
            "warna_akhir": "#ffffff", "efek": "endapan"
        },
        "Pereaksi Fehling": {
            "hasil": "(-) Tetap Biru", 
            "reaksi": r"\text{CH}_3\text{-CO-CH}_3 + \text{Cu}^{2+} \rightarrow \text{Tidak direduksi}", 
            "alasan": "Keton tidak memiliki atom hidrogen pada karbon pengikat oksigen sehingga tidak memiliki sifat reduktor.", 
            "warna_akhir": "#3b82f6", "efek": "tidak_ada"
        },
        "Uji Iodoform": {
            "hasil": "(+) Endapan Kuning", 
            "reaksi": r"\text{CH}_3\text{-CO-CH}_3 + 3\text{I}_2 + 4\text{NaOH} \rightarrow \text{CHI}_3\downarrow + \text{CH}_3\text{COONa} + 3\text{NaI} + 3\text{H}_2\text{O}", 
            "alasan": "Atom hidrogen alfa pada metil keton sangat asam, tersubstitusi oleh Iodin lalu putus membentuk Iodoform kuning.", 
            "warna_akhir": "#fef08a", "efek": "endapan"
        }
    },
    "Etil Asetat": {
        "Ceric Nitrat": {
            "hasil": "(-) Kuning", 
            "reaksi": r"\text{Ester} + \text{Ceric Nitrat} \rightarrow \text{Tidak bereaksi}", 
            "alasan": "Gugus ester tidak memiliki komponen penyusun yang reaktif terhadap uji alkohol ceric.", 
            "warna_akhir": "#facc15", "efek": "tidak_ada"
        },
        "Na-Bisulfit": {
            "hasil": "(-) Bening", 
            "reaksi": r"\text{Ester} + \text{NaHSO}_3 \rightarrow \text{Tidak bereaksi}", 
            "alasan": "Resonansi pasangan elektron bebas dari gugus etoksi menstabilkan karbon karbonil, menjadikannya tidak reaktif terhadap nukleofil lemah.", 
            "warna_akhir": "#f8fafc", "efek": "tidak_ada"
        },
        "Hidroksilamin (Uji Ester)": {
            "hasil": "(+) Merah Violet", 
            "reaksi": r"1.\ \text{R-COOR'} + \text{NH}_2\text{OH} \rightarrow \text{R-CONHOH} + \text{R'-OH} \quad 2.\ 3\text{R-CONHOH} + \text{FeCl}_3 \rightarrow \text{Fe(R-CONHO)}_3 + 3\text{HCl}", 
            "alasan": "Ester diubah oleh hidroksilamin menjadi asam hidroksamat yang dapat mengikat ion Fe3+ menghasilkan kompleks berwarna violet.", 
            "warna_akhir": "#c026d3", "efek": "tidak_ada"
        }
    },
    "Asam Asetat": {
        "Ceric Nitrat": {
            "hasil": "(-) Kuning", 
            "reaksi": r"\text{CH}_3\text{COOH} + \text{Ceric Nitrat} \rightarrow \text{Tidak bereaksi}", 
            "alasan": "Oksigen karboksil ditarik oleh resonansi ikatan rangkap karbonil, menjadikannya kurang nukleofilik untuk berikatan dengan Cerium.", 
            "warna_akhir": "#facc15", "efek": "tidak_ada"
        },
        "Na-Bisulfit": {
            "hasil": "(-) Bening", 
            "reaksi": r"\text{CH}_3\text{COOH} + \text{NaHSO}_3 \rightarrow \text{Tidak bereaksi}", 
            "alasan": "Bukan senyawa golongan aldehid atau keton.", 
            "warna_akhir": "#f8fafc", "efek": "tidak_ada"
        },
        "Hidroksilamin (Uji Ester)": {
            "hasil": "(-) Bening", 
            "reaksi": r"\text{CH}_3\text{COOH} + \text{NH}_2\text{OH} + \text{FeCl}_3 \rightarrow \text{Tidak bereaksi}", 
            "alasan": "Bukan ester. Asam karboksilat tidak memicu pembentukan asam hidroksamat reaktif di kondisi ini.", 
            "warna_akhir": "#f8fafc", "efek": "tidak_ada"
        },
        "Uji Barit (NaHCO3)": {
            "hasil": "(+) Gelembung & Keruh", 
            "reaksi": r"1.\ \text{CH}_3\text{COOH} + \text{NaHCO}_3 \rightarrow \text{CH}_3\text{COONa} + \text{H}_2\text{O} + \text{CO}_2\uparrow \quad 2.\ \text{CO}_2 + \text{Ba(OH)}_2 \rightarrow \text{BaCO}_3\downarrow + \text{H}_2\text{O}", 
            "alasan": "Asam karboksilat mendonasikan proton untuk mengurai bikarbonat. Gas CO2 yang terlepas bereaksi dengan air barit membentuk BaCO3 yang keruh.", 
            "warna_akhir": "#f8fafc", "efek": "gelembung"
        }
    },
    "Heksana": {
        "Ceric Nitrat": {
            "hasil": "(-) Kuning", 
            "reaksi": r"\text{Heksana} + \text{Ceric Nitrat} \rightarrow \text{Tidak bereaksi}", 
            "alasan": "Tidak ada gugus fungsi -OH alkoholik.", 
            "warna_akhir": "#facc15", "efek": "tidak_ada"
        },
        "Na-Bisulfit": {
            "hasil": "(-) Bening", 
            "reaksi": r"\text{Heksana} + \text{NaHSO}_3 \rightarrow \text{Tidak bereaksi}", 
            "alasan": "Tidak memiliki gugus aktif karbonil.", 
            "warna_akhir": "#f8fafc", "efek": "tidak_ada"
        },
        "Hidroksilamin (Uji Ester)": {
            "hasil": "(-) Bening", 
            "reaksi": r"\text{Heksana} + \text{NH}_2\text{OH} \rightarrow \text{Tidak bereaksi}", 
            "alasan": "Bukan merupakan senyawa turunan ester.", 
            "warna_akhir": "#f8fafc", "efek": "tidak_ada"
        },
        "Uji Barit (NaHCO3)": {
            "hasil": "(-) Bening", 
            "reaksi": r"\text{Heksana} + \text{NaHCO}_3 \rightarrow \text{Tidak bereaksi}", 
            "alasan": "Senyawa hidrokarbon alifatik (jenuh) bersifat non-polar dan inert. Karena secara berturut-turut gagal bereaksi di seluruh uji fungsional, ini membuktikan senyawanya adalah alkana.", 
            "warna_akhir": "#f8fafc", "efek": "tidak_ada"
        }
    }
}

# Inisialisasi State Management
if 'test_started' not in st.session_state:
    st.session_state.test_started = False
if 'senyawa_uji' not in st.session_state:
    st.session_state.senyawa_uji = ""
if 'current_step' not in st.session_state:
    st.session_state.current_step = 0
if 'log_history' not in st.session_state:
    st.session_state.log_history = []
if 'trigger_animation' not in st.session_state:
    st.session_state.trigger_animation = False

# ==============================================================================
# 4. SIDEBAR NAVIGASI
# ==============================================================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3022/3022607.png", width=75)
    st.title("OrganicChem")
    st.write("🔬 *Identifikasi Senyawa Organik*")
    st.markdown("---")
    
    pilihan_halaman = st.sidebar.radio(
        "Navigasi Menu:",
        [
            "🏠 HALAMAN UTAMA", 
            "📘 BAB I. HIDROKARBON", 
            "📙 BAB II. ALKOHOL, ETER, DAN FENOL", 
            "📗 BAB III. ALDEHID DAN KETON", 
            "📕 BAB IV. ASAM KARBOKSILAT DAN DERIVATNYA", 
            "🔬 POST TEST"
        ]
    )
    st.markdown("---")
    st.caption("E-Learning Kimia Organik | © 2026")

# ==============================================================================
# 5. LOGIKA KONTEN TIAP HALAMAN
# ==============================================================================

# --- HALAMAN UTAMA ---
if pilihan_halaman == "🏠 HALAMAN UTAMA":
    st.markdown("""
        <div class="banner-utama">
            <h1 style='color: white; margin-bottom: 5px; font-weight: 700;'>Eksplorasi Dunia Kimia Organik Tanpa Batas! 👋</h1>
            <p style='font-size: 1.2em; opacity: 0.95;'>Solusi cerdas belajar mandiri dan simulasi identifikasi gugus fungsi dalam satu platform.</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.subheader("💡 Tentang OrganicChem")
    st.write(
        "Kami hadir untuk menjembatani teori dan praktik. Platform ini dirancang khusus untuk "
        "membantu Anda memahami materi teoretis sekaligus memvisualisasikan reaksi uji kualitatif "
        "senyawa organik secara interaktif—kapan saja dan di mana saja, layaknya memiliki laboratorium pribadi."
    )
    
# --- [BAGIAN DIUBAH] BAB I: BREAKDOWN MENJADI SUB-BAB KECIL ---
elif pilihan_halaman == "📘 BAB I. HIDROKARBON":
    st.title("📘 BAB I. HIDROKARBON")
    st.write("---")
    
    st.markdown("""
    ### **1.1 Pengantar Hidrokarbon**
    Hidrokarbon adalah senyawa organik paling sederhana yang seluruh strukturnya hanya tersusun atas unsur **karbon (C)** dan **hidrogen (H)**. Berdasarkan bentuk rantai dan jenis ikatannya, senyawa ini dikelompokkan ke dalam variasi struktur alifatik jenuh, alifatik tidak jenuh, serta cincin konjugasi aromatik.

    ---
    ### **1.2 Klasifikasi Utama Rantai Karbon**
    * **Alfatik Jenuh (Alkana):** Memiliki ikatan tunggal antar atom karbon ($C-C$).
    * **Alifatik Tidak Jenuh (Alkena & Alkuna):** Mengandung ikatan rangkap dua ($C=C$) atau tiga ($C\equiv C$) yang kaya elektron pi.
    * **Aromatik (Benzena):** Memiliki rantai siklik dengan sistem elektron yang terdelokalisasi secara penuh.

    ---
    ### **1.3 Karakteristik Sifat Fisika**
    #### **1.3.1 Wujud Zat Berdasarkan Panjang Rantai**
    * **Suhu Rendah ($C_1 - C_4$):** Berwujud **gas** (contoh: metana, etana, etena, etuna).
    * **Suhu Sedang ($C_5 - C_{17}$):** Berwujud **cair** (contoh: pentana, heksana, benzena).
    * **Suhu Tinggi ($\ge C_{18}$):** Berwujud **padat** (contoh: parafin padat).

    #### **1.3.2 Sifat Kelarutan & Massa Jenis**
    * **Kelarutan:** Bersifat **nonpolar**, sehingga tidak larut dalam air (pelarut polar). Hidrokarbon larut dengan baik dalam sesama pelarut organik seperti kloroform ($CHCl_3$), karbon tetraklorida ($CCl_4$), atau eter.
    * **Densitas (Massa Jenis):** Memiliki nilai densitas yang lebih kecil daripada air ($< 1.0 \text{ g/mL}$). Jika dicampur dengan air, lapisan hidrokarbon akan selalu berada di bagian atas.

    #### **1.3.3 Pola Titik Didih dan Titik Leleh**
    * Nilai temperatur meningkat seiring bertambahnya massa molekul (panjang rantai karbon).
    * Untuk isomer dengan jumlah atom karbon yang sama, **senyawa rantai lurus memiliki titik didih lebih tinggi** dibandingkan rantai bercabang karena luas permukaan kontak antarmolekul yang jauh lebih besar.

    ---
    ### **1.4 Sifat Kimia & Uji Identifikasi Spesifik**
    
    #### **1.4.1 Golongan Alkana (Hidrokarbon Jenuh)**
    Alkana sering disebut sebagai *parafin* (afinitas kecil) karena sifatnya yang inert atau sangat tidak reaktif terhadap sebagian besar pereaksi seperti asam kuat, basa kuat, dan oksidator pada suhu kamar.
    
    * **Uji Iodo (Substitusi Halogen):** Alkana hanya dapat bereaksi melalui substitusi radikal bebas dengan bantuan paparan sinar ultraviolet (UV) atau pemanasan tinggi. Reaksi berjalan lambat dan ditandai dengan memudarnya warna ungu dari iodium.
    """)
    st.latex(r"\text{CH}_4 + \text{I}_2 \xrightarrow{\text{Sinar UV} / \Delta} \text{CH}_3\text{I} + \text{HI}")
    
    st.markdown("""
    #### **1.4.2 Golongan Alkena dan Alkuna (Hidrokarbon Tidak Jenuh)**
    Sangat reaktif karena memiliki ikatan rangkap yang kaya akan elektron, sehingga mudah mengalami pemutusan ikatan rangkap (adisi).
    
    * **Uji Adisi Iodium:** Mengadisi halogen pada ikatan rangkap secara spontan tanpa memerlukan bantuan sinar UV. Ditandai dengan warna ungu iodium yang memudar/hilang seketika.
    """)
    st.latex(r"\text{R-CH}=\text{CH-R} + \text{I}_2 \rightarrow \text{R-CH(I)-CH(I)-R}")
    
    st.markdown("""
    * **Uji Baeyer (Oksidasi Permanganat):** Alkena atau alkuna dioksidasi oleh larutan kalium permanganat encer dalam suasana netral/basa menghasilkan senyawa glikol. Uji positif ditandai dengan hilangnya warna ungu $KMnO_4$ dan terbentuknya endapan cokelat $MnO_2$.
    """)
    st.latex(r"3\text{CH}_2=\text{CH}_2 + 2\text{KMnO}_4 + 4\text{H}_2\text{O} \rightarrow 3\text{HO-CH}_2\text{-CH}_2\text{-OH} + 2\text{MnO}_2\downarrow + 2\text{KOH}")
    
    st.markdown("""
    #### **1.4.3 Golongan Benzena (Hidrokarbon Aromatik)**
    Memiliki struktur siklik dengan elektron pi yang terdelokalisasi (resonansi) memenuhi aturan Hückel ($4n + 2$), membuat intinya sangat stabil dan sukar diadisi.
    
    * **Uji Bakar Kualitatif:** Ketika dibakar dengan api langsung pada cawan porselin, benzena menghasilkan nyala api berminyak disertai jelaga hitam yang sangat tebal akibat tingginya persentase kadar karbon.
    """)
    st.latex(r"\text{Benzena} + \text{O}_2 \rightarrow \text{C}_{(s)} \text{ + CO} + \text{H}_2\text{O}")
    
    st.markdown("""
    * **Reaksi Nitrasi (Substitusi Elektrofilik):** Benzena cenderung mengalami substitusi atom H pada cincin menggunakan campuran asam nitrat pekat dan katalis asam sulfat pekat.
    """)
    st.latex(r"\text{C}_6\text{H}_6 + \text{HNO}_3 \xrightarrow{\text{H}_2\text{SO}_4\text{ pekat}} \text{C}_6\text{H}_5\text{NO}_2 + \text{H}_2\text{O}")

# --- [BAGIAN DIUBAH] BAB II: BREAKDOWN MENJADI SUB-BAB KECIL ---
elif pilihan_halaman == "📙 BAB II. ALKOHOL, ETER, DAN FENOL":
    st.title("📙 BAB II. ALKOHOL, ETER, DAN FENOL")
    st.write("---")
    
    st.markdown("""
    ### **2.1 Struktur Dasar & Klasifikasi**
    * **Alkohol ($R - OH$):** Senyawa turunan alkana di mana satu atau lebih atom H digantikan oleh gugus hidroksil ($-OH$). Dibagi menjadi alkohol **primer ($1^\circ$)**, **sekunder ($2^\circ$)**, dan **tersier ($3^\circ$)** berdasarkan jenis karbon pengikatnya.
    * **Eter ($R^1 - O - R^2$):** Isomer fungsional dari alkohol yang memiliki gugus oksi di antara dua rantai karbon.
    * **Fenol ($C_6H_5OH$):** Senyawa hidrokarbon aromatik yang mengikat gugus fungsi $-OH$ langsung pada cincin inti benzena.

    ---
    ### **2.2 Sifat Fisika Komparatif**
    #### **2.2.1 Sifat Kelarutan dalam Air**
    * **Alkohol:** Suku rendah mudah larut dalam air karena sanggup membentuk ikatan hidrogen yang kuat dengan molekul air. Kelarutan berkurang seiring bertambah panjangnya rantai karbon hydrophobic.
    * **Eter:** Kelarutannya mirip dengan alkohol karena atom oksigen pada eter masih bisa menerima donor ikatan hidrogen dari molekul air.
    * **Fenol:** Berupa padatan/hablur pada suhu kamar, sedikit larut dalam air, dan larutannya bersifat asam lemah karena ion fenoksida yang terbentuk distabilkan oleh resonansi cincin.

    #### **2.2.2 Analisis Titik Didih**
    * Titik didih eter **jauh lebih rendah** dibandingkan alkohol isomernya. Hal ini disebabkan karena eter tidak memiliki kemampuan untuk membentuk jembatan ikatan hidrogen antar-sesama molekulnya sendiri.

    ---
    ### **2.3 Kimia Identifikasi Alkohol dan Eter**
    
    #### **2.3.1 Pereaksi Lucas (Diferensiasi Kelas Alkohol)**
    Menggunakan campuran reagen $HCl$ pekat dan katalis $ZnCl_2$ untuk membedakan jenis alkohol berdasarkan kecepatan pembentukan senyawa alkil klorida yang tak larut.
    * **Alkohol $3^\circ$:** Bereaksi seketika (larutan langsung keruh/terbentuk dua lapisan terpisah).
    * **Alkohol $2^\circ$:** Bereaksi lambat dalam waktu 5–10 menit dengan bantuan pemanasan.
    * **Alkohol $1^\circ$:** Tidak bereaksi pada suhu kamar.
    """)
    st.latex(r"\text{R}_3\text{C-OH} + \text{HCl} \xrightarrow{\text{ZnCl}_2} \text{R}_3\text{C-Cl}\downarrow + \text{H}_2\text{O}")
    
    st.markdown("""
    #### **2.3.2 Pereaksi Jones (Uji Tingkat Oksidasi)**
    Menggunakan kromium trioksida ($CrO_3$) dalam media asam sulfat pekat. Uji positif ditandai dengan perubahan warna reagen dari jingga ($Cr^{6+}$) menjadi hijau ($Cr^{3+}$).
    * Alkohol $1^\circ$ dioksidasi menjadi Aldehida, lalu berlanjut menjadi Asam Karboksilat.
    * Alkohol $2^\circ$ dioksidasi menjadi Keton.
    * Alkohol $3^\circ$ kebal/tidak dapat dioksidasi (warna larutan tetap jingga).
    """)
    st.latex(r"\text{R-CH}_2\text{-OH} \xrightarrow{\text{CrO}_3/\text{H}_2\text{SO}_4} \text{R-COOH}")
    st.latex(r"\text{R}_2\text{CH-OH} \xrightarrow{\text{CrO}_3/\text{H}_2\text{SO}_4} \text{R}_2\text{C}=\text{O}")
    
    st.markdown("""
    #### **2.3.3 Uji Iodoform (Struktur Metil Karbinol)**
    Khusus diaplikasikan untuk alkohol yang memiliki struktur spesifik metil alfa $(CH_3CH(OH)-)$, seperti etanol atau 2-butanol. Reaksi dengan $I_2$ dalam suasana basa ($NaOH$) menghasilkan kristal padat iodoform ($CHI_3$) berwarna kuning yang berbau khas.
    """)
    st.latex(r"\text{R-CH(OH)-CH}_3 + 4\text{I}_2 + 6\text{NaOH} \rightarrow \text{R-COONa} + \text{CHI}_3\downarrow + 5\text{NaI} + 5\text{H}_2\text{O}")
    
    st.markdown("""
    #### **2.3.4 Uji Kompleks CAN (Ceric Ammonium Nitrate)**
    Digunakan untuk membedakan gugus alkohol dan eter secara umum. Alkohol bereaksi menggantikan ligan nitrat menghasilkan kompleks koordinasi berwarna **merah cerah**, sedangkan eter memberikan hasil negatif (larutan tetap kuning).
    """)
    st.latex(r"\text{ROH} + [\text{Ce(NO}_3)_6]^{2-} \rightarrow [\text{Ce(OR)(NO}_3)_5]^{2-} + \text{HNO}_3")
    
    st.markdown("""
    ---
    ### **2.4 Kimia Identifikasi Fenol**
    
    #### **2.4.1 Reaksi Deprotonasi Basa Kuat**
    Fenol bereaksi dengan $NaOH$ membentuk garam natrium fenoksida yang larut sempurna dalam air. Fenomena ini membuktikan sifat keasaman fenol yang lebih tinggi dibanding alkohol alifatik.
    """)
    st.latex(r"\text{C}_6\text{H}_5\text{OH} + \text{NaOH} \rightarrow \text{C}_6\text{H}_5\text{ONa} + \text{H}_2\text{O}")
    
    st.markdown("""
    #### **2.4.2 Uji Besi(III) Klorida ($FeCl_3$)**
    Ion fenoksida bertindak sebagai ligan yang mengikat ion logam pusat besi(III), membentuk senyawa kompleks koordinasi yang memancarkan warna **ungu tua / kehitaman** yang sangat khas.
    """)
    st.latex(r"6\text{C}_6\text{H}_5\text{OH} + \text{FeCl}_3 \rightarrow [\text{Fe(OC}_6\text{H}_5)_6]^{3-} + 3\text{H}^+ + 3\text{Cl}^-")
    
    st.markdown("""
    #### **2.4.3 Reaksi Brominasi (Trisubstitusi Air Brom)**
    Cincin aromatik pada fenol sangat aktif karena efek induksi donor elektron dari gugus $-OH$. Reaksi dengan air brom ($Br_2/H_2O$) langsung memicu reaksi substitusi di posisi orto dan para, membentuk endapan putih 2,4,6-tribromofenol.
    """)
    st.latex(r"\text{C}_6\text{H}_5\text{OH} + 3\text{Br}_2 \rightarrow \text{C}_6\text{H}_2\text{Br}_3\text{OH}\downarrow + 3\text{HBr}")

# --- [BAGIAN DIUBAH] BAB III: BREAKDOWN MENJADI SUB-BAB KECIL ---
elif pilihan_halaman == "📗 BAB III. ALDEHID DAN KETON":
    st.title("📗 BAB III. ALDEHID DAN KETON")
    st.write("---")
    
    st.markdown("""
    ### **3.1 Pengantar Gugus Karbonil**
    Aldehida ($R-CHO$) dan keton ($R-CO-R'$) merupakan pasangan isomer fungsional yang memiliki kesamaan gugus fungsi **karbonil ($C=O$)**. Perbedaan utamanya:
    * **Aldehida:** Karbon karbonil berikatan langsung dengan minimal satu atom hidrogen bebas pada ujung rantai.
    * **Keton:** Karbon karbonil terikat di antara dua gugus alkil atau aril internal.

    ---
    ### **3.2 Karakteristik Fisika Suku Senyawa**
    * **Aldehida:** Metanal (formaldehida) berwujud gas pada suhu kamar dengan bau menyengat (sering digunakan sebagai formalin). Suku di atasnya berupa cairan dengan aroma yang semakin harum menyerupai buah-buahan.
    * **Keton:** Suku rendah seperti propanon (aseton) berupa cairan encer yang bersifat volatil (mudah menguap), larut baik dalam air, dan sering dimanfaatkan sebagai pelarut organik nonpolar-polar menengah.

    ---
    ### **3.3 Reaksi Adisi Nukleofilik Karbonil**
    
    #### **3.3.1 Adisi Natrium Bisulit ($NaHSO_3$)**
    Serangan nukleofil bisulfit pada karbon karbonil aldehida atau golongan metil keton yang minim halangan sterik menghasilkan padatan kristal aduk berwarna putih yang sukar larut.
    """)
    st.latex(r"\text{R-CHO} + \text{NaHSO}_3 \rightarrow \text{R-CH(OH)-SO}_3\text{Na}")
    
    st.markdown("""
    #### **3.3.2 Mekanisme Hemiasetal dan Asetal**
    Merupakan bentuk reaksi reversibel di mana senyawa gugus karbonil diserang oleh molekul alkohol dengan bantuan katalis gas asam $HCl$.
    """)
    st.latex(r"\text{R-CHO} + \text{R'OH} \xrightarrow{\text{HCl}} \text{R-CH(OH)(OR')}")
    st.latex(r"\text{R-CH(OH)(OR')} + \text{R'OH} \xrightarrow{\text{HCl}} \text{R-CH(OR')}_2 + \text{H}_2\text{O}")
    
    st.markdown("""
    ---
    ### **3.4 Reaksi Diferensiasi Kualitatif (Daya Reduksi)**
    Aldehida bertindak sebagai agen reduktor kuat karena keberadaan atom hidrogen alfa langsung pada karbon karbonilnya. Keton tidak memiliki atom hidrogen tersebut sehingga memberikan hasil negatif pada uji-uji berikut:
    
    #### **3.4.1 Uji Tollens (Reaksi Cermin Perak)**
    Aldehida mengoksidasi dirinya menjadi asam karboksilat sekaligus mereduksi agen ion kompleks perak beramoniak $[\text{Ag(NH}_3)_2]^+$ menjadi endapan logam perak murni yang menempel di dinding dalam tabung reaksi.
    """)
    st.latex(r"\text{R-CHO} + 2[\text{Ag(NH}_3)_2]^+ + 3\text{OH}^- \rightarrow \text{R-COO}^- + 2\text{Ag}\downarrow + 4\text{NH}_3 + 2\text{H}_2\text{O}")
    
    st.markdown("""
    #### **3.4.2 Uji Fehling (Reduksi Kompleks Tembaga Tartrat)**
    Gugus aldehida mereduksi ion $Cu^{2+}$ berwana biru yang berada dalam bentuk kompleks tartrat alkalis, menghasilkan endapan padat merah bata kupro oksida ($Cu_2O$).
    """)
    st.latex(r"\text{R-CHO} + 2\text{Cu}^{2+} + 5\text{OH}^- \rightarrow \text{R-COO}^- + \text{Cu}_2\text{O}\downarrow + 3\text{H}_2\text{O}")
    
    #### **3.4.3 Uji Benedict (Reduksi Kompleks Tembaga Sitrat)**
    st.markdown("""
    Memiliki prinsip dasar yang sama dengan uji Fehling, namun ion tembaga dikomplekskan oleh gugus sitrat dalam kondisi alkalis lemah. Menghasilkan gradasi warna hijau, jingga, hingga endapan merah bata $Cu_2O$.
    """)
    st.latex(r"\text{R-CHO} + 2\text{Cu}^{2+} + 5\text{OH}^- \rightarrow \text{R-COO}^- + \text{Cu}_2\text{O}\downarrow + 3\text{H}_2\text{O}")

# --- [BAGIAN DIUBAH] BAB IV: BREAKDOWN MENJADI SUB-BAB KECIL ---
elif pilihan_halaman == "📕 BAB IV. ASAM KARBOKSILAT DAN DERIVATNYA":
    st.title("📕 BAB IV. ASAM KARBOKSILAT DAN DERIVATNYA")
    st.write("---")
    
    st.markdown("""
    ### **4.1 Pengantar Gugus Karboksil & Derivat**
    * **Asam Karboksilat ($R-COOH$):** Senyawa organik yang mengemban gugus fungsi karboksil, perpaduan terikat antara gugus fungsi karbonil ($-C=O$) dan hidroksil ($-OH$).
    * **Derivat Asam Karboksilat:** Senyawa turunan (seperti ester, halida asam, anhidrida, dan amida) di mana gugus $-OH$ karboksil telah digantikan oleh gugus nukleofilik lain ($-OR', -Cl, -NH_2$).

    ---
    ### **4.2 Sifat Fisika & Karakter Ikatan**
    * **Asam Karboksilat Rantai Pendek ($C_1 - C_4$):** Larut sempurna dalam air karena molekul gugus $-COOH$ mampu berinteraksi membentuk ikatan hidrogen melingkar yang stabil (**dimer**). Kelarutan menurun tajam seiring bertambahnya berat molekul rantai alkil nonpolar.
    * **Titik Didih:** Memiliki temperatur titik didih yang relatif sangat tinggi dibandingkan golongan senyawa organik lain dengan berat molekul setara akibat kuatnya jalinan asosiasi hidrogen.

    ---
    ### **4.3 Reaksi Kimia Utama Asam Karboksilat**
    
    #### **4.3.1 Reaksi Netralisasi Basa Kuat**
    Asam karboksilat bereaksi secara stoikiometris dengan $NaOH$ menghasilkan senyawa produk garam karboksilat yang larut baik dalam air dan molekul air bebas.
    """)
    st.latex(r"\text{R-COOH} + \text{NaOH} \rightarrow \text{R-COONa} + \text{H}_2\text{O}")
    
    st.markdown("""
    #### **4.3.2 Reaksi Penguraian Garam Bikarbonat ($NaHCO_3$)**
    Asam karboksilat memiliki tingkat keasaman yang cukup tinggi untuk mendeprotonasi basa lemah bikarbonat. Reaksi membebaskan gas karbon dioksida secara cepat (*effervescence*). **Uji ini membedakan asam karboksilat dengan fenol** (fenol gagal bereaksi).
    """)
    st.latex(r"\text{R-COOH} + \text{NaHCO}_3 \rightarrow \text{R-COONa} + \text{H}_2\text{O} + \text{CO}_2\uparrow")
    
    st.markdown("""
    *Uji Konfirmasi Air Barit:* Jika gas $CO_2$ dialirkan ke larutan air barit ($Ba(OH)_2$), akan terbentuk endapan putih barium karbonat ($BaCO_3$).
    """)
    st.latex(r"\text{CO}_2 + \text{Ba(OH)}_2 \rightarrow \text{BaCO}_3\downarrow + \text{H}_2\text{O}")
    
    st.markdown("""
    #### **4.3.3 Reaksi Esterifikasi Fischer**
    Reaksi kondensasi reversibel antara asam karboksilat dan alkohol dibantu katalisator dehidrasi asam kuat pekat ($H_2SO_4$). Reaksi ini menghasilkan senyawa golongan ester yang mengeluarkan aroma wangi khas buah-buahan (*fruity odor*).
    """)
    st.latex(r"\text{R-COOH} + \text{R'-OH} \xrightarrow{\text{H}_2\text{SO}_4} \text{R-COOR'} + \text{H}_2\text{O}")
    
    st.markdown("""
    #### **4.3.4 Reaksi Oksidasi Lanjut Khusus**
    Atom C karboksilat umumnya memiliki bilangan oksidasi tinggi (+3). Namun, pada asam karboksilat khusus yang masih memiliki atom hidrogen bebas terikat pada karbonil (seperti asam format atau asam oksalat), senyawa dapat dioksidasi oleh $KMnO_4/H_2SO_4$ menjadi gas $CO_2$.
    """)
    st.latex(r"\text{R-COOH} \xrightarrow{\text{Oksidator}} \text{CO}_2\uparrow + \text{H}_2\text{O}")
    
    st.markdown("""
    ---
    ### **4.4 Identifikasi Derivat (Uji Asam Hidroksamat)**
    Senyawa derivat seperti ester tidak bereaksi langsung dengan uji keasaman. Identifikasi dilakukan dengan mengkondensasikan ester bersama senyawa hidroksilamin ($NH_2OH$) membentuk asam hidroksamat. Gugus ini bertindak sebagai ligan multi-gigi yang menjepit logam Fe dari $FeCl_3$ membentuk kompleks khelat berwarna **merah violet / ungu intens**.
    
    *Tahap 1: Pembentukan Asam Hidroksamat dari Ester*
    """)
    st.latex(r"\text{R-COOR'} + \text{NH}_2\text{OH} \rightarrow \text{R-CONH-OH} + \text{R'-OH}")
    
    st.markdown("""
    *Tahap 2: Pembentukan Kompleks Khelat Ungu Besi(III)*
    """)
    st.latex(r"3\text{R-CONH-OH} + \text{FeCl}_3 \rightarrow \text{Fe(R-CONHO)}_3 + 3\text{HCl}")

# --- POST TEST (SAMA SEKALI TIDAK BERUBAH - SESUAI SKRIP PERTAMA) ---
elif pilihan_halaman == "🔬 POST TEST":
    st.title("🔀 Asisten Identifikasi Cerdas (Step-by-Step)")
    st.write("Sistem ini mensimulasikan penelusuran Identifikasi Kualitatif langkah demi langkah. Tekan tombol *Lanjut* untuk melanjutkan ke tahap reaksi berikutnya.")

    if not st.session_state.test_started:
        st.divider()
        senyawa = st.selectbox("Pilih Senyawa yang Akan Diuji (Sebagai Sampel Buta / Blind Sample):", ["-- Pilih Senyawa --"] + list(flowchart_paths.keys()))
        if st.button("Mulai Identifikasi 🚀", type="primary"):
            if senyawa == "-- Pilih Senyawa --":
                st.warning("⚠️ Harap pilih senyawa terlebih dahulu!")
            else:
                st.session_state.test_started = True
                st.session_state.senyawa_uji = senyawa
                st.session_state.current_step = 0
                st.session_state.log_history = []
                st.session_state.trigger_animation = True
                force_rerun()

    else:
        st.write("---")
        senyawa = st.session_state.senyawa_uji
        urutan = flowchart_paths[senyawa]

        col_visual, col_log = st.columns([1, 2.5])
        
        with col_visual:
            st.markdown("<h4 style='text-align: center;'>Visualisasi Laboratorium</h4>", unsafe_allow_html=True)
            tube_placeholder = st.empty() 
            status_placeholder = st.empty()
            
        with col_log:
            st.markdown("#### 📑 Buku Catatan Laboratorium & Analisis Teoritis")
            log_container = st.container()

        with log_container:
            for log in st.session_state.log_history:
                if "(+)" in log["hasil"]:
                    st.success(f"**Tahap {log['step']}: {log['pereaksi']}** ➔ **{log['hasil']}**\n\n**Persamaan Reaksi:**")
                    st.latex(log['reaksi'])
                    st.write(f"**Pembahasan:**\n{log['alasan']}")
                else:
                    st.error(f"**Tahap {log['step']}: {log['pereaksi']}** ➔ **{log['hasil']}**\n\n**Persamaan Reaksi:**")
                    st.latex(log['reaksi'])
                    st.write(f"**Pembahasan:**\n{log['alasan']}")

        # ---------------- LOGIKA ANIMASI & TOMBOL LANJUT ----------------
        if st.session_state.trigger_animation and st.session_state.current_step < len(urutan):
            pereaksi = urutan[st.session_state.current_step]
            
            tube_placeholder.markdown(render_tube("30%", "#f1f5f9", "tidak_ada"), unsafe_allow_html=True)
            status_placeholder.markdown(f"<div style='text-align:center;'><em>Menyiapkan sampel untuk {pereaksi}...</em></div>", unsafe_allow_html=True)
            time.sleep(1.0)
            
            warna_reagen = reagen_colors[pereaksi]
            tube_placeholder.markdown(render_tube("65%", warna_reagen, "tidak_ada"), unsafe_allow_html=True)
            status_placeholder.markdown(f"<div style='text-align:center;'><em>Meneteskan {pereaksi}...</em></div>", unsafe_allow_html=True)
            time.sleep(1.5)
            
            res = database_reaksi[senyawa][pereaksi]
            tube_placeholder.markdown(render_tube("65%", res["warna_akhir"], res["efek"]), unsafe_allow_html=True)
            status_placeholder.markdown("<div style='text-align:center; font-weight:bold;'>Melihat hasil reaksi...</div>", unsafe_allow_html=True)
            time.sleep(1.2)
            
            st.session_state.log_history.append({
                "step": st.session_state.current_step + 1,
                "pereaksi": pereaksi,
                "hasil": res["hasil"],
                "reaksi": res["reaksi"],
                "alasan": res["alasan"]
            })
            
            st.session_state.current_step += 1
            st.session_state.trigger_animation = False
            force_rerun()

        elif not st.session_state.trigger_animation:
            
            if st.session_state.current_step > 0:
                last_pereaksi = urutan[st.session_state.current_step - 1]
                res = database_reaksi[senyawa][last_pereaksi]
                tube_placeholder.markdown(render_tube("65%", res["warna_akhir"], res["efek"]), unsafe_allow_html=True)
            
            if st.session_state.current_step < len(urutan):
                next_pereaksi = urutan[st.session_state.current_step]
                status_placeholder.markdown("<div style='text-align:center; color:#475569;'>Menunggu konfirmasi praktikan...</div>", unsafe_allow_html=True)
                
                with col_visual:
                    st.write("") 
                    if st.button(f"Lanjutkan ke Uji {next_pereaksi} ⏭️", use_container_width=True, type="primary"):
                        st.session_state.trigger_animation = True
                        force_rerun()
                        
            else:
                status_placeholder.markdown("<div style='text-align:center; font-weight:bold; color:#10b981;'>Seluruh tahap identifikasi selesai!</div>", unsafe_allow_html=True)
                with log_container:
                    st.info(f"🎉 **KESIMPULAN:** Berdasarkan alur eliminasi dan uji spesifik, sampel tak dikenal ini secara sah terbukti sebagai senyawa: **{senyawa.upper()}**.")
                
                with col_visual:
                    st.write("")
                    if st.button("🔄 Uji Sampel Baru", use_container_width=True):
                        st.session_state.test_started = False
                        force_rerun()
