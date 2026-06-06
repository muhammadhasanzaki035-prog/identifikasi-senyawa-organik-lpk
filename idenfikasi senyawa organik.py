import streamlit as st
import time

# ==============================================================================
# 1. KONFIGURASI HALAMAN
# ==============================================================================
st.set_page_config(
    page_title="OrganicChem | Edu-Lab Platform",
    page_icon="🧪",
    layout="wide"
)

# ==============================================================================
# 2. CUSTOM CSS INTERAKTIF (VERSI MODERN)
# ==============================================================================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f0f9ff, #f8fafc);
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f766e, #14b8a6);
}
[data-testid="stSidebar"] * {
    color: white !important;
}
.banner-utama {
    background: linear-gradient(135deg, #06b6d4, #3b82f6);
    padding: 35px;
    border-radius: 15px;
    color: white;
    margin-bottom: 30px;
    box-shadow: 0 6px 20px rgba(59,130,246,0.25);
}
.kotak-analisis {
    border-left: 6px solid #14b8a6;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
    background: linear-gradient(135deg, #f0fdfa, #ecfeff);
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}
.stButton > button {
    border-radius: 12px;
    border: none;
    background: linear-gradient(135deg, #14b8a6, #0ea5e9);
    color: white;
    font-weight: 600;
    transition: all 0.3s ease;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(14,165,233,0.3);
}
.tube-wrap {
    display: flex;
    justify-content: center;
    height: 350px;
    padding-top: 20px;
}
.tube-glass {
    width: 80px;
    height: 300px;
    border: 4px solid #64748b;
    border-top: none;
    border-radius: 0 0 40px 40px;
    position: relative;
    overflow: hidden;
    background: rgba(15, 23, 42, 0.16);
    box-shadow: inset 0 0 15px rgba(0,0,0,0.25);
    backdrop-filter: blur(3px);
}
.tube-liquid {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    transition: height 1.2s ease, background 1.2s ease;
}
.precipitate-layer {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 50px;
    background: linear-gradient(to top, #ffffff 0%, #f1f5f9 80%, #cbd5e1 100%) !important;
    box-shadow: 0 -4px 10px rgba(0,0,0,0.3);
    border-top: 2.5px solid #94a3b8;
}
.cloudy-layer {
    position: absolute;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(to bottom, rgba(255,255,255,0.85), rgba(241,245,249,0.95));
}
.bubble-fx {
    position: absolute;
    background: rgba(0,0,0,0.15);
    border-radius: 50%;
    width: 8px;
    height: 8px;
    animation: floatUp 1.8s infinite ease-in;
}
@keyframes floatUp {
    0% { bottom: 0px; opacity: 1; }
    100% { bottom: 250px; opacity: 0; }
}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. FUNGSI HELPER & DATABASE (FORMAT LATEX PRESISI)
# ==============================================================================
def force_rerun():
    if hasattr(st, 'rerun'):
        st.rerun()
    elif hasattr(st, 'experimental_rerun'):
        st.experimental_rerun()

def render_tube(tinggi, warna, efek):
    e_html = ""
    if efek == "precipitate":
        e_html = "<div class='precipitate-layer'></div>"
    elif efek == "cloudy":
        e_html = "<div class='cloudy-layer'></div>"
    elif efek == "bubbles":
        e_html = "<div class='bubble-fx' style='left:20px;'></div><div class='bubble-fx' style='left:50px; animation-delay:0.5s;'></div>"
    return f"<div class='tube-wrap'><div class='tube-glass'><div class='tube-liquid' style='height:{tinggi}; background:{warna};'>{e_html}</div></div></div>"

reagen_colors = {
    "Uji Golongan Alkohol": "#facc15", 
    "Uji Oksidasi Alkohol": "#f97316", 
    "Uji Golongan Alkohol Tersier": "#f8fafc", 
    "Uji Golongan Alkohol Sekunder": "#f8fafc", 
    "Uji Golongan Alkanal/Aldehida (Bisulfit)": "#f8fafc", 
    "Uji Reduksi Golongan Alkanal (Fehling)": "#3b82f6", 
    "Uji Spesifik Golongan Alkanal (Schiff)": "#f8fafc",
    "Uji Golongan Metil Keton / Metil Karbinol": "#f8fafc",
    "Uji Golongan Ester": "#f8fafc",
    "Uji Golongan Asam Karboksilat": "#f8fafc"
}

flowchart_paths = {
    "Alkohol Primer": ["Uji Golongan Alkohol", "Uji Oksidasi Alkohol", "Uji Golongan Alkohol Sekunder"],
    "Alkohol Sekunder": ["Uji Golongan Alkohol", "Uji Oksidasi Alkohol", "Uji Golongan Alkohol Sekunder", "Uji Golongan Metil Keton / Metil Karbinol"],
    "Alkohol Tersier": ["Uji Golongan Alkohol", "Uji Oksidasi Alkohol", "Uji Golongan Alkohol Tersier"],
    "Aldehida (Alkanal)": ["Uji Golongan Alkohol", "Uji Golongan Alkanal/Aldehida (Bisulfit)", "Uji Reduksi Golongan Alkanal (Fehling)", "Uji Spesifik Golongan Alkanal (Schiff)"],
    "Keton (Alkanon)": ["Uji Golongan Alkohol", "Uji Golongan Alkanal/Aldehida (Bisulfit)", "Uji Reduksi Golongan Alkanal (Fehling)", "Uji Golongan Metil Keton / Metil Karbinol"],
    "Ester (Alkil Alkanoat)": ["Uji Golongan Alkohol", "Uji Golongan Alkanal/Aldehida (Bisulfit)", "Uji Golongan Ester"],
    "Asam Karboksilat": ["Uji Golongan Alkohol", "Uji Golongan Alkanal/Aldehida (Bisulfit)", "Uji Golongan Ester", "Uji Golongan Asam Karboksilat"],
    "Alkana / Hidrokarbon Jenuh": ["Uji Golongan Alkohol", "Uji Golongan Alkanal/Aldehida (Bisulfit)", "Uji Golongan Ester", "Uji Golongan Asam Karboksilat"]
}

database_reaksi = {
    "Alkohol Primer": {
        "Uji Golongan Alkohol": {
            "hasil": "(+) Merah Ceri", 
            "reaksi": r"R-OH + [Ce(NO_3)_6]^{2-} \rightarrow [Ce(OR)(NO_3)_5]^{2-} + HNO_3", 
            "alasan": "Gugus -OH bebas bereaksi menggantikan ligan nitrat pada ion Cerium(IV) membentuk senyawa kompleks koordinasi berwarna merah ceri.", 
            "warna_akhir": "#ef4444", "efek": "none"
        },
        "Uji Oksidasi Alkohol": {
            "hasil": "(+) Hijau", 
            "reaksi": r"3\ R-CH_2OH + 2\ CrO_3 + 3\ H_2SO_4 \rightarrow 3\ R-CHO + Cr_2(SO_4)_3 + 6\ H_2O", 
            "alasan": "Memiliki atom hidrogen alfa. Gugus -OH dioksidasi menjadi aldehida, sedangkan Kromium(VI) jingga tereduksi menjadi Kromium(III) hijau.", 
            "warna_akhir": "#10b981", "efek": "none"
        },
        "Uji Golongan Alkohol Sekunder": {
            "hasil": "(-) Bening", 
            "reaksi": r"R-CH_2OH + HCl \xrightarrow{ZnCl_2} \text{Tidak ada reaksi}", 
            "alasan": "Karbokation primer sangat tidak stabil sehingga tidak mampu bereaksi dengan pereaksi Lucas pada suhu kamar.", 
            "warna_akhir": "#f8fafc", "efek": "none"
        }
    },
    "Alkohol Sekunder": {
        "Uji Golongan Alkohol": {
            "hasil": "(+) Merah Ceri", 
            "reaksi": r"R-OH + [Ce(NO_3)_6]^{2-} \rightarrow [Ce(OR)(NO_3)_5]^{2-} + HNO_3", 
            "alasan": "Ikatan koordinasi terbentuk antara atom oksigen pada gugus hidroksil sekunder dengan logam Cerium pusat.", 
            "warna_akhir": "#ef4444", "efek": "none"
        },
        "Uji Oksidasi Alkohol": {
            "hasil": "(+) Hijau", 
            "reaksi": r"3\ R_2CH-OH + 2\ CrO_3 + 3\ H_2SO_4 \rightarrow 3\ R_2C=O + Cr_2(SO_4)_3 + 6\ H_2O", 
            "alasan": "Alkohol sekunder dioksidasi menjadi keton, ditandai dengan perubahan warna larutan dari jingga ke hijau.", 
            "warna_akhir": "#10b981", "efek": "none"
        },
        "Uji Golongan Alkohol Sekunder": {
            "hasil": "(+) Emulsi Putih", 
            "reaksi": r"R_2CH-OH + HCl \xrightarrow{ZnCl_2} R_2CH-Cl \downarrow + H_2O", 
            "alasan": "Karbokation sekunder memiliki stabilitas menengah. Bereaksi menghasilkan alkil klorida setelah 5-10 menit dengan bantuan pemanasan.", 
            "warna_akhir": "#e2e8f0", "efek": "cloudy"
        },
        "Uji Golongan Metil Keton / Metil Karbinol": {
            "hasil": "(+) Endapan Kuning", 
            "reaksi": r"R-CH(OH)-CH_3 + 4\ I_2 + 6\ NaOH \rightarrow CHI_3 \downarrow + R-COONa + 5\ NaI + 5\ H_2O", 
            "alasan": "Struktur metil karbinol dioksidasi oleh iodin menjadi metil keton, lalu membentuk kristal iodoform berwarna kuning.", 
            "warna_akhir": "#fef08a", "efek": "precipitate"
        }
    },
    "Alkohol Tersier": {
        "Uji Golongan Alkohol": {
            "hasil": "(+) Merah Ceri", 
            "reaksi": r"R-OH + [Ce(NO_3)_6]^{2-} \rightarrow [Ce(OR)(NO_3)_5]^{2-} + HNO_3", 
            "alasan": "Memiliki gugus -OH bebas yang dapat membentuk kompleks koordinasi berwarna merah dengan ceric ammonium nitrate.", 
            "warna_akhir": "#ef4444", "efek": "none"
        },
        "Uji Oksidasi Alkohol": {
            "hasil": "(-) Tetap Jingga", 
            "reaksi": r"R_3C-OH + CrO_3 \rightarrow \text{Tidak bereaksi}", 
            "alasan": "Alkohol tersier tidak memiliki atom hidrogen alfa sehingga tidak dapat dioksidasi oleh pereaksi Jones.", 
            "warna_akhir": "#f97316", "efek": "none"
        },
        "Uji Golongan Alkohol Tersier": {
            "hasil": "(+) Emulsi Putih (Seketika)", 
            "reaksi": r"R_3C-OH + HCl \xrightarrow{ZnCl_2} R_3C-Cl \downarrow + H_2O", 
            "alasan": "Membentuk karbokation tersier yang sangat stabil, sehingga reaksi substitusi berjalan instan membentuk kabut keruh alkil klorida.", 
            "warna_akhir": "#94a3b8", "efek": "cloudy"
        }
    },
    "Aldehida (Alkanal)": {
        "Uji Golongan Alkohol": {
            "hasil": "(-) Kuning", 
            "reaksi": r"R-CHO + [Ce(NO_3)_6]^{2-} \rightarrow \text{Tidak bereaksi}", 
            "alasan": "Aldehida tidak memiliki gugus hidroksil (-OH) bebas sehingga warna pereaksi tetap kuning.", 
            "warna_akhir": "#facc15", "efek": "none"
        },
        "Uji Golongan Alkanal/Aldehida (Bisulfit)": {
            "hasil": "(+) Endapan Putih", 
            "reaksi": r"R-CHO + NaHSO_3 \rightarrow R-CH(OH)SO_3Na \downarrow", 
            "alasan": "Nukleofil bisulfit menyerang gugus karbonil aldehida yang reaktif, menghasilkan produk adisi berupa kristal putih.", 
            "warna_akhir": "#ffffff", "efek": "precipitate"
        },
        "Uji Reduksi Golongan Alkanal (Fehling)": {
            "hasil": "(+) Merah Bata", 
            "reaksi": r"R-CHO + 2\ Cu^{2+} + 5\ OH^- \rightarrow R-COO^- + Cu_2O \downarrow + 3\ H_2O", 
            "alasan": "Aldehida adalah reduktor kuat yang mereduksi kupri oksida menjadi endapan tembaga(I) oksida berwarna merah bata.", 
            "warna_akhir": "#b91c1c", "efek": "precipitate"
        },
        "Uji Spesifik Golongan Alkanal (Schiff)": {
            "hasil": "(+) Ungu / Magenta", 
            "reaksi": r"\text{Aldehida} + \text{Pereaksi Schiff} \rightarrow \text{Kompleks Magenta}", 
            "alasan": "Reaksi adisi spesifik yang mengembalikan struktur warna p-rosanilin menjadi ungu murni.", 
            "warna_akhir": "#d946ef", "efek": "none"
        }
    },
    "Keton (Alkanon)": {
        "Uji Golongan Alkohol": {
            "hasil": "(-) Kuning", 
            "reaksi": r"\text{Keton} + [Ce(NO_3)_6]^{2-} \rightarrow \text{Tidak bereaksi}", 
            "alasan": "Keton tidak memiliki gugus fungsi hidroksil.", 
            "warna_akhir": "#facc15", "efek": "none"
        },
        "Uji Golongan Alkanal/Aldehida (Bisulfit)": {
            "hasil": "(+) Endapan Putih", 
            "reaksi": r"CH_3-CO-CH_3 + NaHSO_3 \rightarrow (CH_3)_2C(OH)SO_3Na \downarrow", 
            "alasan": "Keton suku rendah (seperti aseton) memiliki halangan sterik kecil sehingga masih bisa diadisi oleh bisulfit membentuk endapan putih.", 
            "warna_akhir": "#ffffff", "efek": "precipitate"
        },
        "Uji Reduksi Golongan Alkanal (Fehling)": {
            "hasil": "(-) Tetap Biru", 
            "reaksi": r"\text{Keton} + Cu^{2+} \rightarrow \text{Tidak bereaksi}", 
            "alasan": "Keton tidak memiliki atom hidrogen pada gugus karbonil sehingga tidak bersifat reduktor.", 
            "warna_akhir": "#3b82f6", "efek": "none"
        },
        "Uji Golongan Metil Keton / Metil Karbinol": {
            "hasil": "(+) Endapan Kuning", 
            "reaksi": r"R-CO-CH_3 + 3\ I_2 + 4\ NaOH \rightarrow CHI_3 \downarrow + R-COONa + 3\ NaI + 3\ H_2O", 
            "alasan": "Memiliki gugus metil yang terikat langsung pada karbonil, sehingga bereaksi positif membentuk endapan kuning iodoform.", 
            "warna_akhir": "#fef08a", "efek": "precipitate"
        }
    },
    "Ester (Alkil Alkanoat)": {
        "Uji Golongan Alkohol": {
            "hasil": "(-) Kuning", "reaksi": r"\text{Ester} + [Ce(NO_3)_6]^{2-} \rightarrow \text{Tidak bereaksi}", "alasan": "Tidak memiliki gugus hidroksil bebas.", "warna_akhir": "#facc15", "efek": "none"
        },
        "Uji Golongan Alkanal/Aldehida (Bisulfit)": {
            "hasil": "(-) Bening", "reaksi": r"\text{Ester} + NaHSO_3 \rightarrow \text{Tidak bereaksi}", "alasan": "Gugus ester stabil akibat efek resonansi elektron sehingga tidak reaktif terhadap nukleofil lemah.", "warna_akhir": "#f8fafc", "efek": "none"
        },
        "Uji Golongan Ester": {
            "hasil": "(+) Merah Violet", 
            "reaksi": r"3\ R-CONHOH + FeCl_3 \rightarrow Fe(R-CONHO)_3 + 3\ HCl", 
            "alasan": "Ester bereaksi dengan hidroksilamin membentuk asam hidroksamat yang mengikat besi(III) menjadi kompleks berwarna violet.", 
            "warna_akhir": "#c026d3", "efek": "none"
        }
    },
    "Asam Karboksilat": {
        "Uji Golongan Alkohol": {
            "hasil": "(-) Kuning", "reaksi": r"R-COOH + [Ce(NO_3)_6]^{2-} \rightarrow \text{Tidak bereaksi}", "alasan": "Oksigen hidroksil ditarik oleh efek resonansi karbonil sehingga sifat nukleofilnya hilang.", "warna_akhir": "#facc15", "efek": "none"
        },
        "Uji Golongan Alkanal/Aldehida (Bisulfit)": {
            "hasil": "(-) Bening", "reaksi": r"R-COOH + NaHSO_3 \rightarrow \text{Tidak bereaksi}", "alasan": "Senyawa ini tidak mengandung gugus fungsi aldehida atau keton.", "warna_akhir": "#f8fafc", "efek": "none"
        },
        "Uji Golongan Ester": {
            "hasil": "(-) Bening", "reaksi": r"R-COOH + NH_2OH + FeCl_3 \rightarrow \text{Tidak bereaksi}", "alasan": "Asam karboksilat bebas tidak membentuk hidroksamat pada kondisi uji ini.", "warna_akhir": "#f8fafc", "efek": "none"
        },
        "Uji Golongan Asam Karboksilat": {
            "hasil": "(+) Gelembung & Keruh", 
            "reaksi": r"CO_2 + Ba(OH)_2 \rightarrow BaCO_3 \downarrow + H_2O", 
            "alasan": "Sifat asamnya mendonasikan proton untuk mengurai bikarbonat menjadi gas CO2. Gas tersebut mengeruhkan air barit karena membentuk barium karbonat.", 
            "warna_akhir": "#f8fafc", "efek": "bubbles"
        }
    },
    "Alkana / Hidrokarbon Jenuh": {
        "Uji Golongan Alkohol": {
            "hasil": "(-) Kuning", "reaksi": r"\text{Alkana} + [Ce(NO_3)_6]^{2-} \rightarrow \text{Tidak bereaksi}", "alasan": "Senyawa nonpolar inert, tidak memiliki gugus hidroksil.", "warna_akhir": "#facc15", "efek": "none"
        },
        "Uji Golongan Alkanal/Aldehida (Bisulfit)": {
            "hasil": "(-) Bening", "reaksi": r"\text{Alkana} + NaHSO_3 \rightarrow \text{Tidak bereaksi}", "alasan": "Tidak memiliki gugus fungsi karbonil.", "warna_akhir": "#f8fafc", "efek": "none"
        },
        "Uji Golongan Ester": {
            "hasil": "(-) Bening", "reaksi": r"\text{Alkana} + NH_2OH \rightarrow \text{Tidak bereaksi}", "alasan": "Tidak memiliki gugus fungsi ester.", "warna_akhir": "#f8fafc", "efek": "none"
        },
        "Uji Golongan Asam Karboksilat": {
            "hasil": "(-) Bening", "reaksi": r"\text{Alkana} + NaHCO_3 \rightarrow \text{Tidak bereaksi}", 
            "alasan": "Hidrokarbon jenuh bersifat inert. Kegagalan di seluruh uji gugus fungsi membuktikan sampel ini adalah golongan alkana.", 
            "warna_akhir": "#f8fafc", "efek": "none"
        }
    }
}

# Inisialisasi session state jika belum ada
if "test_started" not in st.session_state:
    st.session_state.test_started = False
if "current_step" not in st.session_state:
    st.session_state.current_step = 0
if "log_history" not in st.session_state:
    st.session_state.log_history = []
if "trigger_animation" not in st.session_state:
    st.session_state.trigger_animation = False

# ==============================================================================
# 4. SIDEBAR NAVIGASI
# ==============================================================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3022/3022607.png", width=75)
    st.title("OrganicChem v1.0")
    st.write("🔬 *E-Learning & Lab Simulator*")
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
# 5. LOGIKA KONTEN TIAP HALAMAN (BERSIH TOTAL & INTERAKTIF)
# ==============================================================================

if pilihan_halaman == "🏠 HALAMAN UTAMA":
    st.markdown("""
        <div class="banner-utama">
            <h1 style='color: white; margin-bottom: 5px; font-weight: 700;'>Selamat Datang di OrganicChem! 👋</h1>
            <p style='font-size: 1.2em; opacity: 0.95;'>Platform Eksplorasi Dunia Kimia Organik Tanpa Batas Melalui Media Pembelajaran Mandiri & Simulasi Identifikasi Gugus Fungsi</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.subheader("💡 Tentang Platform Ini")
    st.write(
        "Platform ini dirancang khusus untuk membantu memahami materi teoritis "
        "sekaligus visualisasi reaksi uji kualitatif senyawa organik di laboratorium secara interaktif—kapan saja dan dimana saja, layaknya memiliki laboratorium pribadi."
    )
    st.markdown("---")
    
    st.markdown("### 📜 Petunjuk Penggunaan")
    st.write("Ikuti langkah-langkah berikut untuk memulai petualangan laboratorium virtualmu:")
    
    p1, p2, p3 = st.columns(3)
    
    with p1:
        st.markdown("""
        <div style="background: white; padding: 20px; border-radius: 12px; border-top: 5px solid #0f766e; box-shadow: 0 4px 6px rgba(0,0,0,0.05); min-height: 180px;">
            <h4 style="margin-top:0; color:#0f766e;">📖 Langkah 1: Pelajari</h4>
            <p style="font-size: 0.95em; color: #475569;">Buka <b>Menu Navigasi</b> di samping kiri. Pilih materi dari <b>BAB I hingga BAB IV</b> untuk membaca teori dasar, sifat fisik/kimia, dan persamaan reaksi kimia senyawa organik.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with p2:
        st.markdown("""
        <div style="background: white; padding: 20px; border-radius: 12px; border-top: 5px solid #14b8a6; box-shadow: 0 4px 6px rgba(0,0,0,0.05); min-height: 180px;">
            <h4 style="margin-top:0; color:#14b8a6;">🧪 Langkah 2: Simulasi</h4>
            <p style="font-size: 0.95em; color: #475569;">Masuk ke menu <b>🔬 POST TEST</b>. Di sana, kamu bisa memilih sampel misterius (<i>Blind Sample</i>) untuk menguji pemahaman analisismu secara langsung.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with p3:
        st.markdown("""
        <div style="background: white; padding: 20px; border-radius: 12px; border-top: 5px solid #0ea5e9; box-shadow: 0 4px 6px rgba(0,0,0,0.05); min-height: 180px;">
            <h4 style="margin-top:0; color:#0ea5e9;">📊 Langkah 3: Amati</h4>
            <p style="font-size: 0.95em; color: #475569;">Klik tombol reaksi, amati perubahan visual pada <b>Visual Lab</b> (warna/endapan/gas), serta baca hasil evaluasi otomatis pada tab <b>Logbook & Analisis</b>.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.info("💡 **Tips:** Pastikan koneksi internet stabil agar transisi animasi tabung reaksi berjalan dengan mulus!")

# --- BAB I ---
elif pilihan_halaman == "📘 BAB I. HIDROKARBON":
    st.title("📘 BAB I. HIDROKARBON")
    st.write("---")
    
    st.markdown("""
    Hidrokarbon adalah senyawa organik yang seluruh strukturnya hanya tersusun atas unsur karbon (C) dan hidrogen (H). Berdasarkan jenis ikatannya, hidrokarbon alifatik dibagi menjadi hidrokarbon jenuh (alkana) dan tidak jenuh (alkena dan alkuna). Sementara itu, hidrokarbon aromatik memiliki rantai siklik konjugasi yang sangat stabil.

    #### **A. Sifat Fisika Hidrokarbon**
    * **Wujud Zat (pada suhu kamar):**
      * Suhu rendah ($C_1 - C_4$) berwujud gas (contoh: metana, etana, etena, etuna).
      * Suhu sedang ($C_5 - C_{17}$) berwujud cair (contoh: pentana, heksana, benzena).
      * Suhu tinggi ($\ge C_{18}$) berwujud padat (contoh: parafin padat).
    * **Kelarutan:** Bersifat nonpolar, sehingga tidak larut dalam air (pelarut polar). Hidrokarbon larut dengan baik dalam sesama pelarut organik nonpolar seperti kloroform ($CHCl_3$), karbon tetraklorida ($CCl_4$), atau eter.
    * **Titik Didih dan Titik Leleh:** Meningkat seiring bertambahnya massa molekul (panjang rantai karbon). Untuk isomer dengan jumlah atom karbon sama, senyawa dengan rantai lurus memiliki titik didih lebih tinggi dibandingkan rantai bercabang karena luas permukaan kontak antarmolekul yang lebih besar.
    * **Densitas:** Memiliki massa jenis (densitas) yang lebih kecil daripada air. Jika dicampur dengan air, lapisan hidrokarbon akan selalu berada di bagian atas.

    #### **B. Sifat Kimia & Reaksi Identifikasi Hidrokarbon**
    
    **1. Alkana (Hidrokarbon Jenuh)**
    * Disebut juga parafin (afinitas kecil) karena sangat tidak reaktif terhadap sebagian besar pereaksi seperti asam kuat, basa kuat, dan oksidator pada suhu kamar.
    * **Uji Iodo (Substitusi Halogen):** Alkana dapat bereaksi dengan halogen ($I_2$) melalui reaksi substitusi radikal bebas dengan bantuan paparan sinar ultraviolet (UV) atau pemanasan tinggi. Reaksi berjalan lambat dan ditandai dengan memudarnya warna ungu dari iodium.
    """)
    
    st.latex(r"\text{CH}_4 + \text{I}_2 \xrightarrow{\text{Sinar UV} / \Delta} \text{CH}_3\text{I} + \text{HI}")
    
    st.markdown("""
    **2. Alkena dan Alkuna (Hidrokarbon Tidak Jenuh)**
    * Sangat reaktif karena memiliki ikatan rangkap 2 atau rangkap 3 yang kaya akan elektron, sehingga mudah mengalami pemutusan ikatan rangkap (adisi).
    * **Uji Adisi Iodium:** Mengadisi halogen pada ikatan rangkap tanpa memerlukan bantuan sinar UV. Ditandai dengan warna ungu iodium yang memudar/hilang seketika.
    """)
    
    st.latex(r"\text{R-CH}=\text{CH-R} + \text{I}_2 \rightarrow \text{R-CH(I)-CH(I)-R}")
    
    st.markdown("""
    * **Uji Baeyer (Oksidasi dengan $KMnO_4$):** Alkena atau alkuna dioksidasi oleh larutan kalium permanganat encer dalam suasana netral/basa menghasilkan senyawa glikol. Uji positif ditandai dengan hilangnya warna ungu $KMnO_4$ and terbentuknya endapan cokelat $MnO_2$.
    """)
    
    st.latex(r"3\text{CH}_2=\text{CH}_2 + 2\text{KMnO}_4 + 4\text{H}_2\text{O} \rightarrow 3\text{HO-CH}_2\text{-CH}_2\text{-OH} + 2\text{MnO}_2\downarrow \text{(endapan cokelat)} + 2\text{KOH}")
    
    st.markdown("""
    **3. Benzena (Hidrokarbon Aromatik)**
    * Memiliki struktur siklik dengan elektron pi yang terdelokalisasi (resonansi) yang memenuhi aturan Hückel ($4n + 2$), membuat intinya sangat stabil.
    * **Uji Bakar:** Ketika dibakar dengan api langsung pada cawan porselin, benzena menghasilkan nyala api berminyak disertai jelaga hitam yang sangat tebal. Jelaga ini terbentuk akibat tingginya persentase kadar karbon dalam benzena dibandingkan kadar hidrogennya.
    """)
    
    st.latex(r"\text{Benzena} + \text{O}_2 \rightarrow \text{C}_{(s)} \text{ [Jelaga hitam]} + \text{CO} + \text{H}_2\text{O (Pembakaran tidak sempurna)}")
    
    st.markdown("""
    * **Reaksi Substitusi Elektrofilik:** Benzena sukar mengalami adisi melainkan cenderung mengalami reaksi substitusi. Contohnya adalah reaksi Nitrasi menggunakan campuran asam nitrat pekat dan asam sulfat pekat sebagai katalis.
    """)
    
    st.latex(r"\text{C}_6\text{H}_6 + \text{HNO}_3 \xrightarrow{\text{H}_2\text{SO}_4\text{ pekat}} \text{C}_6\text{H}_5\text{NO}_2 \text{ (Nitrobenzena)} + \text{H}_2\text{O}")

# --- BAB II ---
elif pilihan_halaman == "📙 BAB II. ALKOHOL, ETER, DAN FENOL":
    st.title("📙 BAB II. ALKOHOL, ETER, DAN FENOL")
    st.write("---")
    
    st.markdown("""
    #### **A. Sifat Fisika & Klasifikasi**
    * **Alkohol ($R - OH$):** Turunan alkana di mana satu atau lebih atom H digantikan oleh gugus hidroksil ($-OH$). Alkohol diklasifikasikan menjadi alkohol primer ($1^\circ$), sekunder ($2^\circ$), dan tersier ($3^\circ$) berdasarkan jenis atom C yang mengikat gugus $-OH$. Alkohol suhu rendah mudah larut dalam air karena sanggup membentuk ikatan hidrogen dengan molekul air. Kelarutan berkurang seiring bertambah panjangnya rantai karbon, namun meningkat pada struktur yang bercabang banyak.
    * **Eter ($R^1 - O - R^2$):** Isomer fungsional dari alkohol. Titik didih eter jauh lebih rendah dibandingkan alkohol isomernya karena tidak memiliki ikatan hidrogen antar-sesama molekul eter. Kelarutannya dalam air mirip dengan alkohol karena oksigen pada eter masih bisa menerima ikatan hidrogen dari air.
    * **Fenol ($C_6H_5OH$):** Senyawa hidrokarbon aromatik yang mengikat gugus fungsi $-OH$ langsung pada cincin benzena. Berupa padatan/hablur pada suhu kamar, sedikit larut dalam air, dan larutannya bersifat asam lemah karena ion fenoksida yang terbentuk distabilkan oleh resonansi.

    #### **B. Persamaan Reaksi Kimia Alkohol & Eter**
    
    **1. Pereaksi Lucas (Substitusi Gugus $-OH$ oleh Cl)**
    * Menggunakan campuran $HCl$ pekat dan katalis $ZnCl_2$ untuk membedakan jenis alkohol berdasarkan kecepatan reaksinya.
    * Alkohol $3^\circ$: Bereaksi seketika (larutan langsung keruh/terbentuk dua lapisan terpisah).
    * Alkohol $2^\circ$: Bereaksi dalam waktu 5–10 menit dengan sedikit pemanasan.
    * Alkohol $1^\circ$: Tidak bereaksi pada suhu kamar.
    """)
    
    st.latex(r"\text{R}_3\text{C-OH (Alkohol } 3^\circ\text{)} + \text{HCl} \xrightarrow{\text{ZnCl}_2} \text{R}_3\text{C-Cl}\downarrow \text{ (Keruh/Alkil klorida)} + \text{H}_2\text{O}")
    
    st.markdown("""
    **2. Pereaksi Jones (Oksidasi Alkohol)**
    * Menggunakan kromium trioksida ($CrO_3$) dalam asam sulfat pekat. Uji positif ditandai dengan perubahan warna pereaksi dari jingga menjadi hijau.
    * Alkohol $1^\circ$ dioksidasi menjadi Aldehida, lalu berlanjut menjadi Asam Karboksilat.
    * Alkohol $2^\circ$ dioksidasi menjadi Keton.
    * Alkohol $3^\circ$ tidak dapat dioksidasi (warna tetap jingga).
    """)
    
    st.latex(r"\text{R-CH}_2\text{-OH (Alkohol } 1^\circ\text{)} \xrightarrow{\text{CrO}_3/\text{H}_2\text{SO}_4} \text{R-COOH (Asam Karboksilat) [Jingga } \rightarrow \text{ Hijau]}")
    st.latex(r"\text{R}_2\text{CH-OH (Alkohol } 2^\circ\text{)} \xrightarrow{\text{CrO}_3/\text{H}_2\text{SO}_4} \text{R}_2\text{C}=\text{O (Keton) [Jingga } \rightarrow \text{ Hijau]}")
    
    st.markdown("""
    **3. Uji Iodoform**
    * Khusus untuk alkohol yang memiliki gugus metil alfa $(CH_3CH(OH))$, seperti etanol atau 2-propanol. Bereaksi dengan $I_2$ dalam suasana basa ($NaOH$) membentuk endapan kuning kristal iodoform ($CHI_3$) yang berbau khas.
    """)
    
    st.latex(r"\text{R-CH(OH)-CH}_3 + 4\text{I}_2 + 6\text{NaOH} \rightarrow \text{R-COONa} + \text{CHI}_3\downarrow \text{ (Endapan Kuning)} + 5\text{NaI} + 5\text{H}_2\text{O}")
    
    st.markdown("""
    **4. Pereaksi Ceric Ammonium Nitrate (CAN)**
    * Alkohol bereaksi membentuk senyawa kompleks koordinasi berwarna merah cerah, sedangkan eter memberikan hasil negatif (warna tetap).
    """)
    
    st.latex(r"\text{ROH} + [\text{Ce(NO}_3)_6]^{2-} \rightarrow [\text{Ce(OR)(NO}_3)_5]^{2-} \text{ (Kompleks Merah)} + \text{HNO}_3")
    
    st.markdown("""
    #### **C. Persamaan Reaksi Kimia Fenol**
    
    **1. Reaksi dengan Basa Kuat ($NaOH$)**
    * Membentuk garam natrium fenoksida yang larut dalam air (menunjukkan sifat asam lemah fenol).
    """)
    
    st.latex(r"\text{C}_6\text{H}_5\text{OH} + \text{NaOH} \rightarrow \text{C}_6\text{H}_5\text{ONa (Natrium fenoksida)} + \text{H}_2\text{O}")
    
    st.markdown("""
    **2. Uji Besi(III) Klorida ($FeCl_3$)**
    * Ion fenoksida membentuk senyawa kompleks koordinasi dengan besi(III) yang menghasilkan warna ungu tua/kehitaman yang khas.
    """)
    
    st.latex(r"6\text{C}_6\text{H}_5\text{OH} + \text{FeCl}_3 \rightarrow [\text{Fe(OC}_6\text{H}_5)_6]^{3-} \text{ (Kompleks Ungu)} + 3\text{H}^+ + 3\text{Cl}^-")
    
    st.markdown("""
    **3. Reaksi Substitusi Aromatik (Trisubstitusi Air Brom)**
    * Cincin aromatik pada fenol sangat reaktif karena efek aktivasi dari gugus $-OH$. Jika direaksikan dengan air brom ($Br_2/H_2O$) yang bersifat polar, akan langsung mengalami trisubstitusi membentuk endapan putih 2,4,6-tribromofenol.
    """)
    
    st.latex(r"\text{C}_6\text{H}_5\text{OH} + 3\text{Br}_2 \text{ (dalam H}_2\text{O)} \rightarrow \text{C}_6\text{H}_2\text{Br}_3\text{OH}\downarrow \text{ (Endapan Putih)} + 3\text{HBr}")

# --- BAB III ---
elif pilihan_halaman == "📗 BAB III. ALDEHID DAN KETON":
    st.title("📗 BAB III. ALDEHID DAN KETON")
    st.write("---")
    
    st.markdown("""
    Aldehida (${R-CHO}$) dan keton (${R-CO-R}'$) adalah senyawa organik isomer fungsional yang sama-sama memiliki gugus fungsi karbonil (${C}={O}$). Perbedaan utamanya terletak pada atom C karbonil aldehida yang mengikat minimal satu atom hidrogen, sedangkan pada keton terikat pada dua gugus alkil/aril.

    #### **A. Sifat Fisika**
    Metanal (formaldehida) merupakan suku paling rendah yang berwujud gas pada suhu kamar dengan bau menyengat. Suku-suku aldehida rendah lainnya berupa cairan dengan bau yang semakin harum (seperti aroma buah-buahan) seiring bertambah panjangnya rantai C. Keton suku rendah (seperti aseton atau propanon) berupa cairan encer, mudah larut dalam air, mudah menguap, dan memiliki aroma yang segar.

    #### **B. Reaksi Adisi Karbonil**
    
    **1. Adisi Natrium Bisulit (${NaHSO}_3$):**
    * Reaksi adisi nukleofilik pada gugus karbonil aldehida atau metil keton menghasilkan senyawa aduk berupa kristal padat berwarna putih yang sukar larut.
    """)
    
    st.latex(r"\text{R-CHO} + \text{NaHSO}_3 \rightarrow \text{R-CH(OH)-SO}_3\text{Na (Kristal Putih)}")
    
    st.markdown("""
    **2. Pembentukan Hemiasetal dan Asetal:**
    * Reaksi reversibel gugus karbonil dengan alkohol dalam suasana asam gas $HCl$.
    """)
    
    st.latex(r"\text{R-CHO (Aldehida)} + \text{R'OH} \xrightarrow{\text{HCl}} \text{R-CH(OH)(OR') (Hemiasetal)}")
    st.latex(r"\text{R-CH(OH)(OR')} + \text{R'OH} \xrightarrow{\text{HCl}} \text{R-CH(OR')}_2\text{ (Asetal)} + \text{H}_2\text{O}")
    
    st.markdown("""
    #### **C. Reaksi Diferensiasi (Uji Daya Reduksi Aldehida)**
    Aldehida bertindak sebagai reduktor kuat karena keberadaan atom hidrogen pada karbon karbonilnya, sedangkan keton tidak memiliki daya pereduksi dan memberikan hasil negatif pada uji-uji berikut:
    
    **1. Uji Tollens (Cermin Perak):**
    * Aldehida mengoksidasi dirinya menjadi asam karboksilat sekaligus mereduksi ion kompleks perak beramoniak $[\text{Ag(NH}_3)_2]^+$ menjadi logam perak mendesak yang menempel di dinding tabung reaksi membentuk cermin perak.
    """)
    
    st.latex(r"\text{R-CHO} + 2[\text{Ag(NH}_3)_2]^+ + 3\text{OH}^- \rightarrow \text{R-COO}^- + 2\text{Ag}\downarrow\text{ (Cermin Perak)} + 4\text{NH}_3 + 2\text{H}_2\text{O}")
    
    st.markdown("""
    **2. Uji Fehling:**
    * Aldehida mereduksi ion ${Cu}^{2+}$ yang berada dalam bentuk kompleks tartrat basa, menghasilkan endapan merah bata kupro oksida (${Cu}_2{O}$).
    """)
    
    st.latex(r"\text{R-CHO} + 2\text{Cu}^{2+} + 5\text{OH}^- \rightarrow \text{R-COO}^- + \text{Cu}_2\text{O}\downarrow\text{ (Endapan Merah Bata)} + 3\text{H}_2\text{O}")
    
    st.markdown("""
    **3. Uji Benedict:**
    * Memiliki prinsip kerja yang serupa dengan Uji Fehling, namun ion ${Cu}^{2+}$ dikomplekskan oleh sitrat. Pereaksi berada dalam kondisi alkalis lemah untuk menghasilkan endapan merah bata ${Cu}_2{O}$ saat direaksikan dengan aldehida.
    """)
    
    st.latex(r"\text{R-CHO} + 2\text{Cu}^{2+}\text{(sitrat)} + 5\text{OH}^- \rightarrow \text{R-COO}^- + \text{Cu}_2\text{O}\downarrow\text{ (Endapan Merah Bata)} + 3\text{H}_2\text{O}")

# --- BAB IV ---
elif pilihan_halaman == "📕 BAB IV. ASAM KARBOKSILAT DAN DERIVATNYA":
    st.title("📕 BAB IV. ASAM KARBOKSILAT DAN DERIVATNYA")
    st.write("---")
    
    st.markdown("""
    Asam karboksilat memiliki gugus fungsi karboksil ($-{COOH}$), senyawa gabungan dari gugus karbonil dan hidroksil. Derivat atau turunan asam karboksilat (seperti ester, halida asam/asil halida, anhidrida asam, dan amida) terbentuk ketika gugus $-{OH}$ pada karboksilat digantikan oleh nukleofil lain.

    #### **A. Sifat Fisika**
    Asam karboksilat rantai pendek ($C_1 - C_4$) memiliki kelarutan yang sangat baik di dalam air karena kemampuan gugus $-{COOH}$ membentuk ikatan hidrogen antarmolekul yang kuat membentuk dimer. Kelarutan senyawa akan semakin menurun seiring dengan bertambah tingginya bobot molekul (rantai alkil nonpolar semakin panjang). Titik didih asam karboksilat relatif tinggi dibandingkan senyawa organik lain dengan berat molekul setara.

    #### **B. Persamaan Reaksi Kimia Asam Karboksilat**
    
    **1. Reaksi dengan Basa Kuat (${NaOH}$):**
    * Menghasilkan garam karboksilat yang larut dan air.
    """)
    
    st.latex(r"\text{R-COOH} + \text{NaOH} \rightarrow \text{R-COONa} + \text{H}_2\text{O}")
    
    st.markdown("""
    **2. Reaksi dengan Basa Lemah (${NaHCO}_3$):**
    * Asam karboksilat tergolong cukup asam untuk mendeprotonasi natrium bikarbonat, menghasilkan garam, air, dan pelepasan gas karbon dioksida secara cepat (effervescence). Reaksi ini membedakan asam karboksilat dengan fenol (fenol tidak bereaksi dengan ${NaHCO}_3$).
    """)
    
    st.latex(r"\text{R-COOH} + \text{NaHCO}_3 \rightarrow \text{R-COONa} + \text{H}_2\text{O} + \text{CO}_2\uparrow \text{ (Gas)}")
    
    st.markdown("""
    Jika gas ${CO}_2$ yang terbentuk dialirkan ke dalam air barit (${Ba(OH)}_2$), akan terbentuk endapan putih barium karbonat (${BaCO}_3$):
    """)
    
    st.latex(r"\text{CO}_2 + \text{Ba(OH)}_2 \rightarrow \text{BaCO}_3\downarrow \text{ (Endapan Putih)} + \text{H}_2\text{O}")
    
    st.markdown("""
    **3. Esterifikasi Fischer:**
    * Reaksi kondensasi antara asam karboksilat dengan alkohol dibantu katalis asam kuat pekat (${H}_2{SO}_4$) menghasilkan senyawa ester yang beraroma wangi khas seperti buah-buahan.
    """)
    
    st.latex(r"\text{R-COOH} + \text{R'-OH} \xrightarrow{\text{H}_2\text{SO}_4, \Delta} \text{R-COOR' (Ester beraroma)} + \text{H}_2\text{O}")
    
    st.markdown("""
    **4. Oksidasi Asam Karboksilat:**
    * Atom C karbonil pada asam karboksilat mengemban bilangan oksidasi +3. Asam karboksilat tertentu yang masih mengikat hidrogen bebas (seperti asam format atau asam oksalat) dapat dioksidasi lebih lanjut oleh oksidator kuat (${KMnO}_4$ dalam ${H}_2{SO}_4$) menuju bilangan oksidasi maksimal +4 berupa gas ${CO}_2$.
    """)
    
    st.latex(r"\text{R-COOH} \xrightarrow{\text{KMnO}_4/\text{H}_2\text{SO}_4} \text{CO}_2\uparrow + \text{H}_2\text{O}")
    
    st.markdown("""
    #### **C. Persamaan Reaksi Identifikasi Derivat Asam Karboksilat (Uji Asam Hidroksamat)**
    Derivat asam karboksilat (contohnya ester) terlebih dahulu dikondensasikan dengan hidroksilamin (${NH}_2{OH}$) menghasilkan senyawa asam hidroksamat. Sifat kimia khas dari asam hidroksamat adalah kemampuannya mengkelat logam besi membentuk senyawa kompleks besi(III) hidroksamat yang menghasilkan warna ungu intens saat ditambahkan larutan ${FeCl}_3$.
    
    *Pembentukan Asam Hidroksamat dari Ester:*
    """)
    
    st.latex(r"\text{R-COOR' (Ester)} + \text{NH}_2\text{OH} \rightarrow \text{R-CONH-OH (Asam Hidroksamat)} + \text{R'-OH}")
    
    st.markdown("""
    *Pembentukan Kompleks Khelat Ungu dengan ${FeCl}_3$:*
    """)
    
    st.latex(r"3\text{R-CONH-OH} + \text{FeCl}_3 \rightarrow \text{Fe(R-CONHO)}_3 \text{ (Kompleks Ungu)} + 3\text{HCl}")
# --- POST TEST ---
elif pilihan_halaman == "🔬 POST TEST":
    st.title("🔀 Smart Flowchart Auto-Analyzer (Step-by-Step)")
    st.write("Sistem ini mensimulasikan penelusuran Identifikasi Kualitatif Golongan Fungsi secara otomatis berderet.")

    if not st.session_state.test_started:
        st.divider()
        senyawa = st.selectbox("Pilih Golongan Senyawa yang Akan Diuji (Sebagai *Blind Sample*):", ["-- Pilih Senyawa --"] + list(flowchart_paths.keys()))
        if st.button("Mulai Identifikasi 🚀", type="primary"):
            if senyawa == "-- Pilih Senyawa --":
                st.warning("⚠️ Harap pilih komponen senyawa terlebih dahulu!")
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
            st.markdown("<h4 style='text-align: center;'>Visual Lab</h4>", unsafe_allow_html=True)
            tube_placeholder = st.empty() 
            status_placeholder = st.empty()
            
            st.write("")
            if st.button("⏹️ Stop & Pilih Reagen/Sampel Ulang", use_container_width=True, type="secondary"):
                st.session_state.test_started = False
                st.session_state.current_step = 0
                st.session_state.log_history = []
                st.session_state.trigger_animation = False
                force_rerun()
            
        with col_log:
            st.markdown("#### 📑 Logbook & Analisis Teoritis")
            log_container = st.container()

        with log_container:
            for log in st.session_state.log_history:
                if "(+)" in log["hasil"]:
                    st.success(f"**Tahap {log['step']}: {log['pereaksi']}** ➔ **{log['hasil']}**")
                    st.latex(log['reaksi'])
                    st.write(f"**Pembahasan:** {log['alasan']}")
                else:
                    st.error(f"**Tahap {log['step']}: {log['pereaksi']}** ➔ **{log['hasil']}**")
                    st.latex(log['reaksi'])
                    st.write(f"**Pembahasan:** {log['alasan']}")

        if st.session_state.trigger_animation and st.session_state.current_step < len(urutan):
            pereaksi = urutan[st.session_state.current_step]
            
            tube_placeholder.markdown(render_tube("30%", "#f1f5f9", "none"), unsafe_allow_html=True)
            status_placeholder.markdown(f"<div style='text-align:center;'><em>Menyiapkan sampel untuk {pereaksi}...</em></div>", unsafe_allow_html=True)
            time.sleep(1.0)
            
            warna_reagen = reagen_colors[pereaksi]
            tube_placeholder.markdown(render_tube("65%", warna_reagen, "none"), unsafe_allow_html=True)
            status_placeholder.markdown(f"<div style='text-align:center;'><em>Mereaksikan {pereaksi}...</em></div>", unsafe_allow_html=True)
            time.sleep(1.5)
            
            res = database_reaksi[senyawa][pereaksi]
            tube_placeholder.markdown(render_tube("65%", res["warna_akhir"], res["efek"]), unsafe_allow_html=True)
            status_placeholder.markdown("<div style='text-align:center; font-weight:bold;'>Mengamati pengendapan & perubahan warna...</div>", unsafe_allow_html=True)
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
                status_placeholder.markdown("<div style='text-align:center; color:#475569;'>Menunggu konfirmasi data...</div>", unsafe_allow_html=True)
                
                with col_visual:
                    if st.button(f"Lanjutkan ke {next_pereaksi} ⏭️", use_container_width=True, type="primary"):
                        st.session_state.trigger_animation = True
                        force_rerun()
                        
            else:
                status_placeholder.markdown("<div style='text-align:center; font-weight:bold; color:#10b981;'>Rangkaian uji selesai!</div>", unsafe_allow_html=True)
                with log_container:
                    st.info(f"🎉 **KESIMPULAN AKHIR:** Sampel ini terbukti sah merupakan golongan **{senyawa.upper()}**.")
                
                with col_visual:
                    if st.button("🔄 Uji Golongan Senyawa Lain", use_container_width=True):
                        st.session_state.test_started = False
                        force_rerun()
