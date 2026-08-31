import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re
from urllib.parse import quote
from urllib.error import URLError
from datetime import datetime
import streamlit as st
import base64
from pathlib import Path

# --- FUNGSI-FUNGSI HELPER ---

def parse_value(value):
    """
    PERBAIKAN: Menggunakan versi yang lebih andal untuk membaca berbagai format angka.
    """
    if isinstance(value, (int, float)):
        return float(value)
    try:
        s = str(value).strip()
        if not s: return 0.0
        if '%' in s:
            s = s.replace(',', '.'); s = re.sub(r'[^\d.-]', '', s)
            return float(s) if s else 0.0
        # Menghapus titik ribuan, lalu mengganti koma desimal
        s = s.replace('.', '').replace(',', '.')
        return float(s) if s else 0.0
    except (ValueError, TypeError):
        return 0.0

def format_otomatis(n, prefix="Rp"):
    """
    PERBAIKAN: Definisi fungsi diperbarui untuk menerima argumen 'prefix'.
    """
    if not isinstance(n, (int, float)):
        return f"{prefix} 0".strip()
    abs_n = abs(n)
    if abs_n >= 1_000_000_000_000:
        val, satuan = n / 1_000_000_000_000, "T"
    elif abs_n >= 1_000_000_000:
        val, satuan = n / 1_000_000_000, "M"
    elif abs_n >= 1_000_000:
        val, satuan = n / 1_000_000, "Jt"
    else:
        # Menambahkan spasi hanya jika prefix ada
        return f"{prefix} {n:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".").strip()

    # Menambahkan spasi hanya jika prefix ada
    formatted_val = f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{prefix} {formatted_val} {satuan}".strip()


# --- FUNGSI MEMUAT DATA ---
@st.cache_data(ttl=1200)
def get_data(sheet_name):
    SHEET_ID = "1MHvPog5TFyIx8lnUVV3mYJP0BZKCTHjkGe1zJ7Js8Ek"
    url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(sheet_name)}'
    try:
        df = pd.read_csv(url, header=0); df.columns = df.columns.str.strip()
        return df.dropna(how='all')
    except Exception as e:
        st.error(f"Gagal memuat sheet '{sheet_name}'. Pastikan nama sheet benar dan file dapat diakses publik.")
        return pd.DataFrame()

def img_to_base64(img_path):
    """Mengubah file gambar menjadi string base64."""
    path = Path(img_path)
    if not path.is_file():
        # Jika file tidak ditemukan, kembalikan None agar tidak error
        st.error(f"File logo tidak ditemukan di: {img_path}")
        return None
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def tampilkan_header(lebar_logo_kiri=550, lebar_intress=155, lebar_djpb=60, margin_atas='4rem', margin_bawah='5rem'):
    """
    Menampilkan header dengan:
    - Semua logo sejajar sempurna di garis bawah yang sama
    - Logo kanan rata kanan
    - Presisi tinggi dalam penempatan
    """
    # CSS untuk presisi layout
    st.markdown(
        f"""
        <style>
            /* Reset padding utama */
            div.block-container {{
                padding-top: {margin_atas};
                padding-bottom: {margin_bawah};
                padding-left: 2rem;
                padding-right: 2rem;
            }}
            
            /* Flex container untuk header */
            [data-testid="stHorizontalBlock"] {{
                align-items: flex-end !important;
            }}
            
            /* Kolom logo kiri */
            [data-testid="column"]:nth-of-type(1) {{
                align-self: flex-end !important;
                padding-bottom: 0 !important;
            }}
            
            /* Reset margin gambar */
            .stImage img {{
                margin-bottom: 0 !important;
                vertical-align: bottom !important;
            }}
            
            /* Container logo kanan */
            .logo-kanan-container {{
                display: flex !important;
                gap: 8px !important;
                align-items: flex-end !important;
            }}
        </style>
        """,
        unsafe_allow_html=True
    )

    # Layout kolom
    col1, col2, col3 = st.columns([2, 5, 2.5])

    with col1:
        # Logo Kemenkeu dengan penyesuaian presisi
        st.markdown(
            f'<div style="display:flex;align-items:flex-end;height:100%;">'
            f'<img src="data:image/png;base64,{img_to_base64("logo/KEMENKEU.png")}" width="{lebar_logo_kiri}" style="vertical-align:bottom;">'
            f'</div>',
            unsafe_allow_html=True
        )

    with col3:
        # Path logo
        intress_path = "logo/INTRESS.png"
        djpb_path = "logo/DJPb.png"

        # Encode gambar ke base64
        intress_b64 = img_to_base64(intress_path)
        djpb_b64 = img_to_base64(djpb_path)

        # Hanya tampilkan jika gambar berhasil di-load
        if intress_b64 and djpb_b64:
            st.markdown(f"""
            <div style="display: flex; justify-content: flex-end; align-items: center; gap: 8px;">
                <img src="data:image/png;base64,{intress_b64}" width="{lebar_intress}">
                <img src="data:image/png;base64,{djpb_b64}" width="{lebar_djpb}">
            </div>
            """, unsafe_allow_html=True)
# --- FUNGSI-FUNGSI VISUALISASI LENGKAP ---

