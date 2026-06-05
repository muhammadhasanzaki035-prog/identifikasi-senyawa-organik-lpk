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
# 3. FUNGSI HELPER & DATABASE (BERSIH DARI TEKS MENTAH)
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
            "reaksi": "R-OH + [Ce(NO3)6]2- -> [Ce(OR)(NO3)5]2- + HNO3", 
            "alasan": "Gugus -OH bebas bereaksi menggantikan ligan nitrat pada ion Cerium(IV) membentuk senyawa kompleks koordinasi berwarna merah ceri.", 
            "warna_akhir": "#ef4444", "efek": "none"
        },
        "Uji Oksidasi Alkohol": {
            "hasil": "(+) Hijau", 
            "reaksi": "3 R-CH2OH + 2 CrO3 + 3 H2SO4 -> 3 R-CHO + Cr2(SO4)3 + 6 H2O", 
            "alasan": "Memiliki atom hidrogen alfa. Gugus -OH dioksidasi menjadi aldehida/asam karboksilat, sedangkan Kromium(VI) jingga tereduksi menjadi Kromium(III) hijau.", 
            "warna_akhir": "#10b981", "efek": "none"
        },
        "Uji Golongan Alkohol Sekunder": {
            "hasil": "(-) Bening", 
            "reaksi": "R-CH2OH + HCl (katalis ZnCl2) -> Tidak terjadi reaksi / tetap bening", 
            "alasan": "Karbokation primer sangat tidak stabil sehingga tidak mampu bereaksi dengan pereaksi Lucas pada suhu kamar.", 
            "warna_akhir": "#f8fafc", "efek": "none"
        }
    },
    "Alkohol Sekunder": {
        "Uji Golongan Alkohol": {
            "hasil": "(+) Merah Ceri", 
            "reaksi": "R-OH + [Ce(NO3)6]2- -> [Ce(OR)(NO3)5]2- + HNO3", 
            "alasan": "Ikatan koordinasi terbentuk antara atom oksigen pada gugus hidroksil sekunder dengan logam Cerium pusat.", 
            "warna_akhir": "#ef4444", "efek": "none"
        },
        "Uji Oksidasi Alkohol": {
            "hasil": "(+) Hijau", 
            "reaksi": "3 R2CH-OH + 2 CrO3 + 3 H2SO4 -> 3 R2C=O + Cr2(SO4)3 + 6 H2O", 
            "alasan": "Alkohol sekunder dioksidasi menjadi keton, ditandai dengan perubahan warna larutan dari jingga ke hijau.", 
            "warna_akhir": "#10b981", "efek": "none"
        },
        "Uji Golongan Alkohol Sekunder": {
            "hasil": "(+) Emulsi Putih", 
            "reaksi": "R2CH-OH + HCl (katalis ZnCl2) -> R2CH-Cl + H2O", 
            "alasan": "Karbokation sekunder memiliki stabilitas menengah. Bereaksi menghasilkan alkil klorida setelah 5-10 menit dengan bantuan pemanasan.", 
            "warna_akhir": "#e2e8f0", "efek": "cloudy"
        },
        "Uji Golongan Metil Keton / Metil Karbinol": {
            "hasil": "(+) Endapan Kuning", 
            "reaksi": "R-CH(OH)-CH3 + 4 I2 + 6 NaOH -> CHI3 (iodoform) + R-COONa + 5 NaI + 5 H2O", 
            "alasan": "Struktur metil karbinol dioksidasi oleh iodin menjadi metil keton, lalu membentuk kristal iodoform berwarna kuning.", 
            "warna_akhir": "#fef08a", "efek": "precipitate"
        }
    },
    "Alkohol Tersier": {
        "Uji Golongan Alkohol": {
            "hasil": "(+) Merah Ceri", 
            "reaksi": "R-OH + [Ce(NO3)6]2- -> [Ce(OR)(NO3)5]2- + HNO3", 
            "alasan": "Memiliki gugus -OH bebas yang dapat membentuk kompleks koordinasi berwarna merah dengan ceric ammonium nitrate.", 
            "warna_akhir": "#ef4444", "efek": "none"
        },
        "Uji Oksidasi Alkohol": {
            "hasil": "(-) Tetap Jingga", 
            "reaksi": "R3C-OH + CrO3 -> Tidak bereaksi", 
            "alasan": "Alkohol tersier tidak memiliki atom hidrogen alfa sehingga tidak dapat dioksidasi oleh pereaksi Jones.", 
            "warna_akhir": "#f97316", "efek": "none"
        },
        "Uji Golongan Alkohol Tersier": {
            "hasil": "(+) Emulsi Putih (Seketika)", 
            "reaksi": "R3C-OH + HCl (katalis ZnCl2) -> R3C-Cl + H2O", 
            "alasan": "Membentuk karbokation tersier yang sangat stabil, sehingga reaksi substitusi berjalan instan membentuk kabut keruh alkil klorida.", 
            "warna_akhir": "#94a3b8", "efek": "cloudy"
        }
    },
    "Aldehida (Alkanal)": {
        "Uji Golongan Alkohol": {
            "hasil": "(-) Kuning", 
            "reaksi": "R-CHO + [Ce(NO3)6]2- -> Tidak bereaksi", 
            "alasan": "Aldehida tidak memiliki gugus hidroksil (-OH) bebas sehingga warna pereaksi tetap kuning.", 
            "warna_akhir": "#facc15", "efek": "none"
        },
        "Uji Golongan Alkanal/Aldehida (Bisulfit)": {
            "hasil": "(+) Endapan Putih", 
            "reaksi": "R-CHO + NaHSO3 -> R-CH(OH)SO3Na", 
            "alasan": "Nukleofil bisulfit menyerang gugus karbonil aldehida yang reaktif, menghasilkan produk adisi berupa kristal putih.", 
            "warna_akhir": "#ffffff", "efek": "precipitate"
        },
        "Uji Reduksi Golongan Alkanal (Fehling)": {
            "hasil": "(+) Merah Bata", 
            "reaksi": "R-CHO + 2 Cu2+ + 5 OH- -> R-COO- + Cu2O + 3 H2O", 
            "alasan": "Aldehida adalah reduktor kuat yang mereduksi kupri oksida menjadi endapan tembaga(I) oksida berwarna merah bata.", 
            "warna_akhir": "#b91c1c", "efek": "precipitate"
        },
        "Uji Spesifik Golongan Alkanal (Schiff)": {
            "hasil": "(+) Ungu / Magenta", 
            "reaksi": "Aldehida + Reagen Schiff -> Senyawa kompleks berwarna magenta", 
            "alasan": "Reaksi adisi spesifik yang mengembalikan struktur warna p-rosanilin menjadi ungu murni.", 
            "warna_akhir": "#d946ef", "efek": "none"
        }
    },
    "Keton (Alkanon)": {
        "Uji Golongan Alkohol": {
            "hasil": "(-) Kuning", 
            "reaksi": "Keton + [Ce(NO3)6]2- -> Tidak bereaksi", 
            "alasan": "Keton tidak memiliki gugus fungsi hidroksil.", 
            "warna_akhir": "#facc15", "efek": "none"
        },
        "Uji Golongan Alkanal/Aldehida (Bisulfit)": {
            "hasil": "(+) Endapan Putih", 
            "reaksi": "CH3-CO-CH3 + NaHSO3 -> (CH3)2C(OH)SO3Na", 
            "alasan": "Keton suku rendah (seperti aseton) memiliki halangan sterik kecil sehingga masih bisa diadisi oleh bisulfit membentuk endapan putih.", 
            "warna_akhir": "#ffffff", "efek": "precipitate"
        },
        "Uji Reduksi Golongan Alkanal (Fehling)": {
            "hasil": "(-) Tetap Biru", 
            "reaksi": "Keton + Cu2+ -> Tidak bereaksi", 
            "alasan": "Keton tidak memiliki atom hidrogen pada gugus karbonil sehingga tidak bersifat reduktor.", 
            "warna_akhir": "#3b82f6", "efek": "none"
        },
        "Uji Golongan Metil Keton / Metil Karbinol": {
            "hasil": "(+) Endapan Kuning", 
            "reaksi": "R-CO-CH3 + 3 I2 + 4 NaOH -> CHI3 + R-COONa + 3 NaI + 3 H2O", 
            "alasan": "Memiliki gugus metil yang terikat langsung pada karbonil, sehingga bereaksi positif membentuk endapan kuning iodoform.", 
            "warna_akhir": "#fef08a", "efek": "precipitate"
        }
    },
    "Ester (Alkil Alkanoat)": {
        "Uji Golongan Alkohol": {
            "hasil": "(-) Kuning", "reaksi": "Ester + [Ce(NO3)6]2- -> Tidak bereaksi", "alasan": "Tidak memiliki gugus hidroksil bebas.", "warna_akhir": "#facc15", "efek": "none"
        },
        "Uji Golongan Alkanal/Aldehida (Bisulfit)": {
            "hasil": "(-) Bening", "reaksi": "Ester + NaHSO3 -> Tidak bereaksi", "alasan": "Gugus ester stabil akibat efek resonansi elektron sehingga tidak reaktif terhadap nukleofil lemah.", "warna_akhir": "#f8fafc", "efek": "none"
        },
        "Uji Golongan Ester": {
            "hasil": "(+) Merah Violet", 
            "reaksi": "1. R-COOR' + NH2OH -> R-CONHOH + R'OH\n2. 3 R-CONHOH + FeCl3 -> Fe(R-CONHO)3 + 3 HCl", 
            "alasan": "Ester bereaksi dengan hidroksilamin membentuk asam hidroksamat yang mengikat besi(III) menjadi kompleks berwarna violet.", 
            "warna_akhir": "#c026d3", "efek": "none"
        }
    },
    "Asam Karboksilat": {
        "Uji Golongan Alkohol": {
            "hasil": "(-) Kuning", "reaksi": "R-COOH + [Ce(NO3)6]2- -> Tidak bereaksi", "alasan": "Oksigen hidroksil ditarik oleh efek resonansi karbonil sehingga sifat nukleofilnya hilang.", "warna_akhir": "#facc15", "efek": "none"
        },
        "Uji Golongan Alkanal/Aldehida (Bisulfit)": {
            "hasil": "(-) Bening", "reaksi": "R-COOH + NaHSO3 -> Tidak bereaksi", "alasan": "Senyawa ini tidak mengandung gugus fungsi aldehida atau keton.", "warna_akhir": "#f8fafc", "efek": "none"
        },
        "Uji Golongan Ester": {
            "hasil": "(-) Bening", "reaksi": "R-COOH + NH2OH + FeCl3 -> Tidak bereaksi", "alasan": "Asam karboksilat bebas tidak membentuk hidroksamat pada kondisi uji ini.", "warna_akhir": "#f8fafc", "efek": "none"
        },
        "Uji Golongan Asam Karboksilat": {
            "hasil": "(+) Gelembung & Keruh", 
            "reaksi": "1. R-COOH + NaHCO3 -> R-COONa + H2O + CO2\n2. CO2 + Ba(OH)2 -> BaCO3 + H2O", 
            "alasan": "Sifat asamnya mendonasikan proton untuk mengurai bikarbonat menjadi gas CO2. Gas tersebut mengeruhkan air barit karena membentuk barium karbonat.", 
            "warna_akhir": "#f8fafc", "efek": "bubbles"
        }
    },
    "Alkana / Hidrokarbon Jenuh": {
        "Uji Golongan Alkohol": {
            "hasil": "(-) Kuning", "reaksi": "Alkana + [Ce(NO3)6]2- -> Tidak bereaksi", "alasan": "Senyawa nonpolar inert, tidak memiliki gugus hidroksil.", "warna_akhir": "#facc15", "efek": "none"
        },
        "Uji Golongan Alkanal/Aldehida (Bisulfit)": {
            "hasil": "(-) Bening", "reaksi": "Alkana + NaHSO3 -> Tidak bereaksi", "alasan": "Tidak memiliki gugus fungsi karbonil.", "warna_akhir": "#f8fafc", "efek": "none"
        },
        "Uji Golongan Ester": {
            "hasil": "(-) Bening", "reaksi": "Alkana + NH2OH -> Tidak bereaksi", "alasan": "Tidak memiliki gugus fungsi ester.", "warna_akhir": "#f8fafc", "efek": "none"
        },
        "Uji Golongan Asam Karboksilat": {
            "hasil": "(-) Bening", "reaksi": "Alkana + NaHCO3 -> Tidak bereaksi", 
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
# 5. LOGIKA KONTEN TIAP HALAMAN (BERSIH TOTAL DARI BAHASA MESIN)
# ==============================================================================

if pilihan_halaman == "🏠 HALAMAN UTAMA":
    st.markdown("""
        <div class="banner-utama">
            <h1 style='color: white; margin-bottom: 5px; font-weight: 700;'>Selamat Datang di OrganicChem! 👋</h1>
            <p style='font-size: 1.2em; opacity: 0.95;'>Platform Media Pembelajaran Mandiri & Simulasi Identifikasi Gugus Fungsi</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.subheader("💡 Tentang Platform Ini")
    st.write(
        "Platform ini dirancang khusus untuk membantu memahami materi teoritis "
        "sekaligus visualisasi reaksi uji kualitatif senyawa organik di laboratorium secara interaktif."
    )
    st.markdown("---")
    st.markdown("""
    ### **RANGKUMAN MATERI PRAKTIKUM KIMIA ORGANIK**
    Silakan gunakan menu navigasi di sebelah kiri untuk membaca rangkuman materi praktikum Kimia Organik secara sistematis.
    """)

elif pilihan_halaman == "📘 BAB I. HIDROKARBON":
    st.title("📘 BAB I. HIDROKARBON")
    st.write("---")
    
    st.markdown("""
    Hidrokarbon adalah senyawa organik yang seluruh strukturnya hanya tersusun atas unsur karbon (C) dan hidrogen (H). Berdasarkan jenis ikatannya, hidrokarbon alifatik dibagi menjadi hidrokarbon jenuh (alkana) dan tidak jenuh (alkena dan alkuna). Sementara itu, hidrokarbon aromatik memiliki rantai siklik konjugasi yang sangat stabil.

    #### **A. Sifat Fisika Hidrokarbon**
    
    * **Wujud Zat (pada suhu kamar):**
      * Suku rendah (C1 - C4) berwujud gas (contoh: metana, etana, etena, etuna).
      * Suku sedang (C5 - C17) berwujud cair (contoh: pentana, heksana, benzena).
      * Suku tinggi (>= C18) berwujud padat (contoh: parafin padat).
    * **Kelarutan:** Bersifat nonpolar, sehingga tidak larut dalam air (pelarut polar). Hidrokarbon larut dengan baik dalam sesama pelarut organik nonpolar seperti kloroform (CHCl3), karbon tetraklorida (CCl4), atau eter.
    * **Titik Didih dan Titik Leleh:** Meningkat seiring bertambahnya massa molekul (panjang rantai karbon). Untuk isomer dengan jumlah atom karbon sama, senyawa dengan rantai lurus memiliki titik didih lebih tinggi dibandingkan rantai bercabang karena luas permukaan kontak antarmolekul yang lebih besar.
    * **Densitas:** Memiliki massa jenis (densitas) yang lebih kecil daripada air. Jika dicampur dengan air, lapisan hidrokarbon akan selalu berada di bagian atas.

    #### **B. Sifat Kimia & Reaksi Identifikasi Hidrokarbon**

    ##### **1. Alkana (Hidrokarbon Jenuh)**
    Alkana disebut juga parafin (afinitas kecil) karena sangat tidak reaktif terhadap sebagian besar pereaksi seperti asam kuat, basa kuat, dan oksidator pada suhu kamar.
    
    * **Uji Iodo (Substitusi Halogen):** Alkana dapat bereaksi dengan halogen (I2) melalui reaksi substitusi radikal bebas dengan bantuan paparan sinar ultraviolet (UV) atau pemanasan tinggi. Reaksi berjalan lambat dan ditandai dengan memudarnya warna ungu dari iodium.
    """)
    
    st.code("CH4 + I2 --(Sinar UV / Pemanasan)--> CH3I + HI", language="text")
    
    st.markdown("""
    ##### **2. Alkena dan Alkuna (Hidrokarbon Tidak Jenuh)**
    Sangat reaktif karena memiliki ikatan rangkap (C=C atau C#C) yang kaya akan elektron, sehingga mudah mengalami pemutusan ikatan rangkap (adisi).
    
    * **Uji Adisi Iodium:** Mengadisi halogen pada ikatan rangkap tanpa memerlukan bantuan sinar UV. Ditandai dengan warna ungu iodium yang memudar/hilang seketika.
    """)
    
    st.code("R-CH=CH-R + I2 ----> R-CH(I)-CH(I)-R", language="text")
    
    st.markdown("""
    * **Uji Baeyer (Oksidasi dengan KMnO4):** Alkena atau alkuna dioksidasi oleh larutan kalium permanganat encer dalam suasana netral/basa menghasilkan senyawa glikol. Uji positif ditandai dengan hilangnya warna ungu KMnO4 dan terbentuknya endapan cokelat MnO2.
    """)
    
    st.code("3 CH2=CH2 + 2 KMnO4 + 4 H2O ----> 3 HO-CH2-CH2-OH + 2 MnO2 (endapan cokelat) + 2 KOH", language="text")
    
    st.markdown("""
    ##### **3. Benzena (Hidrokarbon Aromatik)**
    Memiliki struktur siklik dengan elektron pi yang terdelokalisasi (resonansi) yang memenuhi aturan Huckel, membuat intinya sangat stabil.
    
    * **Uji Bakar:** Ketika dibakar dengan api langsung pada cawan porselin, benzena menghasilkan nyala api berminyak disertai jelaga hitam yang sangat tebal. Jelaga ini terbentuk akibat tingginya persentase kadar karbon dalam benzena.
    """)
    
    st.code("Benzena + O2 ----> C (Jelaga Hitam) + CO + H2O", language="text")
    
    st.markdown("""
    * **Reaksi Substitusi Elektrofilik:** Benzena sukar mengalami adisi melainkan cenderung mengalami reaksi substitusi. Contohnya adalah reaksi Nitrasi menggunakan campuran asam nitrat pekat dan asam sulfat pekat sebagai katalis.
    """)
    
    st.code("C6H6 + HNO3 --(H2SO4 pekat)--> C6H5NO2 + H2O", language="text")

elif pilihan_halaman == "📙 BAB II. ALKOHOL, ETER, DAN FENOL":
    st.title("📙 BAB II. ALKOHOL, ETER, DAN FENOL")
    st.write("---")
    
    st.markdown("""
    #### **A. Sifat Fisika & Klasifikasi**

    * **Alkohol (R-OH):** Turunan alkana di mana satu atau lebih atom H digantikan oleh gugus hidroksil (-OH). Alkohol diklasifikasikan menjadi alkohol primer (1), sekunder (2), dan tersier (3) berdasarkan jenis atom C yang mengikat gugus -OH. Alkohol suku rendah mudah larut dalam air karena sanggup membentuk ikatan hidrogen dengan molekul air.
    * **Eter (R-O-R'):** Isomer fungsional dari alkohol. Titik didih eter jauh lebih rendah dibandingkan alkohol isomernya karena tidak memiliki ikatan hidrogen antar-sesama molekul eter.
    * **Fenol (C6H5OH):** Senyawa hidrokarbon aromatik yang mengikat gugus fungsi -OH langsung pada cincin benzena. Berupa padatan/hablur pada suhu kamar, sedikit larut dalam air, dan larutannya bersifat asam lemah karena ion fenoksida yang terbentuk distabilkan oleh resonansi.

    #### **B. Persamaan Reaksi Kimia Alkohol & Eter**

    ##### **1. Pereaksi Lucas**
    Menggunakan campuran HCl pekat dan katalis ZnCl2 untuk membedakan jenis alkohol berdasarkan kecepatan reaksinya:
    * Alkohol Tersier: Bereaksi seketika (larutan langsung keruh/terbentuk dua lapisan terpisah).
    * Alkohol Sekunder: Bereaksi dalam waktu 5-10 menit dengan sedikit pemanasan.
    * Alkohol Primer: Tidak bereaksi pada suhu kamar.
    """)
    
    st.code("R3C-OH + HCl --(ZnCl2)--> R3C-Cl (endapan keruh) + H2O", language="text")
    
    st.markdown("""
    ##### **2. Pereaksi Jones (Oksidasi Alkohol)**
    Menggunakan kromium trioksida (CrO3) dalam asam sulfat pekat. Uji positif ditandai dengan perubahan warna pereaksi dari jingga menjadi hijau:
    * Alkohol Primer dioksidasi menjadi Aldehida, lalu berlanjut menjadi Asam Karboksilat.
    * Alkohol Sekunder dioksidasi menjadi Keton.
    * Alkohol Tersier tidak dapat dioksidasi (warna tetap jingga).
    """)
    
    st.code("R-CH2-OH --(CrO3/H2SO4)--> R-COOH (Hijau)\nR2CH-OH --(CrO3/H2SO4)--> R2C=O (Hijau)", language="text")
    
    st.markdown("""
    ##### **3. Uji Iodoform**
    Khusus untuk alkohol yang memiliki gugus metil alfa (CH3-CH(OH)-), seperti etanol atau 2-propanol. Bereaksi dengan I2 dalam suasana basa (NaOH) membentuk endapan kuning kristal iodoform (CHI3).
    """)
    
    st.code("R-CH(OH)-CH3 + 4 I2 + 6 NaOH ----> R-COONa + CHI3 (endapan kuning) + 5 NaI + 5 H2O", language="text")
    
    st.markdown("""
    ##### **4. Pereaksi Ceric Ammonium Nitrate (CAN)**
    Alkohol bereaksi membentuk senyawa kompleks koordinasi berwarna merah cerah, sedangkan eter memberikan hasil negatif (warna tetap kuning).
    """)
    
    st.code("ROH + [Ce(NO3)6]2- ----> [Ce(OR)(NO3)5]2- (Merah Ceri) + HNO3", language="text")
    
    st.markdown("""
    #### **C. Persamaan Reaksi Kimia Fenol**

    ##### **1. Reaksi dengan Basa Kuat (NaOH)**
    Membentuk garam natrium fenoksida yang larut dalam air (menunjukkan sifat asam lemah fenol).
    """)
    
    st.code("C6H5OH + NaOH ----> C6H5ONa + H2O", language="text")
    
    st.markdown("""
    ##### **2. Uji Besi(III) Klorida (FeCl3)**
    Ion fenoksida membentuk senyawa kompleks koordinasi dengan besi(III) yang menghasilkan warna ungu tua/kehitaman yang khas.
    """)
    
    st.code("6 C6H5OH + FeCl3 ----> [Fe(OC6H5)6]3- (Kompleks Ungu) + 3 H+ + 3 Cl-", language="text")

elif pilihan_halaman == "📗 BAB III. ALDEHID DAN KETON":
    st.title("📗 BAB III. ALDEHID DAN KETON")
    st.write("---")
    
    st.markdown("""
    Aldehida (R-CHO) dan keton (R-CO-R') adalah senyawa organik isomer fungsional yang sama-sama memiliki gugus fungsi karbonil (C=O). Perbedaan utamanya terletak pada atom C karbonil aldehida yang mengikat minimal satu atom hidrogen, sedangkan pada keton terikat pada dua gugus alkil.

    #### **A. Sifat Fisika**

    Metanal (formaldehida) merupakan suku paling rendah yang berwujud gas pada suhu kamar dengan bau menyengat. Keton suku rendah (seperti aseton atau propanon) berupa cairan encer, mudah larut dalam air, mudah menguap, dan memiliki aroma yang khas.

    #### **B. Reaksi Adisi Karbonil**

    ##### **1. Adisi Natrium Bisulfit (NaHSO3)**
    Reaksi adisi nukleofilik pada gugus karbonil aldehida atau metil keton menghasilkan senyawa aduk berupa kristal padat berwarna putih yang sukar larut.
    """)
    
    st.code("R-CHO + NaHSO3 ----> R-CH(OH)-SO3Na (Kristal Putih)", language="text")
    
    st.markdown("""
    #### **C. Reaksi Diferensiasi (Uji Daya Reduksi Aldehida)**

    Aldehida bertindak sebagai reduktor kuat karena keberadaan atom hidrogen pada karbon karbonilnya, sedangkan keton tidak memiliki daya pereduksi dan memberikan hasil negatif pada uji-uji berikut:

    ##### **1. Uji Tollens (Cermin Perak)**
    Aldehida mereduksi ion kompleks perak beramoniak menjadi logam perak mengkilap yang menempel di dinding tabung reaksi membentuk cermin perak.
    """)
    
    st.code("R-CHO + 2 [Ag(NH3)2]+ + 3 OH- ----> R-COO- + 2 Ag (Cermin Perak) + 4 NH3 + 2 H2O", language="text")
    
    st.markdown("""
    ##### **2. Uji Fehling**
    Aldehida mereduksi ion Cu2+ yang berada dalam bentuk kompleks tartrat basa, menghasilkan endapan merah bata kupro oksida (Cu2O).
    """)
    
    st.code("R-CHO + 2 Cu2+ + 5 OH- ----> R-COO- + Cu2O (endapan merah bata) + 3 H2O", language="text")

elif pilihan_halaman == "📕 BAB IV. ASAM KARBOKSILAT DAN DERIVATNYA":
    st.title("📕 BAB IV. ASAM KARBOKSILAT DAN DERIVATNYA")
    st.write("---")
    
    st.markdown("""
    Asam karboksilat memiliki gugus fungsi karboksil (-COOH), senyawa gabungan dari gugus karbonil dan hidroksil.

    #### **A. Sifat Fisika**

    Asam karboksilat rantai pendek (C1 - C4) memiliki kelarutan yang sangat baik di dalam air karena kemampuan gugus -COOH membentuk ikatan hidrogen antarmolekul yang kuat untuk membentuk konfigurasi dimer.

    #### **B. Persamaan Reaksi Kimia Asam Karboksilat**

    ##### **1. Reaksi dengan Basa Kuat (NaOH)**
    Menghasilkan garam karboksilat yang larut sempurna dalam air.
    """)
    
    st.code("R-COOH + NaOH ----> R-COONa + H2O", language="text")
    
    st.markdown("""
    ##### **2. Reaksi dengan Basa Lemah (NaHCO3)**
    Asam karboksilat menghasilkan pelepasan gas karbon dioksida secara cepat. Jika gas CO2 yang terbentuk dialirkan ke dalam air barit (Ba(OH)2), akan terbentuk endapan putih barium karbonat (BaCO3):
    """)
    
    st.code("R-COOH + NaHCO3 ----> R-COONa + H2O + CO2 (gas)\nCO2 + Ba(OH)2 ----> BaCO3 (endapan putih) + H2O", language="text")
    
    st.markdown("""
    ##### **3. Esterifikasi Fischer**
    Reaksi kondensasi antara asam karboksilat dengan alkohol dibantu katalis asam sulfat pekat (H2SO4) menghasilkan senyawa ester yang beraroma wangi khas seperti buah-buahan (fruity odor).
    """)
    
    st.code("R-COOH + R'-OH --(H2SO4, Panas)--> R-COOR' (Ester wangi) + H2O", language="text")
    
    st.markdown("""
    #### **C. Uji Identifikasi Derivat Asam Karboksilat (Uji Asam Hidroksamat)**

    Derivat asam karboksilat (contohnya ester) dikondensasikan dengan hidroksilamin (NH2OH) menghasilkan senyawa asam hidroksamat yang mengikat ion Fe3+ sehingga memicu warna ungu/violet intens saat ditambahkan larutan FeCl3.
    """)
    
    st.code("1. R-COOR' + NH2OH ----> R-CONH-OH + R'OH\n2. 3 R-CONH-OH + FeCl3 ----> Fe(R-CONHO)3 (Kompleks Violet) + 3 HCl", language="text")

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
                    st.success(f"**Tahap {log['step']}: {log['pereaksi']}** ➔ **{log['hasil']}**\n\n**Persamaan Reaksi:**\n`{log['reaksi']}`\n\n**Pembahasan Kajian:**\n{log['alasan']}")
                else:
                    st.error(f"**Tahap {log['step']}: {log['pereaksi']}** ➔ **{log['hasil']}**\n\n**Persamaan Reaksi:**\n`{log['reaksi']}`\n\n**Pembahasan Kajian:**\n{log['alasan']}")

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
