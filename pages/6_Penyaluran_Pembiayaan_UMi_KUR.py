
import streamlit as st
from utils import tampilkan_header, display_umi_kur_chart, get_data
from datetime import datetime

# Konfigurasi Halaman
st.set_page_config(
    layout="wide",
    page_title="Penyaluran Pembiayaan UMi & KUR",
    page_icon="💼"
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
        font-size: 2.5rem;
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

    /* Khusus untuk KUR/UMi */
    .product-badge {
        display: inline-block;
        padding: 0.35rem 0.65rem;
        border-radius: 50rem;
        font-size: 1.8rem;
        font-weight: 700;
    }
    .kur-badge {
        color: #1e40af;
        background-color: #dbeafe;
    }
    .umi-badge {
        color: #166534;
        background-color: #dcfce7;
    }
</style>
""", unsafe_allow_html=True)

# Pesan di Sidebar
with st.sidebar:
    #st.markdown('<div class="sidebar-info">', unsafe_allow_html=True)
    st.info("Anda sedang melihat laman **penyaluran pembiayaan UMi dan KUR**.", icon="💼")
    st.markdown("- KPPN Lhokseumawe")
    st.markdown('</div>', unsafe_allow_html=True)

# Header dengan logo
tampilkan_header()

# --- KONTEN HALAMAN ---

# Header dengan format yang konsisten
st.markdown("<h1 class='main-title'>PENYALURAN PEMBIAYAAN</h1>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; margin-bottom: 0.5rem;">
    <span class="product-badge umi-badge">UMi</span>
    <span class="product-badge kur-badge">KUR</span>
</div>
""", unsafe_allow_html=True)
st.markdown("<h3 class='sub-header'>Lingkup KPPN Lhokseumawe</h3>", unsafe_allow_html=True)

# Periode/tanggal
REPORT_YEAR = 2026
st.markdown(f"<p class='period'>Periode: Januari - Juli {REPORT_YEAR}</p>", unsafe_allow_html=True)


st.markdown('<hr class="divider">', unsafe_allow_html=True)

# Container untuk visualisasi utama
with st.container():
    #st.markdown('<div class="viz-container">', unsafe_allow_html=True)
    display_umi_kur_chart()
    st.markdown('</div>', unsafe_allow_html=True)

# Analisis tambahan
#with st.expander("**SUMBER:**", expanded=False):
    #st.write("""SIKP UMi & KUR 3O Juni 2025""")

# Tombol kembali ke home
st.markdown('<div class="back-button">', unsafe_allow_html=True)
if st.button("⬅ Kembali ke Menu Utama", use_container_width=True, type="primary"):
    st.switch_page("Home.py")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# Catatan kaki
st.caption("""
**Catatan:**
- **Sumber:** SIKP UMi & KUR 31 Juli 2026
- Data yang disajikan adalah per tanggal 31 Juli 2026
- UMi: Ultra Mikro
- KUR: Kredit Usaha Rakyat
""")