def display_pendapatan_infographic():
    SHEET_NAME = 'KINERJA PENDAPATAN APBN'
    df = get_data(SHEET_NAME)
    if df is None or df.empty: return

    st.markdown("""
    <style>
        .pend-row { display: flex; align-items: center; border-bottom: 1px solid #f0f0f0; padding: 15px 5px; }
        .pend-row:last-child { border-bottom: none; }
        .pend-icon { font-size: 2.5em; width: 60px; text-align: center; }
        .pend-details { flex-grow: 1; padding-left: 15px; }
        .pend-details-sub { padding-left: 85px; }
        .pend-category { font-size: 1.05em; color: #333; font-weight: 600; }
        .pend-amount { font-size: 1.2em; color: #003366; font-weight: 700; }
        .pend-yoy { display: inline-block; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 0.95em; margin-left: 10px; }
        .pend-yoy-positive { background-color: #e6f7ec; color: #008744; }
        .pend-yoy-negative { background-color: #fdecea; color: #d93025; }
    </style>
    """, unsafe_allow_html=True)
    try:
        df['anggaran_num'] = df['anggaran (Rp)'].apply(parse_value)
        df['yoy_num'] = df['% yoy'].apply(parse_value)
        perpajakan = df[df['kategori'] == 'Penerimaan Perpajakan'].iloc[0]
        pajak_dn = df[df['kategori'] == 'Pajak Dalam Negeri'].iloc[0]
        pajak_pi = df[df['kategori'] == 'Pajak Perdagangan Internasional'].iloc[0]
        pnbp = df[df['kategori'] == 'Penerimaan Negara Bukan Pajak'].iloc[0]
        pnbp_lain = df[df['kategori'] == 'PNBP Lainnya'].iloc[0]
        pnbp_blu = df[df['kategori'] == 'Pendapatan BLU'].iloc[0]
        penerimaan_dn = df[df['kategori'] == 'Penerimaan Dalam Negeri'].iloc[0]

        display_data = [
            {'level': 1, 'icon': '💰', 'cat': '1. Penerimaan Perpajakan', 'amount': perpajakan['anggaran_num'], 'yoy': perpajakan['yoy_num']},
            {'level': 2, 'icon': '', 'cat': 'a) Pajak Dalam Negeri', 'amount': pajak_dn['anggaran_num'], 'yoy': pajak_dn['yoy_num']},
            {'level': 2, 'icon': '', 'cat': 'b) Pajak Perdagangan Internasional', 'amount': pajak_pi['anggaran_num'], 'yoy': pajak_pi['yoy_num']},
            {'level': 1, 'icon': '🏦', 'cat': '2. Penerimaan Negara Bukan Pajak', 'amount': pnbp['anggaran_num'], 'yoy': pnbp['yoy_num']},
            {'level': 2, 'icon': '', 'cat': 'a) PNBP Lainnya', 'amount': pnbp_lain['anggaran_num'], 'yoy': pnbp_lain['yoy_num']},
            {'level': 2, 'icon': '', 'cat': 'b) Pendapatan BLU', 'amount': pnbp_blu['anggaran_num'], 'yoy': pnbp_blu['yoy_num']},
            {'level': 1, 'icon': '🧾', 'cat': '3. Penerimaan Dalam Negeri', 'amount': penerimaan_dn['anggaran_num'], 'yoy': penerimaan_dn['yoy_num']},
        ]

        for item in display_data:
            details_class = "pend-details-sub" if item['level'] == 2 else "pend-details"
            #if item['yoy'] > 0: yoy_class, yoy_symbol = "pend-yoy-positive", "▲"
            #elif item['yoy'] < 0: yoy_class, yoy_symbol = "pend-yoy-negative", "▼"
            #else: yoy_class, yoy_symbol = "pend-yoy-zero", "▬"
            st.markdown(f"""
            <div class="pend-row"><div class="pend-icon">{item['icon']}</div><div class="{details_class}">
            <div class="pend-category">{item['cat']}</div><div><span class="pend-amount">{format_otomatis(item['amount'])}</span>
            </div></div></div>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Gagal memproses visualisasi Pendapatan: {e}")

def display_belanja_kl_chart():
    SHEET_NAME = 'REALISASI BELANJA KL'
    df = get_data(SHEET_NAME)
    if df is None or df.empty: return

    st.markdown("""
    <style>
        .bkl-summary-box { background-color: #FFFBEA; border: 1px solid #FFECB3; border-radius: 10px; padding: 15px; text-align: center; width: 250px; height: fit-content; margin: 30px auto 0 auto; }
        .bkl-summary-title { font-size: 1.1em; font-weight: 600; }
        .bkl-summary-percent { font-size: 2.5em; font-weight: 700; color: #003366; margin: 5px 0; }
        .bkl-summary-pagu { font-size: 0.9em; }
        .bkl-item { display: flex; align-items: center; margin-bottom: 25px; }
        .bkl-cat-label { width: 120px; font-weight: 600; text-align: right; padding-right: 15px; }
        .bkl-bars-container { flex-grow: 1; }
        .bkl-bar-wrapper { margin-bottom: 4px; position: relative; }
        .bkl-bar { height: 20px; border-radius: 4px; }
        .bkl-bar-realisasi { background-color: #f7d702; }
        .bkl-bar-pagu { background-color: #77abfc; }
        .bkl-bar-label { position: absolute; left: 8px; top: 50%; transform: translateY(-50%); color: #000000; font-size: 0.8em; font-weight: 600; text-shadow: 1px 1px 2px rgba(0,0,0,0.5); }
        .bkl-stats { width: 180px; text-align: left; padding-left: 15px; font-size: 0.95em; }
        .bkl-yoy-pos { color: #2E7D32; font-weight: 600; }
        .bkl-yoy-neg { color: #C62828; font-weight: 600; }
        .bkl-legend { display: flex; justify-content: center; gap: 20px; margin-top: 20px; font-size: 0.9em; }
        .bkl-legend-item { display: flex; align-items: center; gap: 5px; }
        .bkl-legend-color { width: 15px; height: 15px; border-radius: 3px; }
    </style>
    """, unsafe_allow_html=True)
    try:
        df['pagu_num'] = df['Pagu (Rp)'].apply(parse_value)
        df['realisasi_num'] = df['Realisasi (Rp)'].apply(parse_value)
        df['yoy_num'] = df['%yoy'].apply(parse_value)
        df['persen_realisasi'] = (df['realisasi_num'] / df['pagu_num'].replace(0, np.nan) * 100).fillna(0)
        total_pagu = df['pagu_num'].sum()
        total_realisasi = df['realisasi_num'].sum()
        total_persen_realisasi = (total_realisasi / total_pagu) * 100 if total_pagu > 0 else 0
        max_val = df['pagu_num'].max()

        for _, row in df.sort_values('pagu_num', ascending=False).iterrows():
            width_realisasi = (row['realisasi_num'] / max_val) * 100 if max_val > 0 else 0
            width_pagu = (row['pagu_num'] / max_val) * 100 if max_val > 0 else 0
            if row['yoy_num'] > 0: yoy_class, yoy_symbol = "bkl-yoy-pos", "▲"
            elif row['yoy_num'] < 0: yoy_class, yoy_symbol = "bkl-yoy-neg", "▼"
            else: yoy_class, yoy_symbol = "bkl-yoy-zero", "▬"
            st.markdown(f"""
            <div class="bkl-item">
                <div class="bkl-cat-label">{row['Jenis Belanja']}</div>
                <div class="bkl-bars-container">
                    <div class="bkl-bar-wrapper"><div class="bkl-bar bkl-bar-realisasi" style="width: {width_realisasi}%;"><span class="bkl-bar-label">{format_otomatis(row['realisasi_num'])}</span></div></div>
                    <div class="bkl-bar-wrapper"><div class="bkl-bar bkl-bar-pagu" style="width: {width_pagu}%;"><span class="bkl-bar-label">{format_otomatis(row['pagu_num'])}</span></div></div>
                </div>
                <div class="bkl-stats"><div><b>{row['persen_realisasi']:.2f}%</b></div><div class="{yoy_class}">{yoy_symbol} {row['yoy_num']:.2f}% yoy</div></div>
            </div>""", unsafe_allow_html=True)
        st.markdown("""<div class="bkl-legend"><div class="bkl-legend-item"><div class="bkl-legend-color" style="background-color: #FFC107;"></div> Realisasi</div><div class="bkl-legend-item"><div class="bkl-legend-color" style="background-color: #0D47A1;"></div> Pagu</div></div>""", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="bkl-summary-box">
            <div class="bkl-summary-title">Realisasi Total</div>
            <div class="bkl-summary-percent">{total_persen_realisasi:.2f}%</div>
            <div class="bkl-summary-pagu">dari pagu <b>{format_otomatis(total_pagu)}</b></div>
        </div>""", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Gagal memproses visualisasi Belanja K/L: {e}")

def display_tkd_chart():
    SHEET_NAME = 'CAPAIAN PENYALURAN TKD'
    df = get_data(SHEET_NAME)
    if df is None or df.empty: return

    st.markdown("""
    <div style="background-color: #0D47A1; border-radius: 10px; padding: 20px; margin-bottom: 25px; text-align: center;">
        <div style="color: white; font-size: 26px; font-weight: bold; font-family: 'Arial', sans-serif;">
            CAPAIAN PENYALURAN TRANSFER KE DAERAH
        </div>
        <div style="color: #B0C4DE; font-size: 18px; font-family: 'Arial', sans-serif; margin-top: 5px;">
            BERDASARKAN JENIS DANA
        </div>
    </div>
    """, unsafe_allow_html=True)

    try:
        df['pagu_num'] = df['Pagu (Rp)'].apply(parse_value)
        df['realisasi_num'] = df['Realisasi (Rp)'].apply(parse_value)
        df['persentase'] = (df['realisasi_num'] / df['pagu_num'].replace(0, np.nan) * 100).fillna(0)

        max_val = df['pagu_num'].max()
        if max_val >= 1_000_000_000:
            divisor, unit, yaxis_title = 1_000_000_000, "M", "dalam Miliar Rupiah"
        else:
            divisor, unit, yaxis_title = 1_000_000, "Jt", "dalam Juta Rupiah"
        df['pagu_display'] = df['pagu_num'] / divisor
        df['realisasi_display'] = df['realisasi_num'] / divisor

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.add_trace(go.Bar(
            x=df['Jenis Dana'], y=df['pagu_display'], name='Pagu', marker_color='#0056b3',
            text=df['pagu_display'].apply(lambda x: f"<b>{x:,.2f}</b>"),
            textposition='outside',
            textfont=dict(color='black', size=11, family="Arial")
        ), secondary_y=False)

        fig.add_trace(go.Bar(
            x=df['Jenis Dana'], y=df['realisasi_display'], name='Realisasi', marker_color='#ffc107',
            text=df['realisasi_display'].apply(lambda x: f"<b>{x:,.2f}</b>"),
            textposition='outside',
            textfont=dict(color='black', size=11, family="Arial")
        ), secondary_y=False)

        fig.add_trace(go.Scatter(
            x=df['Jenis Dana'], y=df['persentase'], name='Persentase',
            mode='lines+markers+text',
            line=dict(color='black', width=3),
            marker=dict(color='black', size=8),
            text=df['persentase'].apply(lambda x: f'<b>{x:.2f}%</b>'),
            textposition="top center",
            textfont=dict(color='black', size=12, family="Arial")
        ), secondary_y=True)

        # PERUBAHAN: Mengatur warna sumbu, tick, dan judul menjadi hitam
        fig.update_layout(
            barmode='group',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            uniformtext_minsize=8,
            uniformtext_mode='hide',
            margin=dict(t=50),
            xaxis=dict(
                tickfont=dict(color='black', size=12),
                linecolor='black'
            ),
            yaxis=dict(
                title=yaxis_title,
                title_font=dict(color='black', size=12),
                tickfont=dict(color='black', size=12),
                linecolor='black'
            ),
            yaxis2=dict(
                title='Persentase (%)',
                title_font=dict(color='black', size=12),
                tickfont=dict(color='black', size=12),
                linecolor='black'
            )
        )

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Gagal memproses data untuk visualisasi TKD: {e}")


def display_transfer_daerah_wilayah_chart():
    """
    Menampilkan visualisasi data Transfer ke Daerah per PEMDA
    dengan warna biru-kuning dan ringkasan total.
    """
    SHEET_NAME = 'CAPAIAN PENYALURAN TKD WILAYAH'
    df = get_data(SHEET_NAME)
    if df is None or df.empty:
        st.warning(f"Tidak ada data untuk ditampilkan di sheet '{SHEET_NAME}'.")
        return

    # Menambahkan judul untuk chart
    st.markdown("""
    <div style="background-color: #0D47A1; border-radius: 10px; padding: 20px; margin-bottom: 25px; text-align: center;">
        <div style="color: white; font-size: 26px; font-weight: bold; font-family: 'Arial', sans-serif;">
            CAPAIAN PENYALURAN TRANSFER KE DAERAH
        </div>
        <div style="color: #B0C4DE; font-size: 18px; font-family: 'Arial', sans-serif; margin-top: 5px;">
            BERDASARKAN PEMERINTAH DAERAH
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- CSS Styles ---
    # Warna diubah menjadi biru dan kuning
    st.markdown("""
    <style>
        .tkd-w-summary-box { background-color: #f8f9fa; border-radius: 10px; padding: 20px; text-align: center; margin-top: 20px; border: 1px solid #dee2e6;}
        .tkd-w-summary-title { font-size: 1.1em; color: #000000; margin-bottom: 8px; font-weight: 600; }
        .tkd-w-summary-amount { font-size: 2em; font-weight: 700; color: #ffc107; line-height: 1.2; }
        .tkd-w-summary-pagu { font-size: 1em; color: #6c757d; }
        .tkd-w-summary-footer { border-top: 1px solid #dee2e6; padding-top: 15px; margin-top: 15px; display: flex; align-items: center; justify-content: center; gap: 15px; }
        .tkd-w-summary-percent-label { font-size: 1.2em; color: #000000; font-weight: 600; }
        .tkd-w-summary-percent-val { font-size: 2em; font-weight: 700; color: #0056b3; background-color: #e7f1ff; padding: 5px 12px; border-radius: 8px; }
        .tkd-w-item { display: flex; align-items: center; margin-bottom: 25px; }
        .tkd-w-cat-label { width: 120px; font-weight: 600; text-align: right; padding-right: 15px; }
        .tkd-w-bars-container { flex-grow: 1; }
        .tkd-w-bar-wrapper { margin-bottom: 4px; position: relative; }
        .tkd-w-bar { height: 20px; border-radius: 4px; }
        .tkd-w-bar-realisasi { background-color: #ffc107; } /* Warna kuning untuk realisasi */
        .tkd-w-bar-pagu { background-color: #0056b3; } /* Warna biru untuk pagu */
        .tkd-w-bar-label { position: absolute; left: 8px; top: 50%; transform: translateY(-50%); color: white; font-size: 0.8em; font-weight: 600; text-shadow: 1px 1px 2px rgba(0,0,0,0.5); }
        .tkd-w-stats { width: 120px; text-align: center; padding-left: 15px; font-size: 1.1em; font-weight: bold; }
        .tkd-w-legend { display: flex; justify-content: center; gap: 20px; margin-top: 20px; font-size: 0.9em; }
        .tkd-w-legend-item { display: flex; align-items: center; gap: 5px; }
        .tkd-w-legend-color { width: 15px; height: 15px; border-radius: 3px; }
    </style>
    """, unsafe_allow_html=True)

    try:
        df['pagu_num'] = df['PAGU'].apply(parse_value)
        df['realisasi_num'] = df['REALISASI'].apply(parse_value)
        df['persen_realisasi'] = (df['realisasi_num'] / df['pagu_num'].replace(0, np.nan) * 100).fillna(0)

        total_pagu = df['pagu_num'].sum()
        total_realisasi = df['realisasi_num'].sum()
        total_persen_realisasi = (total_realisasi / total_pagu) * 100 if total_pagu > 0 else 0
        max_val = df['pagu_num'].max()

        for _, row in df.sort_values('pagu_num', ascending=False).iterrows():
            width_realisasi = (row['realisasi_num'] / max_val) * 100 if max_val > 0 else 0
            width_pagu = (row['pagu_num'] / max_val) * 100 if max_val > 0 else 0

            st.markdown(f"""
            <div class="tkd-w-item">
                <div class="tkd-w-cat-label">{row['WILAYAH']}</div>
                <div class="tkd-w-bars-container">
                    <div class="tkd-w-bar-wrapper">
                        <div class="tkd-w-bar tkd-w-bar-realisasi" style="width: {width_realisasi}%;">
                            <span class="tkd-w-bar-label">{format_otomatis(row['realisasi_num'])}</span>
                        </div>
                    </div>
                    <div class="tkd-w-bar-wrapper">
                        <div class="tkd-w-bar tkd-w-bar-pagu" style="width: {width_pagu}%;">
                            <span class="tkd-w-bar-label">{format_otomatis(row['pagu_num'])}</span>
                        </div>
                    </div>
                </div>
                <div class="tkd-w-stats">
                    <div>{row['persen_realisasi']:.2f}%</div>
                </div>
            </div>""", unsafe_allow_html=True)

        # --- Legenda ---
        st.markdown("""
        <div class="tkd-w-legend">
            <div class="tkd-w-legend-item"><div class="tkd-w-legend-color" style="background-color: #ffc107;"></div> Realisasi</div>
            <div class="tkd-w-legend-item"><div class="tkd-w-legend-color" style="background-color: #0056b3;"></div> Pagu</div>
        </div>
        """, unsafe_allow_html=True)

        # --- Kotak Ringkasan Total (dipindahkan ke sini) ---
        summary_html = f"""
        <div class="tkd-w-summary-box">
            <div class="tkd-w-summary-title">Total Dana Transfer ke Daerah (TKD) disalurkan sebesar</div>
            <div class="tkd-w-summary-amount">{format_otomatis(total_realisasi)}</div>
            <div class="tkd-w-summary-pagu">dari total pagu {format_otomatis(total_pagu)}</div>
            <div class="tkd-w-summary-footer">
                <span class="tkd-w-summary-percent-label">Tingkat Realisasi</span>
                <span class="tkd-w-summary-percent-val">{total_persen_realisasi:.2f}%</span>
            </div>
        </div>
        """
        st.markdown(summary_html, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Gagal memproses visualisasi TKD per Wilayah: {e}")

def display_belanja_negara_chart():
    SHEET_NAME = 'REALISASI BELANJA NEGARA'
    df = get_data(SHEET_NAME)
    if df is None or df.empty: return

    try:
        df['pagu_num'] = df['Pagu (Rp)'].apply(parse_value)
        df['realisasi_num'] = df['Realisasi (Rp)'].apply(parse_value)
        df['persentase'] = (df['realisasi_num'] / df['pagu_num'].replace(0, np.nan) * 100).fillna(0)

        max_val = df['pagu_num'].max()
        if max_val >= 1_000_000_000_000:
            divisor, unit, yaxis_title = 1_000_000_000_000, "T", "dalam Triliun Rupiah"
        else:
            divisor, unit, yaxis_title = 1_000_000_000, "M", "dalam Miliar Rupiah"
        df['pagu_display'] = df['pagu_num'] / divisor
        df['realisasi_display'] = df['realisasi_num'] / divisor

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.add_trace(go.Bar(
            x=df['Kategori'], y=df['pagu_display'], name='Pagu', marker_color='#2962FF',
            text=df['pagu_display'].apply(lambda x: f"<b>{x:,.2f}</b>"),
            textposition='outside',
            textfont=dict(color='black', size=11, family="Arial")
        ), secondary_y=False)

        fig.add_trace(go.Bar(
            x=df['Kategori'], y=df['realisasi_display'], name='Realisasi', marker_color='#FFC107',
            text=df['realisasi_display'].apply(lambda x: f"<b>{x:,.2f}</b>"),
            textposition='outside',
            textfont=dict(color='black', size=11, family="Arial")
        ), secondary_y=False)

        fig.add_trace(go.Scatter(
            x=df['Kategori'], y=df['persentase'], name='Persentase',
            mode='lines+markers',
            line=dict(color='black', width=3),
            marker=dict(color='black', size=8)
        ), secondary_y=True)

        for i, row in df.iterrows():
            fig.add_annotation(
                x=row['Kategori'], y=row['persentase'], text=f"<b>{row['persentase']:.2f}%</b>",
                font=dict(color="black", size=12, family="Arial"),
                showarrow=False, yshift=15, yref="y2"
            )

        # PERUBAHAN: Mengatur warna sumbu, tick, dan judul menjadi hitam
        fig.update_layout(
            barmode='group',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(t=50),
            xaxis=dict(
                tickfont=dict(color='black', size=12),
                linecolor='black'
            ),
            yaxis=dict(
                title=yaxis_title,
                title_font=dict(color='black', size=12),
                tickfont=dict(color='black', size=12),
                linecolor='black'
            ),
            yaxis2=dict(
                title='Persentase (%)',
                title_font=dict(color='black', size=12),
                tickfont=dict(color='black', size=12),
                linecolor='black'
            )
        )

        st.plotly_chart(fig, use_container_width=True)

        total_data = df[df['Kategori'] == 'Belanja Negara'].iloc[0]
        summary_text = (f"Belanja Negara yang dikelola ➔ Realisasi <b>{format_otomatis(total_data['realisasi_num'])}</b> dari Pagu <b>{format_otomatis(total_data['pagu_num'])}</b> ({total_data['persentase']:.2f}%)")
        st.markdown(f'<div style="background-color: #E8F5E9; border-radius: 10px; padding: 15px; text-align: center; margin-top: -20px; position: relative; z-index: 1; border: 1px solid #A5D6A7;"><p style="font-size: 1.1em; color: #1B5E20;">{summary_text}</p></div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Gagal memproses data untuk visualisasi Belanja Negara: {e}")


def display_umi_kur_chart():
    SHEET_NAME = "PENYALURAN PEMBIAYAAN UMi & KUR"
    df = get_data(SHEET_NAME)
    if df is None or df.empty:
        st.warning("Data tidak ditemukan.")
        return

    # --- INJEKSI CSS ---
    # Perubahan: Memperbesar font UMi dan mengubah target warna pada KUR
    st.markdown("""
    <style>
        /* Kartu Ringkasan */
        .summary-card { padding: 18px; border-radius: 10px; text-align: center; margin-bottom: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.05); }
        .umi-card { background-color: #E7F5FF; border: 1px solid #B3E5FC; }
        .kur-card { background-color: #FFF8E1; border: 1px solid #FFECB3; }
        .summary-title { font-size: 1.1em; font-weight: 600; color: #333; }
        .summary-amount { font-size: 2em; font-weight: 700; color: #0D47A1; margin: 5px 0; }
        .kur-card .summary-amount { color: #FF6F00; }
        .summary-debitur { font-size: 1em; color: #555; }

        /* Visualisasi UMi */
        /* <-- PERUBAHAN: Ukuran font diperbesar --> */
        .umi-item { display: flex; align-items: center; margin-bottom: 15px; font-size: 1.2em; }
        .umi-label { width: 120px; text-align: right; padding-right: 15px; font-weight: 600; color: #333; }
        .umi-bar-container { flex-grow: 1; margin-right: 8px;  }
        .umi-bar {
            height: 35px; /* Sedikit lebih tinggi */
            border-radius: 5px; color: white; display: flex;
            align-items: center; justify-content: center; font-weight: 700; /* Font lebih tebal */
            text-shadow: 1px 1px 1px rgba(0,0,0,0.4); margin: 0 auto;
            font-size: 0.9em; /* Ukuran font di dalam bar disesuaikan */
            padding: 3px; 
        }
        .umi-bar-0 { background: linear-gradient(45deg, #ffc107, #ffca2c); }
        .umi-bar-1 { background: linear-gradient(45deg, #007bff, #3395ff); }
        .umi-bar-2 { background: linear-gradient(45deg, #28a745, #34ce57); }
        .umi-debitur-details {
            width: 150px; /* Sedikit lebih lebar */
            text-align: left; padding-left: 3px;
            font-weight: 600; color: #333; white-space: nowrap;
        }

        /* Visualisasi KUR */
        .kur-item {
            display: flex;
            align-items: center;
            font-size: 1.25em;
            margin-bottom: 18px;
            padding: 10px;
            border-radius: 8px;
            background-color: #f8f9fa;
        }
        .kur-label { width: 140px; text-align: right; padding-right: 15px; font-weight: 700; color: #343a40; }
        
        /* <-- PERUBAHAN: Target pewarnaan diubah ke .kur-amount --> */
        .kur-amount { font-weight: 700; }
        .kur-amount-0 { color: #007bff; } /* Biru */
        .kur-amount-1 { color: #28a745; } /* Hijau */
        .kur-amount-2 { color: #dc3545; } /* Merah */

        .kur-arrow { font-size: 1.5em; color: #6c757d; margin: 0 15px; }
        .kur-debitur { font-weight: 600; color: #343a40; }
    </style>
    """, unsafe_allow_html=True)

    try:
        # Konversi kolom ke numerik
        df['pembiayaan_num'] = df['Jumlah Pembiayaan (Rp)'].apply(parse_value)
        df['debitur_num'] = df['Jumlah Debitur'].apply(parse_value)

        # Pisahkan data UMi dan KUR
        umi_df = df[df['Jenis Pembiayaan'] == 'UMi'].copy()
        kur_df = df[df['Jenis Pembiayaan'] == 'KUR'].copy()

        # Kalkulasi Total
        total_umi_val = umi_df['pembiayaan_num'].sum()
        total_umi_debitur = umi_df['debitur_num'].sum()
        total_kur_val = kur_df['pembiayaan_num'].sum()
        total_kur_debitur = kur_df['debitur_num'].sum()
        max_umi_val = umi_df['pembiayaan_num'].max() if not umi_df.empty else 0

        # --- TAMPILAN UMi ---
        st.subheader("Penyaluran Pembiayaan UMi")
        st.markdown(f"""
        <div class="summary-card umi-card">
            <div class="summary-title">Total Penyaluran UMi</div>
            <div class="summary-amount">{format_otomatis(total_umi_val)}</div>
            <div class="summary-debitur">untuk <b>{int(total_umi_debitur):,}</b> debitur</div>
        </div>
        """, unsafe_allow_html=True)

        for i, row in umi_df.reset_index().iterrows():
            bar_width = (row['pembiayaan_num'] / max_umi_val) * 60 if max_umi_val > 0 else 0
            st.markdown(f"""
            <div class="umi-item">
                <div class="umi-label">{row['Wilayah']}</div>
                <div class="umi-bar-container">
                    <div class="umi-bar umi-bar-{i % 3}" style="width: {bar_width}%; min-width: 120px;">{format_otomatis(row['pembiayaan_num'])}</div>
                </div>
                <div class="umi-debitur-details">
                    ➔ <b>{int(row['debitur_num']):,}</b> Debitur
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        # --- TAMPILAN KUR ---
        st.subheader("Penyaluran Pembiayaan KUR")
        st.markdown(f"""
        <div class="summary-card kur-card">
            <div class="summary-title">Total Penyaluran KUR</div>
            <div class="summary-amount">{format_otomatis(total_kur_val)}</div>
            <div class="summary-debitur">untuk <b>{int(total_kur_debitur):,}</b> debitur</div>
        </div>
        """, unsafe_allow_html=True)

        for i, row in kur_df.reset_index().iterrows():
            # <-- PERUBAHAN: Class warna dipindahkan dari kur-label ke kur-amount -->
            st.markdown(f"""
            <div class="kur-item">
                <div class="kur-label">{row['Wilayah']}</div>
                <div class="kur-amount kur-amount-{i % 3}">{format_otomatis(row['pembiayaan_num'])}</div>
                <div class="kur-arrow">➔</div>
                <div class="kur-debitur">{int(row['debitur_num']):,} Debitur</div>
            </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Gagal memproses data untuk visualisasi UMi & KUR: {e}")


def display_digitalisasi_chart():
    SHEET_NAME = "CAPAIAN DIGITALISASI PEMBAYARAN"
    df = get_data(SHEET_NAME)
    if df is None or df.empty: return

    st.markdown("""
    <style>
        /* TEMA KEMENKEU/DJPB */
        :root {
            --djpb-blue: #03045e;
            --djpb-blue-light: #03045e;
            --djpb-red: #0077b6;
            --djpb-red-light: #0077b6;
            --djpb-gold: #00b4d8;
            --djpb-gold-light: #00b4d8;
            --djpb-green: #90e0ef;
            --djpb-green-light: #90e0ef;
            --djpb-dark: #184e77;
            --djpb-light: #caf0f8;
        }
        
        .digi-card { 
            background-color: white; 
            border-radius: 12px; 
            padding: 20px; 
            border-left: 6px solid; 
            box-shadow: 0 4px 12px rgba(0,0,0,0.05); 
            border: 1px solid #e9ecef; 
            height: 100%; 
            margin-bottom: 20px; 
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .digi-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 16px rgba(0,0,0,0.1);
        }
        .digi-header { 
            display: flex; 
            align-items: center; 
            margin-bottom: 18px; 
        }
        .digi-icon { 
            font-size: 2.2rem; 
            margin-right: 15px; 
            width: 50px; 
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--djpb-light);
            border-radius: 50%;
            padding: 10px;
        }
        .digi-title { 
            font-size: 1.5rem; 
            font-weight: 800; 
            color: var(--djpb-dark);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .digi-metrics-grid { 
            display: grid; 
            grid-template-columns: 1fr 1fr; 
            gap: 15px; 
        }
        .digi-metric-item { 
            padding: 18px; 
            border-radius: 10px; 
            text-align: center; 
            border: 1px solid #e9ecef;
            transition: all 0.3s ease;
        }
        .digi-metric-item:hover {
            transform: scale(1.02);
        }
        .digi-metric-label { 
            font-size: 1rem; 
            color: #ffffff; 
            margin-bottom: 10px; 
            font-weight: 600;
        }
        .digi-value-container { 
            display: flex; 
            justify-content: center; 
            align-items: baseline; 
            gap: 8px; 
            flex-wrap: wrap; 
        }
        .digi-metric-value { 
            font-size: 1.8rem; 
            font-weight: 800; 
            color: #ffffff; 
            line-height: 1.2; 
        }
        .digi-yoy { 
            font-size: 0.9rem; 
            font-weight: 700; 
            padding: 4px 8px;
            border-radius: 12px;
        }
        .digi-yoy-pos { 
            background-color:#ddf0b2;
            color: #143601;
        }
        .digi-yoy-neg { 
            background-color: #ffe1c8;
            color: #e34234;
        }
        .digi-yoy-zero { 
            background-color: #f2f7f7;
            color: #2b2827;
        }
    </style>
    """, unsafe_allow_html=True)

    def get_yoy_html(yoy_value):
        if yoy_value is None or str(yoy_value).strip().lower() == 'none':
            return ""
        yoy_val = parse_value(yoy_value)
        if yoy_val > 0:
            return f'<div class="digi-yoy digi-yoy-pos">▲ +{abs(yoy_val):.1f}%</div>'
        elif yoy_val < 0:
            return f'<div class="digi-yoy digi-yoy-neg">▼ {abs(yoy_val):.1f}%</div>'
        else:
            return f'<div class="digi-yoy digi-yoy-zero">▬ 0.0%</div>'

    try:
        df['nilai_transaksi_num'] = df['Nilai Transaksi (Rp)'].apply(parse_value)
        df['jumlah_transaksi_num'] = df['Jumlah Transaksi'].apply(parse_value)

        platforms = {
            'digipay': {
                'name': 'DIGIPAY', 
                'color': 'var(--djpb-blue)', 
                'icon': '📱',
                'box_colors': [
                    'var(--djpb-blue)',    # SATKER - Biru
                    'var(--djpb-red-light)',    # VENDOR - Merah
                    'var(--djpb-gold-light)',   # TRANSAKSI - Emas
                    'var(--djpb-green-light)'   # NILAI TRANSAKSI - Hijau
                ]
            },
            'KKP': {
                'name': 'KARTU KREDIT PEMERINTAH', 
                'color': 'var(--djpb-gold)', 
                'icon': '💳',
                'box_colors': [
                    'var(--djpb-gold-light)',  # SATKER PENGGUNA - Emas
                    'var(--djpb-green-light)',    # NILAI TRANSAKSI - Merah
                    'var(--djpb-blue-light)',   # (Jika ada metrik tambahan) - Biru
                    'var(--djpb-green-light)'   # (Jika ada metrik tambahan) - Hijau
                ]
            },
            'CMS': {
                'name': 'CASH MANAGEMENT SYSTEM', 
                'color': 'var(--djpb-green)', 
                'icon': '🖥️',
                'box_colors': [
                    'var(--djpb-red-light)',  # SATKER PENGGUNA - Hijau
                    'var(--djpb-blue-light)',   # NILAI TRANSAKSI - Biru
                    'var(--djpb-red-light)',    # (Jika ada metrik tambahan) - Merah
                    'var(--djpb-gold-light)'    # (Jika ada metrik tambahan) - Emas
                ]
            }
        }

        for platform_key, data in platforms.items():
            platform_df = df[df['Platform'] == platform_key]

            if not platform_df.empty:
                row = platform_df.iloc[0]
                metrik_values = re.findall(r'\d+', str(row['Metrik Utama']))
                yoy_nilai_html = get_yoy_html(row['Pertumbuhan YoY (%)'])

                card_html = f'<div class="digi-card" style="border-left-color: {data["color"]};">'
                card_html += f'<div class="digi-header"><div class="digi-icon">{data["icon"]}</div><div class="digi-title">{data["name"]}</div></div>'
                card_html += '<div class="digi-metrics-grid">'

                if platform_key == 'digipay' and len(metrik_values) >= 2:
                    card_html += f"""
                        <div class="digi-metric-item" style="background-color: {data['box_colors'][0]};">
                            <div class="digi-metric-label">SATKER</div>
                            <div class="digi-metric-value">{metrik_values[0]}</div>
                        </div>
                        <div class="digi-metric-item" style="background-color: {data['box_colors'][1]};">
                            <div class="digi-metric-label">VENDOR</div>
                            <div class="digi-metric-value">{metrik_values[1]}</div>
                        </div>
                        <div class="digi-metric-item" style="background-color: {data['box_colors'][2]};">
                            <div class="digi-metric-label">TRANSAKSI</div>
                            <div class="digi-metric-value">{int(row['jumlah_transaksi_num']):,}</div>
                        </div>
                        <div class="digi-metric-item" style="background-color: {data['box_colors'][3]};">
                            <div class="digi-metric-label">NILAI TRANSAKSI</div>
                            <div class="digi-value-container">
                                <div class="digi-metric-value">{format_otomatis(row['nilai_transaksi_num'])}</div>
                                {yoy_nilai_html}
                            </div>
                        </div>
                    """
                elif len(metrik_values) >= 2: # Untuk KKP dan CMS
                    card_html += f"""
                        <div class="digi-metric-item" style="background-color: {data['box_colors'][0]};">
                            <div class="digi-metric-label">SATKER PENGGUNA</div>
                            <div class="digi-metric-value">{metrik_values[0]} DARI {metrik_values[1]}</div>
                        </div>
                        <div class="digi-metric-item" style="background-color: {data['box_colors'][1]};">
                            <div class="digi-metric-label">NILAI TRANSAKSI</div>
                            <div class="digi-value-container">
                                <div class="digi-metric-value">{format_otomatis(row['nilai_transaksi_num'])}</div>
                                {yoy_nilai_html}
                            </div>
                        </div>
                    """
                card_html += '</div></div>'
                st.markdown(card_html, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"GAGAL MEMPROSES DATA DIGITALISASI: {str(e).upper()}")

def generate_press_release():
    """
    FUNGSI YANG DIPERBARUI:
    Menghasilkan siaran pers detail dengan mengadopsi logika terstruktur
    dari class APBNSheetWisePressRelease.
    """
    press_sections = []
    today = "Rabu, 23 Juli 2025"

    # --- 1. BAGIAN PENDAPATAN ---
    pendapatan_df = get_data('KINERJA PENDAPATAN APBN')
    if not pendapatan_df.empty:
        try:
            pendapatan_df['anggaran_num'] = pendapatan_df['anggaran (Rp)'].apply(parse_value)

            press_sections.append("## 1. KINERJA PENDAPATAN NEGARA\n---\n")
            # --- Main Categories ---
            penerimaan_dalam_negeri = pendapatan_df[pendapatan_df['kategori'] == 'Penerimaan Dalam Negeri'].iloc[0]
            perpajakan = pendapatan_df[pendapatan_df['kategori'] == 'Penerimaan Perpajakan'].iloc[0]
            pnbp = pendapatan_df[pendapatan_df['kategori'] == 'Penerimaan Negara Bukan Pajak'].iloc[0]

            # --- Total Pendapatan ---
            press_sections.append(
                f"**Total Pendapatan Negara** mencapai **{format_otomatis(penerimaan_dalam_negeri['anggaran_num'])}**."
            )

            # --- Perpajakan Detail ---
            press_sections.append("\n### **Penerimaan Perpajakan**")
            press_sections.append(
                f"- Kontribusi total: **{format_otomatis(perpajakan['anggaran_num'])}**"
            )

            pajak_dalam_negeri = pendapatan_df[pendapatan_df['kategori'] == 'Pajak Dalam Negeri'].iloc[0]
            pajak_perdagangan = pendapatan_df[pendapatan_df['kategori'] == 'Pajak Perdagangan Internasional'].iloc[0]

            press_sections.append("  - Rincian:")
            press_sections.append(
                f"    - **Pajak Dalam Negeri**: {format_otomatis(pajak_dalam_negeri['anggaran_num'])}"
            )
            press_sections.append(
                f"    - **Pajak Perdagangan Internasional**: {format_otomatis(pajak_perdagangan['anggaran_num'])}"
            )

            # --- PNBP Detail ---
            press_sections.append("\n### **Penerimaan Negara Bukan Pajak (PNBP)**")
            press_sections.append(
                f"- Kontribusi total: **{format_otomatis(pnbp['anggaran_num'])}**"
            )

            pnbp_lainnya = pendapatan_df[pendapatan_df['kategori'] == 'PNBP Lainnya'].iloc[0]
            pendapatan_blu = pendapatan_df[pendapatan_df['kategori'] == 'Pendapatan BLU'].iloc[0]

            press_sections.append("  - Rincian:")
            press_sections.append(
                f"    - **PNBP Lainnya**: {format_otomatis(pnbp_lainnya['anggaran_num'])}"
            )
            press_sections.append(
                f"    - **Pendapatan BLU**: {format_otomatis(pendapatan_blu['anggaran_num'])}"
            )

            # --- Analysis Commentary ---
            press_sections.append("\n### **Analisis**")
            # Bagian analisis YoY dihapus
            press_sections.append("- Kinerja pendapatan negara yang solid menjadi penopang utama APBN.")


        except Exception as e:
            press_sections.append(f"\n**Gagal memproses data pendapatan**: {str(e)}")


    # --- 2. BAGIAN BELANJA KL---
    belanja_df = get_data('REALISASI BELANJA KL')
    if not belanja_df.empty:
        try:
            # --- Data Processing ---
            belanja_df['pagu_num'] = belanja_df['Pagu (Rp)'].apply(parse_value)
            belanja_df['realisasi_num'] = belanja_df['Realisasi (Rp)'].apply(parse_value)
            belanja_df['persentase'] = (belanja_df['realisasi_num'] / belanja_df['pagu_num'].replace(0, np.nan) * 100).fillna(0)
            belanja_df['yoy_num'] = belanja_df['%yoy'].apply(parse_value)

            press_sections.append("## 2. REALISASI BELANJA K/L\n---\n")

            # --- Total Belanja ---
            total_pagu = belanja_df['pagu_num'].sum()
            total_realisasi = belanja_df['realisasi_num'].sum()
            total_persen = (total_realisasi / total_pagu * 100) if total_pagu > 0 else 0

            press_sections.append(
                f"**Total Belanja K/L** telah mencapai realisasi **{format_otomatis(total_realisasi)}** "
                f"({total_persen:.2f}% dari pagu {format_otomatis(total_pagu)})."
            )

            # --- Detail per Jenis Belanja ---
            press_sections.append("\n### **Rincian Realisasi per Jenis Belanja**")

            for _, row in belanja_df.iterrows():
                trend_icon = "↑" if row['yoy_num'] >= 0 else "↓"
                press_sections.append(
                    f"- **{row['Jenis Belanja']}**:\n"
                    f"  - Realisasi: {format_otomatis(row['realisasi_num'])} ({row['persentase']:.2f}% dari pagu)\n"
                    f"  - YoY: {abs(row['yoy_num']):.2f}% {trend_icon} "
                    f"({'naik' if row['yoy_num'] >= 0 else 'turun'})"
                )

            # --- Analisis Kinerja ---
            press_sections.append("\n### **Analisis Kinerja**")

            # Analisis capaian realisasi
            if total_persen > 75:
                press_sections.append("- Secara keseluruhan, realisasi belanja menunjukkan penyerapan anggaran yang baik.")
            elif total_persen > 50:
                press_sections.append("- Realisasi belanja cukup namun masih perlu optimalisasi.")
            else:
                press_sections.append("- Terdapat tantangan serius dalam penyerapan anggaran.")

            # Highlight performa terbaik dan terburuk
            max_real = belanja_df.loc[belanja_df['persentase'].idxmax()]
            min_real = belanja_df.loc[belanja_df['persentase'].idxmin()]

            press_sections.append(
                f"\n- **Penyerapan Tertinggi**: {max_real['Jenis Belanja']} ({max_real['persentase']:.2f}%)\n"
                f"- **Penyerapan Terendah**: {min_real['Jenis Belanja']} ({min_real['persentase']:.2f}%)"
            )

            # Analisis tren pertumbuhan
            growing = belanja_df[belanja_df['yoy_num'] > 0]
            declining = belanja_df[belanja_df['yoy_num'] < 0]

            if not growing.empty:
                press_sections.append("\n**Jenis Belanja yang Tumbuh**:")
                for _, row in growing.iterrows():
                    press_sections.append(f"- {row['Jenis Belanja']} (+{row['yoy_num']:.2f}%)")

            if not declining.empty:
                press_sections.append("\n**Jenis Belanja yang Menurun**:")
                for _, row in declining.iterrows():
                    press_sections.append(f"- {row['Jenis Belanja']} ({row['yoy_num']:.2f}%)")

        except Exception as e:
            press_sections.append(f"\n**Gagal memproses data belanja**: {str(e)}")

 # --- 3. BAGIAN TRANSFER KE DAERAH ---
    tkd_df = get_data('CAPAIAN PENYALURAN TKD')
    tkd_wilayah_df = get_data('CAPAIAN PENYALURAN TKD WILAYAH')

    if not tkd_df.empty and not tkd_wilayah_df.empty:
        try:
            # --- Data Processing ---
            # Proses data jenis dana
            tkd_df['pagu_num'] = tkd_df['Pagu (Rp)'].apply(parse_value)
            tkd_df['realisasi_num'] = tkd_df['Realisasi (Rp)'].apply(parse_value)
            tkd_df['persentase'] = (tkd_df['realisasi_num'] / tkd_df['pagu_num'].replace(0, np.nan) * 100).fillna(0)

            press_sections.append("## 3. PENYALURAN TRANSFER KE DAERAH (TKD)\n---\n")
            # Proses data wilayah
            tkd_wilayah_df['pagu_num'] = tkd_wilayah_df['PAGU'].apply(parse_value)
            tkd_wilayah_df['realisasi_num'] = tkd_wilayah_df['REALISASI'].apply(parse_value)
            tkd_wilayah_df['persentase'] = (tkd_wilayah_df['realisasi_num'] / tkd_wilayah_df['pagu_num'].replace(0, np.nan) * 100).fillna(0)

            # --- Total TKD ---
            total_pagu = tkd_df['pagu_num'].sum()
            total_realisasi = tkd_df['realisasi_num'].sum()
            total_persen = (total_realisasi / total_pagu * 100) if total_pagu > 0 else 0

            press_sections.append(
                f"**Total Transfer ke Daerah** yang telah disalurkan mencapai "
                f"**{format_otomatis(total_realisasi)}** ({total_persen:.2f}% dari pagu "
                f"{format_otomatis(total_pagu)})."
            )

            # --- Analisis per Jenis Dana ---
            press_sections.append("\n### **Analisis Penyaluran per Jenis Dana**")

            # Urutkan dari realisasi terbesar
            tkd_sorted = tkd_df.sort_values('realisasi_num', ascending=False)

            for _, row in tkd_sorted.iterrows():
                press_sections.append(
                    f"- **{row['Jenis Dana']}**: "
                    f"{format_otomatis(row['realisasi_num'])} "
                    f"({row['persentase']:.2f}% dari pagu)"
                )

            # Highlight 3 jenis dana dengan realisasi tertinggi
            top3 = tkd_sorted.head(3)
            press_sections.append("\n**Top 3 Dana dengan Realisasi Tertinggi**:")
            for i, (_, row) in enumerate(top3.iterrows(), 1):
                press_sections.append(
                    f"{i}. **{row['Jenis Dana']}**: "
                    f"{format_otomatis(row['realisasi_num'])} "
                    f"({row['persentase']:.2f}%)"
                )

            # --- Analisis per Wilayah (Diganti dari tabel menjadi narasi) ---
            press_sections.append("\n### **Distribusi per Wilayah**")

            # Urutkan berdasarkan persentase tertinggi
            tkd_wilayah_sorted = tkd_wilayah_df.sort_values('persentase', ascending=False)

            press_sections.append("\nPenyaluran dana per wilayah adalah sebagai berikut:")
            for _, row in tkd_wilayah_sorted.iterrows():
                press_sections.append(
                    f"- **{row['WILAYAH']}** mencatat realisasi sebesar **{format_otomatis(row['realisasi_num'])}**, "
                    f"atau mencapai **{row['persentase']:.2f}%** dari pagu."
                )

            # Highlight wilayah terbaik dan terburuk
            best_wilayah = tkd_wilayah_sorted.iloc[0]
            worst_wilayah = tkd_wilayah_sorted.iloc[-1]

            press_sections.append("\n**Kinerja Wilayah:**")
            press_sections.append(
                f"- **Wilayah Terbaik**: **{best_wilayah['WILAYAH']}** dengan penyerapan "
                f"**{best_wilayah['persentase']:.2f}%**."
            )
            press_sections.append(
                f"- **Wilayah Terendah**: **{worst_wilayah['WILAYAH']}** dengan penyerapan "
                f"**{worst_wilayah['persentase']:.2f}%**."
            )

            # --- Analisis Kinerja ---
            press_sections.append("\n### **Analisis Kinerja**")

            avg_penyerapan = tkd_df['persentase'].mean()
            if avg_penyerapan > 60:
                press_sections.append("- Rata-rata penyaluran TKD menunjukkan kinerja yang baik.")
            elif avg_penyerapan > 30:
                press_sections.append("- Penyaluran TKD masih perlu ditingkatkan.")
            else:
                press_sections.append("- Terdapat kendala serius dalam penyaluran TKD.")

            if (tkd_wilayah_df['persentase'] < 30).any():
                press_sections.append("- Beberapa wilayah mengalami keterlambatan penyerapan yang signifikan.")

        except Exception as e:
            press_sections.append(f"\n**Gagal memproses data TKD**: {str(e)}")


    # --- 4. BAGIAN BELANJA NEGARA ---
    belanja_n_df = get_data('REALISASI BELANJA NEGARA')
    if not belanja_n_df.empty:
        try:
            # --- Data Processing ---
            belanja_n_df['pagu_num'] = belanja_n_df['Pagu (Rp)'].apply(parse_value)
            belanja_n_df['realisasi_num'] = belanja_n_df['Realisasi (Rp)'].apply(parse_value)
            belanja_n_df['persentase'] = (belanja_n_df['realisasi_num'] / belanja_n_df['pagu_num'].replace(0, np.nan) * 100).fillna(0)

            press_sections.append("## 4. REALISASI BELANJA NEGARA\n---\n")

            # --- Total Belanja Negara ---
            total = belanja_n_df[belanja_n_df['Kategori'] == 'Belanja Negara'].iloc[0]
            press_sections.append(
                f"**Total Belanja Negara** telah mencapai realisasi **{format_otomatis(total['realisasi_num'])}** "
                f"({total['persentase']:.2f}% dari pagu {format_otomatis(total['pagu_num'])})."
            )

            # --- Belanja K/L ---
            kl = belanja_n_df[belanja_n_df['Kategori'] == 'Belanja K/L'].iloc[0]
            press_sections.append("\n### **Belanja Kementerian/Lembaga**")
            press_sections.append(
                f"- Realisasi: **{format_otomatis(kl['realisasi_num'])}** "
                f"({kl['persentase']:.2f}% dari pagu)"
            )

            # --- Transfer ke Daerah ---
            tkd = belanja_n_df[belanja_n_df['Kategori'] == 'Transfer ke Daerah'].iloc[0]
            press_sections.append("\n### **Transfer ke Daerah**")
            press_sections.append(
                f"- Realisasi: **{format_otomatis(tkd['realisasi_num'])}** "
                f"({tkd['persentase']:.2f}% dari pagu)"
            )

            # --- Analisis Komparatif ---
            press_sections.append("\n### **Analisis Komparatif**")

            # Hitung kontribusi masing-masing komponen
            kontrib_kl = (kl['realisasi_num'] / total['realisasi_num']) * 100
            kontrib_tkd = (tkd['realisasi_num'] / total['realisasi_num']) * 100

            press_sections.append(
                f"- Kontribusi Belanja K/L: {kontrib_kl:.2f}% dari total realisasi\n"
                f"- Kontribusi Transfer ke Daerah: {kontrib_tkd:.2f}% dari total realisasi"
            )

            # --- Analisis Kinerja ---
            press_sections.append("\n### **Evaluasi Kinerja**")

            if total['persentase'] > 75:
                press_sections.append("- Secara keseluruhan, penyerapan anggaran menunjukkan kinerja yang baik.")
            elif total['persentase'] > 50:
                press_sections.append("- Capaian realisasi cukup namun masih perlu optimalisasi.")
            else:
                press_sections.append("- Terdapat tantangan serius dalam penyerapan anggaran.")

            if kl['persentase'] < tkd['persentase']:
                press_sections.append("- Penyerapan Transfer ke Daerah lebih baik dibanding Belanja K/L.")
            else:
                press_sections.append("- Belanja K/L menunjukkan penyerapan yang lebih baik.")

            # --- Rekomendasi ---
            press_sections.append("\n### **Rekomendasi**")
            if kl['persentase'] < 50:
                press_sections.append("- Perlu percepatan realisasi belanja di Kementerian/Lembaga.")
            if tkd['persentase'] < 50:
                press_sections.append("- Perlu evaluasi proses penyaluran Transfer ke Daerah.")

        except Exception as e:
            press_sections.append(f"\n**Gagal memproses data belanja negara**: {str(e)}")


    # --- 5. BAGIAN PEMBIAYAAN ---
    pembiayaan_df = get_data('PENYALURAN PEMBIAYAAN UMi & KUR')
    if not pembiayaan_df.empty:
        try:
            # --- Data Processing ---
            pembiayaan_df['pembiayaan_num'] = pembiayaan_df['Jumlah Pembiayaan (Rp)'].apply(parse_value)
            pembiayaan_df['debitur_num'] = pembiayaan_df['Jumlah Debitur'].apply(parse_value)

            press_sections.append("## 5. PENYALURAN PEMBIAYAAN UMi & KUR\n---\n")

            # --- Total Pembiayaan ---
            total_umi = pembiayaan_df[pembiayaan_df['Jenis Pembiayaan'] == 'UMi']['pembiayaan_num'].sum()
            total_kur = pembiayaan_df[pembiayaan_df['Jenis Pembiayaan'] == 'KUR']['pembiayaan_num'].sum()
            total_all = total_umi + total_kur

            total_debitur_umi = pembiayaan_df[pembiayaan_df['Jenis Pembiayaan'] == 'UMi']['debitur_num'].sum()
            total_debitur_kur = pembiayaan_df[pembiayaan_df['Jenis Pembiayaan'] == 'KUR']['debitur_num'].sum()
            total_debitur_all = total_debitur_umi + total_debitur_kur

            press_sections.append(
                f"**Total Pembiayaan UMKM** yang telah disalurkan mencapai **{format_otomatis(total_all)}** "
                f"kepada **{int(total_debitur_all):,} debitur**."
            )

            # --- UMi Detail ---
            press_sections.append("\n### **Pembiayaan Ultra Mikro (UMi)**")
            press_sections.append(
                f"- Total penyaluran: **{format_otomatis(total_umi)}** ({total_umi/total_all*100:.1f}% dari total)\n"
                f"- Jumlah debitur: **{int(total_debitur_umi):,}** ({total_debitur_umi/total_debitur_all*100:.1f}% dari total)"
            )

            # Detail per wilayah UMi
            umi_wilayah = pembiayaan_df[pembiayaan_df['Jenis Pembiayaan'] == 'UMi']
            if not umi_wilayah.empty:
                press_sections.append("\n  **Penyaluran per Wilayah**:")
                for _, row in umi_wilayah.iterrows():
                    avg_per_debitur = row['pembiayaan_num'] / row['debitur_num'] if row['debitur_num'] > 0 else 0
                    press_sections.append(
                        f"  - **{row['Wilayah']}**: {format_otomatis(row['pembiayaan_num'])} "
                        f"(kepada {int(row['debitur_num']):,} debitur, "
                        f"rata-rata {format_otomatis(avg_per_debitur)}/debitur)"
                    )

            # --- KUR Detail ---
            press_sections.append("\n### **Kredit Usaha Rakyat (KUR)**")
            press_sections.append(
                f"- Total penyaluran: **{format_otomatis(total_kur)}** ({total_kur/total_all*100:.1f}% dari total)\n"
                f"- Jumlah debitur: **{int(total_debitur_kur):,}** ({total_debitur_kur/total_debitur_all*100:.1f}% dari total)"
            )

            # Detail per wilayah KUR
            kur_wilayah = pembiayaan_df[pembiayaan_df['Jenis Pembiayaan'] == 'KUR']
            if not kur_wilayah.empty:
                press_sections.append("\n  **Penyaluran per Wilayah**:")
                for _, row in kur_wilayah.iterrows():
                    avg_per_debitur = row['pembiayaan_num'] / row['debitur_num'] if row['debitur_num'] > 0 else 0
                    press_sections.append(
                        f"  - **{row['Wilayah']}**: {format_otomatis(row['pembiayaan_num'])} "
                        f"(kepada {int(row['debitur_num']):,} debitur, "
                        f"rata-rata {format_otomatis(avg_per_debitur)}/debitur)"
                    )

            # --- Analisis Komparatif ---
            press_sections.append("\n### **Analisis Komparatif**")


            # Wilayah dengan penyaluran tertinggi
            max_umi = umi_wilayah.loc[umi_wilayah['pembiayaan_num'].idxmax()] if not umi_wilayah.empty else None
            max_kur = kur_wilayah.loc[kur_wilayah['pembiayaan_num'].idxmax()] if not kur_wilayah.empty else None

            if max_umi is not None:
                press_sections.append(f"\n- **Wilayah penyaluran UMi terbesar**: {max_umi['Wilayah']} ({format_otomatis(max_umi['pembiayaan_num'])})")
            if max_kur is not None:
                press_sections.append(f"- **Wilayah penyaluran KUR terbesar**: {max_kur['Wilayah']} ({format_otomatis(max_kur['pembiayaan_num'])})")

        except Exception as e:
            press_sections.append(f"\n**Gagal memproses data pembiayaan**: {str(e)}")


    # --- 6. BAGIAN KOPDES & MBG ---
    kopdes_df = get_data('KOPDES')
    mbg_df = get_data('MBG')

    if not kopdes_df.empty and not mbg_df.empty:
        try:
            # Proses data KOPDES
            kopdes_df['total_desa'] = kopdes_df['total_desa'].apply(parse_value)
            kopdes_df['terbentuk'] = kopdes_df['terbentuk'].apply(parse_value)
            kopdes_df['persentase'] = (kopdes_df['terbentuk'] / kopdes_df['total_desa'].replace(0, np.nan) * 100).fillna(0)

            # Proses data MBG
            mbg_df['penerima'] = mbg_df['penerima'].apply(parse_value)
            mbg_df['persentase'] = mbg_df['persentase'].apply(parse_value)

            # Hitung total
            total_desa = int(kopdes_df['total_desa'].sum())
            total_terbentuk = int(kopdes_df['terbentuk'].sum())
            total_penerima_mbg = int(mbg_df['penerima'].sum())
            overall_kopdes_percentage = (total_terbentuk / total_desa * 100) if total_desa > 0 else 0

            press_sections.append("## 6. CAPAIAN KOPDES & MBG\n---\n")

            # --- Ringkasan Utama ---
            press_sections.append(
                f"**Pembentukan KOPDES** telah mencapai **{total_terbentuk:,} desa** dari total **{total_desa:,} desa** "
                f"di wilayah kerja (**{overall_kopdes_percentage:.0f}%**). Sementara itu, "
                f"**Program MBG** telah menjangkau **{total_penerima_mbg:,} penerima** manfaat."
            )

            # --- Detail KOPDES ---
            press_sections.append("\n### **Detail Pembentukan KOPDES**")
            for _, row in kopdes_df.sort_values(by='PEMDA').iterrows():
                press_sections.append(
                    f"- **{row['PEMDA']}**: {int(row['terbentuk']):,} desa "
                    f"(**{row['persentase']:.0f}%** dari total {int(row['total_desa']):,} desa)"
                )

            # --- Detail MBG ---
            press_sections.append("\n### **Detail Penerima MBG**")
            for _, row in mbg_df.sort_values(by='PEMDA').iterrows():
                press_sections.append(
                    f"- **{row['PEMDA']}**: {int(row['penerima']):,} penerima "
                    f"(**{row['persentase']:.2f}%** dari target)"
                )

            # --- Analisis Kinerja ---
            press_sections.append("\n### **Analisis Kinerja**")

            # Highlight wilayah dengan pencapaian terbaik
            best_mbg = mbg_df.loc[mbg_df['persentase'].idxmax()]
            press_sections.append(
                f"\n- **Wilayah dengan penyerapan MBG tertinggi**: "
                f"{best_mbg['PEMDA']} ({best_mbg['persentase']:.2f}%)"
            )

        except Exception as e:
            press_sections.append(f"\n**Gagal memproses data KOPDES & MBG**: {str(e)}")

    # --- 7. BAGIAN DIGITALISASI ---
    digital_df = get_data('CAPAIAN DIGITALISASI PEMBAYARAN')
    if not digital_df.empty:
        try:
            # --- Data Processing ---
            digital_df['nilai_num'] = digital_df['Nilai Transaksi (Rp)'].apply(parse_value)
            digital_df['yoy_num'] = digital_df['Pertumbuhan YoY (%)'].apply(parse_value)

            press_sections.append("## 7. CAPAIAN DIGITALISASI PEMBAYARAN\n---\n")
            # --- Total Digitalisasi ---
            total_transaksi = digital_df['Jumlah Transaksi'].sum() if 'Jumlah Transaksi' in digital_df.columns else None
            total_nilai = digital_df['nilai_num'].sum()

            press_sections.append(
                f"**Total Nilai Transaksi Digital** mencapai **{format_otomatis(total_nilai)}**"
            )
            if total_transaksi is not None:
                press_sections[-1] += f" dari **{int(total_transaksi):,} transaksi**."

            # --- Detail per Platform ---
            press_sections.append("\n### **Analisis per Platform Digital**")

            for _, row in digital_df.iterrows():
                platform_info = [
                    f"\n**{row['Platform'].upper()}**:",
                    f"- {row['Metrik Utama']}",
                ]

                if pd.notna(row['Jumlah Transaksi']) and row['Jumlah Transaksi'] != '-':
                    platform_info.append(f"- Jumlah transaksi: {int(row['Jumlah Transaksi']):,}")

                platform_info.append(f"- Nilai transaksi: {format_otomatis(row['nilai_num'])}")

                trend = "↑" if row['yoy_num'] >= 0 else "↓"
                platform_info.append(
                    f"- Pertumbuhan YoY: {abs(row['yoy_num']):.2f}% {trend} "
                    f"({'naik' if row['yoy_num'] >= 0 else 'turun'})"
                )

                press_sections.append("\n".join(platform_info))

            # --- Analisis Kinerja ---
            press_sections.append("\n### **Analisis Kinerja**")

            # Platform dengan nilai transaksi tertinggi
            max_platform = digital_df.loc[digital_df['nilai_num'].idxmax()]
            press_sections.append(
                f"- Platform dominan: **{max_platform['Platform']}** "
                f"(kontribusi {max_platform['nilai_num']/total_nilai*100:.1f}% dari total)."
            )

            # Platform dengan pertumbuhan terbaik
            growing = digital_df[digital_df['yoy_num'] > 0]
            if not growing.empty:
                press_sections.append("\n**Platform dengan Pertumbuhan Positif**:")
                for _, row in growing.iterrows():
                    press_sections.append(f"- {row['Platform']} (+{row['yoy_num']:.2f}%)")

            # Platform dengan penurunan
            declining = digital_df[digital_df['yoy_num'] < 0]
            if not declining.empty:
                press_sections.append("\n**Platform yang Mengalami Penurunan**:")
                for _, row in declining.iterrows():
                    press_sections.append(
                        f"- {row['Platform']} ({row['yoy_num']:.2f}%) "
                        f"{'*perlu evaluasi*' if row['yoy_num'] < -30 else ''}"
                    )

        except Exception as e:
            press_sections.append(f"\n**Gagal memproses data digitalisasi**: {str(e)}")

    # --- GABUNGKAN SEMUA BAGIAN ---
    if press_sections:
        # Note: Markdown does not support text color like yellow.
        # The title is formatted as a large header instead.
        header = ["<font color='grey'>---</font>"]

        final_report = header + press_sections
        return "\n\n".join(final_report)


def display_kopdes_mbg_chart():
    """
    PERUBAHAN TERBARU:
    - Warna angka (bukan nama PEMDA) yang berbeda untuk tiap daerah
    - Format jumlah KOPDES tanpa garis miring (/)
    - Teks diperbesar dan ditebalkan
    - Kolom total MBG dihapus persentasenya
    - Jarak dan alignment diperbaiki
    """
    # --- Memuat Data dari Google Sheets ---
    try:
        kopdes_df = get_data('KOPDES')
        mbg_df = get_data('MBG')

        if kopdes_df is None or kopdes_df.empty or mbg_df is None or mbg_df.empty:
            st.warning("Data untuk KOPDES atau MBG tidak ditemukan/kosong. Visualisasi dilewati.")
            return
    except Exception as e:
        st.error(f"Gagal memuat data awal untuk KOPDES/MBG: {e}")
        return

    # --- Injeksi CSS untuk Styling Final ---
    st.markdown("""
    <style>
        /* Palet Warna */
        :root {
            --djpb-blue-dark: #005FAC;
            --djpb-blue-medium: #1E488F;
            --djpb-blue-light: #EFF5FC;
            --djpb-gold: #FFD700;
            --djpb-gold-light: #FFF9E6;
            --text-dark: #212529;
            --text-light: #FFFFFF;
            --border-color: #DEE2E6;
            
            /* Warna angka untuk tiap daerah */
            --num-lhokseumawe: #4E79A7;
            --num-bireuen: #F28E2B;
            --num-aceh-utara: #E15759;
        }

        /* Container Kartu */
        .summary-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }

        /* Kartu Statistik */
        .summary-card-v5 {
            background-color: var(--djpb-blue-dark);
            color: var(--text-light);
            padding: 25px;
            border-radius: 15px;
            border: 2px solid var(--djpb-gold);
            box-shadow: 0 6px 20px rgba(10, 42, 94, 0.3);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .summary-card-v5:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(10, 42, 94, 0.4);
        }
        .summary-header-v5 {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 8px;
            margin-bottom: 15px;
            text-align: center;
        }
        .summary-title-v5 {
            font-size: 1.3em;
            font-weight: 700;
            letter-spacing: 0.5px;
        }
        .summary-icon-v5 {
            font-size: 1.8em;
            opacity: 0.9;
            margin-bottom: 5px;
        }
        /* Angka besar dengan warna emas */
        .summary-value-v5 {
            font-size: 3.5em;
            font-weight: 900;
            color: var(--djpb-gold);
            line-height: 1;
            margin: 15px 0;
            text-align: center;
        }
        .summary-footer-v5 {
            margin-top: 10px;
            font-size: 1em;
            font-weight: 500;
            opacity: 0.9;
            text-align: center;
        }
        .progress-container-v5 {
            background-color: rgba(255, 255, 255, 0.15);
            border-radius: 10px;
            height: 8px;
            margin-top: 12px;
            overflow: hidden;
        }
        .progress-bar-v5 {
            background-color: var(--djpb-gold);
            height: 100%;
            border-radius: 10px;
        }

        /* Desain Detail Section */
        .data-section-v5 {
            background-color: #FFFFFF;
            border: 1px solid var(--border-color);
            border-radius: 15px;
            padding: 25px;
            margin-top: 25px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }
        .data-title-v5 {
            font-size: 1.7em;
            font-weight: 800;
            color: var(--djpb-blue-dark);
            text-align: center;
            margin-bottom: 25px;
            border-bottom: 3px solid var(--djpb-gold);
            padding-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        /* Grid layout untuk detail data */
        .data-row-v5 {
            display: grid;
            grid-template-columns: 2fr 1.5fr 1fr;
            gap: 15px;
            align-items: center;
            padding: 18px 10px;
            border-bottom: 1px solid var(--djpb-blue-light);
        }
        .data-row-v5:last-of-type { border-bottom: none; }
        .total-row-v5 {
            background-color: var(--djpb-blue-light);
            border-top: 2px solid var(--djpb-blue-medium);
            font-weight: 700;
            color: var(--djpb-blue-dark);
            border-radius: 0 0 10px 10px;
        }
        /* Teks lebih besar dan tebal */
        .pemda-name-v5 { 
            font-weight: 700; 
            font-size: 1.2em;
            letter-spacing: 0.3px;
            color: var(--djpb-blue-medium);
        }
        
        /* Warna angka untuk tiap daerah */
        .num-lhokseumawe { color: var(--num-lhokseumawe); }
        .num-bireuen { color: var(--num-bireuen); }
        .num-aceh-utara { color: var(--num-aceh-utara); }
        
        .data-value-v5 { 
            text-align: right; 
            font-family: "Consolas", "Menlo", monospace; 
            font-size: 1.3em; 
            font-weight: 700;
        }
        .percentage-v5 { 
            text-align: center; 
            font-weight: 800; 
            padding: 8px 12px; 
            border-radius: 20px; 
            color: var(--text-dark); 
            font-size: 1.1em; 
        }
        .p-high { background-color: #A8D5BA; }
        .p-mid { background-color: #FEEFB3; }
        .p-low { background-color: #F5C6CB; }
        .p-100 { background-color: #B4D7F5; color: var(--djpb-blue-dark); }
    </style>
    """, unsafe_allow_html=True)

    try:
        # --- Proses dan Kalkulasi Data ---
        kopdes_df['total_desa'] = kopdes_df['total_desa'].apply(parse_value)
        kopdes_df['terbentuk'] = kopdes_df['terbentuk'].apply(parse_value)
        kopdes_df['persentase'] = (kopdes_df['terbentuk'] / kopdes_df['total_desa'].replace(0, np.nan) * 100).fillna(0)

        mbg_df['penerima'] = mbg_df['penerima'].apply(parse_value)
        mbg_df['persentase'] = mbg_df['persentase'].apply(parse_value)

        total_desa = int(kopdes_df['total_desa'].sum())
        total_terbentuk = int(kopdes_df['terbentuk'].sum())
        total_penerima_mbg = int(mbg_df['penerima'].sum())
        overall_kopdes_percentage = (total_terbentuk / total_desa * 100) if total_desa > 0 else 0

        # --- Tampilan Visualisasi Baru ---
        st.markdown('<div class="summary-container">', unsafe_allow_html=True)
        
        # Kartu Total Desa
        st.markdown(f"""
            <div class="summary-card-v5">
                <div class="summary-header-v5">
                    <span class="summary-title-v5">TOTAL DESA</span>
                </div>
                <div class="summary-value-v5">{total_desa:,}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Kartu KOPDES Terbentuk
        st.markdown(f"""
            <div class="summary-card-v5">
                <div class="summary-header-v5">
                    <span class="summary-title-v5">Desa Yang Telah Mendirikan Kopdes</span>
                </div>
                <div class="summary-value-v5">{total_terbentuk:,}</div>
                <div class="summary-footer-v5">
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Kartu Penerima MBG
        st.markdown(f"""
            <div class="summary-card-v5">
                <div class="summary-header-v5">
                    <span class="summary-icon-v5">👥</span>
                    <span class="summary-title-v5">PENERIMA MBG</span>
                </div>
                <div class="summary-value-v5">{total_penerima_mbg:,}</div>
                <div class="summary-footer-v5">Total Penerima</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

        # Bagian Detail KOPDES
        st.markdown('<div class="data-section-v5"><div class="data-title-v5">Desa Yang Telah Melaksanakan Musdes</div>', unsafe_allow_html=True)
        
        # Class warna angka untuk tiap daerah
        num_classes = {
            "Kota Lhokseumawe": "num-lhokseumawe",
            "Kab. Bireuen": "num-bireuen",
            "Kab. Aceh Utara": "num-aceh-utara"
        }
        
        for _, row in kopdes_df.sort_values(by='PEMDA').iterrows():
            num_class = num_classes.get(row['PEMDA'], '')
            st.markdown(f"""
            <div class="data-row-v5">
                <span class="pemda-name-v5">{row['PEMDA']}</span>
                <span class="data-value-v5 {num_class}">{int(row['terbentuk']):,} <span style="color: var(--text-dark); font-weight: 500;">dari</span> {int(row['total_desa']):,} desa</span>
                <span class="percentage-v5 p-100">{row['persentase']:.0f}%</span>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown(f"""
            <div class="data-row-v5 total-row-v5">
                <span class="pemda-name-v5">TOTAL</span>
                <span class="data-value-v5">{total_terbentuk:,} <span style="color: var(--text-dark); font-weight: 500;">dari</span> {total_desa:,} desa</span>
                <span class="percentage-v5 p-100">{overall_kopdes_percentage:.0f}%</span>
            </div></div>
        """, unsafe_allow_html=True)

        # Bagian Detail MBG
        st.markdown('<div class="data-section-v5"><div class="data-title-v5">PENERIMA MAKANAN BERGIZI GRATIS (MBG)</div>', unsafe_allow_html=True)
        
        for _, row in mbg_df.sort_values(by='PEMDA').iterrows():
            num_class = num_classes.get(row['PEMDA'], '')
            if row['persentase'] >= 7: percentage_class = "p-high"
            elif row['persentase'] >= 5: percentage_class = "p-mid"
            else: percentage_class = "p-low"
            
            st.markdown(f"""
            <div class="data-row-v5">
                <span class="pemda-name-v5">{row['PEMDA']}</span>
                <span class="data-value-v5 {num_class}">{int(row['penerima']):,} Penerima</span>
                <span class="percentage-v5 {percentage_class}">{row['persentase']:.2f}%</span>
            </div>
            """, unsafe_allow_html=True)
            
        # Total tanpa persentase
        st.markdown(f"""
            <div class="data-row-v5 total-row-v5">
                <span class="pemda-name-v5">TOTAL</span>
                <span class="data-value-v5">{total_penerima_mbg:,} Penerima</span>
                <span></span>
            </div></div>
        """, unsafe_allow_html=True)

    except KeyError as e:
        st.error(f"Terjadi kesalahan: Kolom {e} tidak ditemukan di Google Sheet. Mohon periksa kembali nama kolom pada sheet 'KOPDES' atau 'MBG'.")
    except Exception as e:
        st.error(f"Gagal memproses visualisasi KOPDES & MBG: {e}")
