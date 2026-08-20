
import streamlit as st
from utils import tampilkan_header, display_belanja_kl_chart, get_data
from datetime import datetime

# Konfigurasi Halaman
st.set_page_config(
    layout="wide",
    page_title="Realisasi Belanja K/L",
    page_icon="🏛️"
)

# Custom CSS untuk perbaikan tampilan
st.markdown("""
<style>
    /* Gaya untuk header utama */
    .main-title {
        text-align: center;
        color: #2b5876;
        font-size: 2.8rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        background: linear-gradient(to right, #2b5876, #4e4376);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Gaya untuk subheader */
    .sub-header {
        text-align: center;
        color: #4a6fa5;
        font-size: 1.8rem;
        margin-top: 0 !important;
        margin-bottom: 0.5rem;
        font-weight: 500;
    }

    /* Gaya untuk periode */
    .period {
        text-align: center;
        color: #6b7280;
        font-size: 2rem;
        margin-bottom: 1.5rem;
    }

    /* Gaya untuk tombol kembali */
    .back-button {
        display: flex;
        justify-content: center;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }

    /* Garis pemisah */
    .divider {
        margin: 1.5rem 0;
        border: 0;
        height: 1px;
        background-image: linear-gradient(to right, rgba(0,0,0,0), rgba(75, 85, 99, 0.5), rgba(0,0,0,0));
    }

    /* Container untuk visualisasi */
    .viz-container {
        border-radius: 12px;
        padding: 1.5rem;
        background-color: #f8fafc;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        margin-bottom: 2rem;
        border: 1px solid #e5e7eb;
    }
</style>
""", unsafe_allow_html=True)

# Pesan di Sidebar
with st.sidebar:
    st.markdown('<div class="sidebar-info">', unsafe_allow_html=True)
    st.info("Anda sedang melihat laman **realisasi belanja K/L**.", icon="🏛️")
    st.markdown("- KPPN Lhokseumawe")
    st.markdown('</div>', unsafe_allow_html=True)

# Header dengan logo
tampilkan_header()

# --- KONTEN HALAMAN ---

# Header dengan format yang konsisten
st.markdown("<h1 class='main-title'>REALISASI BELANJA KEMENTERIAN/LEMBAGA</h1>", unsafe_allow_html=True)
st.markdown("<h3 class='sub-header'>Lingkup KPPN Lhokseumawe</h3>", unsafe_allow_html=True)

# Periode/tanggal
REPORT_YEAR = 2026
st.markdown(f"<p class='period'>Periode: Januari - Juli {REPORT_YEAR}</p>", unsafe_allow_html=True)


st.markdown('<hr class="divider">', unsafe_allow_html=True)

# Container untuk visualisasi utama
with st.container():
    #st.markdown('<div class="viz-container">', unsafe_allow_html=True)
    display_belanja_kl_chart()
    st.markdown('</div>', unsafe_allow_html=True)

# Analisis tambahan
#with st.expander("**SUMBER:**", expanded=False):
    #st.write("""SINTESA 30 JUNI 2025""")

# Tombol kembali ke home
st.markdown('<div class="back-button">', unsafe_allow_html=True)
if st.button("⬅ Kembali ke Beranda", use_container_width=True, type="primary"):
    st.switch_page("Home.py")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# Catatan kaki
st.caption("""
**Catatan:**
- **Sumber:** SINTESA 31 Juli 2026
- Data yang disajikan adalah per tanggal 31 Juli 2026
""")
