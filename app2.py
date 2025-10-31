import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from pathlib import Path

# ============================================================================
# KONFIGURASI APLIKASI
# ============================================================================
st.set_page_config(
    page_title="Analisis PRINCALS - Kepuasan Akademik",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1e3a8a;
        text-align: center;
        padding: 1.5rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# FUNGSI LOAD DATA
# ============================================================================
@st.cache_data
def load_data():
    """Load semua data dari file Excel"""
    try:
        base_path = Path("C:/Users/NITRO/Documents/pa/results")
        data = pd.read_excel(base_path / "data_dengan_cluster.xlsx")
        cluster_analysis = pd.read_excel(base_path / "analisis_cluster.xlsx")
        detail_cluster = pd.read_excel(base_path / "detail_cluster.xlsx")
        return data, cluster_analysis, detail_cluster
    except FileNotFoundError as e:
        st.error(f"❌ File tidak ditemukan: {e}")
        st.stop()
    except Exception as e:
        st.error(f"❌ Error: {e}")
        st.stop()

# ============================================================================
# FUNGSI VISUALISASI
# ============================================================================
def plot_pca_3d(data):
    fig = px.scatter_3d(
        data, x='PCA_1', y='PCA_2', z='IPK',
        color='CLUSTER', symbol='JKEL', size='PRESENSI',
        hover_name='NAMA',
        title='📊 Distribusi Mahasiswa (PCA 3D)',
        color_continuous_scale='viridis'
    )
    fig.update_layout(height=700)
    return fig

def plot_radar_chart(cluster_analysis):
    categories = ['IPK', 'PRESENSI', 'RATA_TEORI', 'RATA_PRAKTEK', 'NA_NUMERIK']
    fig = go.Figure()
    colors = ['#10b981', '#f59e0b', '#ef4444']
    
    for idx, cluster in enumerate(cluster_analysis.index):
        fig.add_trace(go.Scatterpolar(
            r=cluster_analysis.loc[cluster, categories].values,
            theta=['IPK', 'Presensi', 'Teori', 'Praktik', 'Nilai'],
            fill='toself',
            name=f'Cluster {cluster}',
            line_color=colors[idx % len(colors)]
        ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 4])),
        title="🎯 Karakteristik Cluster",
        height=600
    )
    return fig

def plot_cluster_comparison(cluster_analysis):
    fig = make_subplots(
        rows=2, cols=3,
        subplot_titles=('IPK', 'Presensi', 'Teori', 'Praktik', 'Nilai', 'Jumlah'),
        specs=[[{"type": "bar"}]*3, [{"type": "bar"}]*3]
    )
    
    colors = ['#10b981', '#f59e0b', '#ef4444']
    metrics = [
        ('IPK', 1, 1), ('PRESENSI', 1, 2), ('RATA_TEORI', 1, 3),
        ('RATA_PRAKTEK', 2, 1), ('NA_NUMERIK', 2, 2)
    ]
    
    for metric, row, col in metrics:
        fig.add_trace(
            go.Bar(x=cluster_analysis.index, y=cluster_analysis[metric],
                  marker_color=colors, text=cluster_analysis[metric].round(2),
                  textposition='outside', showlegend=False),
            row=row, col=col
        )
    
    if 'JUMLAH_MAHASISWA' in cluster_analysis.columns:
        fig.add_trace(
            go.Bar(x=cluster_analysis.index, y=cluster_analysis['JUMLAH_MAHASISWA'],
                  marker_color=colors, text=cluster_analysis['JUMLAH_MAHASISWA'],
                  textposition='outside', showlegend=False),
            row=2, col=3
        )
    
    fig.update_layout(height=700, title_text="📊 Perbandingan Cluster")
    return fig

def plot_distribution_grid(data):
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    variables = [
        ('IPK', 'IPK'), ('PRESENSI', 'Presensi'), ('RATA_TEORI', 'Kuisioner Teori'),
        ('RATA_PRAKTEK', 'Kuisioner Praktik'), ('NA_NUMERIK', 'Nilai'), ('CLUSTER', 'Cluster')
    ]
    
    for idx, (var, title) in enumerate(variables):
        row, col = idx // 3, idx % 3
        if var == 'CLUSTER':
            counts = data[var].value_counts().sort_index()
            axes[row, col].bar(counts.index, counts.values, color=['#10b981', '#f59e0b', '#ef4444'])
        else:
            sns.histplot(data=data, x=var, hue='CLUSTER', kde=True, ax=axes[row, col],
                        palette=['#10b981', '#f59e0b', '#ef4444'])
        axes[row, col].set_title(f'Distribusi {title}', fontweight='bold')
        axes[row, col].grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

# ============================================================================
# INTERPRETASI
# ============================================================================
def get_cluster_interpretation(cluster_num):
    interpretations = {
        0: {
            'emoji': '🌟', 'title': 'Mahasiswa Berprestasi Tinggi',
            'desc': 'Kelompok dengan performa akademik excellent',
            'chars': ['IPK tinggi (>3.5)', 'Presensi >95%', 'Kepuasan tinggi'],
            'rec': 'Pertahankan motivasi dan berikan tantangan pengembangan.'
        },
        1: {
            'emoji': '⚖️', 'title': 'Mahasiswa Performa Seimbang',
            'desc': 'Kelompok dengan performa akademik moderat',
            'chars': ['IPK sedang (3.0-3.5)', 'Presensi 85-95%', 'Kepuasan sedang'],
            'rec': 'Berikan pendampingan untuk meningkatkan performa.'
        },
        2: {
            'emoji': '⚠️', 'title': 'Mahasiswa Perlu Perhatian',
            'desc': 'Kelompok yang memerlukan intervensi akademik',
            'chars': ['IPK rendah (<3.0)', 'Presensi <85%', 'Kepuasan rendah'],
            'rec': 'Intervensi intensif dan bimbingan akademik diperlukan.'
        }
    }
    return interpretations.get(cluster_num, interpretations[1])

# ============================================================================
# MAIN APP
# ============================================================================
def main():
    st.markdown('<h1 class="main-title">🎓 Analisis PRINCALS - Kepuasan Akademik</h1>', 
                unsafe_allow_html=True)
    
    # Load data
    with st.spinner("⏳ Memuat data..."):
        data, cluster_analysis, detail_cluster = load_data()
    
    # SIDEBAR
    st.sidebar.title("🔧 Kontrol Panel")
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 Filter Data")
    
    selected_clusters = st.sidebar.multiselect(
        "Cluster", sorted(data['CLUSTER'].unique()), 
        default=sorted(data['CLUSTER'].unique())
    )
    selected_angkatan = st.sidebar.multiselect(
        "Angkatan", sorted(data['ANGKATAN'].unique()),
        default=sorted(data['ANGKATAN'].unique())
    )
    selected_jkel = st.sidebar.multiselect(
        "Jenis Kelamin", sorted(data['JKEL'].unique()),
        default=sorted(data['JKEL'].unique())
    )
    
    # Filter data
    filtered_data = data[
        (data['CLUSTER'].isin(selected_clusters)) &
        (data['ANGKATAN'].isin(selected_angkatan)) &
        (data['JKEL'].isin(selected_jkel))
    ]
    
    st.sidebar.markdown("---")
    st.sidebar.info(f"📊 Data: **{len(filtered_data)}** dari {len(data)} mahasiswa")
    
    # Navigasi
    st.sidebar.markdown("---")
    page = st.sidebar.radio(
        "📋 Navigasi",
        ["📊 Dashboard", "📈 Visualisasi", "👥 Detail Cluster", "🔍 Data Explorer"]
    )
    
    # HALAMAN 1: DASHBOARD
    if page == "📊 Dashboard":
        st.header("📊 Dashboard Ringkasan")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Mahasiswa", len(filtered_data))
        with col2:
            st.metric("Rata-rata IPK", f"{filtered_data['IPK'].mean():.2f}")
        with col3:
            st.metric("Rata-rata Presensi", f"{filtered_data['PRESENSI'].mean():.1%}")
        with col4:
            avg_kuis = filtered_data[['RATA_TEORI', 'RATA_PRAKTEK']].mean().mean()
            st.metric("Rata-rata Kuisioner", f"{avg_kuis:.2f}")
        
        st.markdown("---")
        st.subheader("📈 Ringkasan Cluster")
        st.dataframe(cluster_analysis.style.background_gradient(cmap='RdYlGn', axis=0),
                    use_container_width=True)
        
        st.markdown("---")
        st.subheader("🔍 Interpretasi Cluster")
        
        for cluster_num in cluster_analysis.index:
            interp = get_cluster_interpretation(cluster_num)
            with st.expander(f"{interp['emoji']} Cluster {cluster_num}: {interp['title']}", 
                           expanded=True):
                st.markdown(f"**{interp['desc']}**")
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown("##### Karakteristik:")
                    for char in interp['chars']:
                        st.markdown(f"- {char}")
                with col2:
                    cluster_data = filtered_data[filtered_data['CLUSTER'] == cluster_num]
                    st.metric("Jumlah", len(cluster_data))
                    st.metric("Persentase", f"{len(cluster_data)/len(filtered_data)*100:.1f}%")
                st.info(f"💡 **Rekomendasi:** {interp['rec']}")
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            counts = filtered_data['CLUSTER'].value_counts().sort_index()
            fig = px.pie(values=counts.values, names=[f'Cluster {i}' for i in counts.index],
                        title='Distribusi Cluster', 
                        color_discrete_sequence=['#10b981', '#f59e0b', '#ef4444'])
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = px.box(filtered_data, x='CLUSTER', y='IPK', color='CLUSTER',
                        title='Distribusi IPK per Cluster',
                        color_discrete_sequence=['#10b981', '#f59e0b', '#ef4444'])
            st.plotly_chart(fig, use_container_width=True)
    
    # HALAMAN 2: VISUALISASI
    elif page == "📈 Visualisasi":
        st.header("📈 Visualisasi Lanjutan")
        
        tab1, tab2, tab3, tab4 = st.tabs(["🔮 PCA 3D", "🎯 Radar", "📊 Perbandingan", "📈 Distribusi"])
        
        with tab1:
            st.plotly_chart(plot_pca_3d(filtered_data), use_container_width=True)
        with tab2:
            st.plotly_chart(plot_radar_chart(cluster_analysis), use_container_width=True)
        with tab3:
            st.plotly_chart(plot_cluster_comparison(cluster_analysis), use_container_width=True)
        with tab4:
            st.pyplot(plot_distribution_grid(filtered_data))
    
    # HALAMAN 3: DETAIL CLUSTER
    elif page == "👥 Detail Cluster":
        st.header("👥 Detail Cluster")
        
        options = ["📊 Semua"] + [f"Cluster {i}" for i in sorted(cluster_analysis.index)]
        selected = st.selectbox("Pilih Cluster", options)
        
        if selected == "📊 Semua":
            cols = ['NAMA', 'ANGKATAN', 'JKEL', 'STATUS', 'CLUSTER', 'IPK', 
                   'PRESENSI', 'RATA_TEORI', 'RATA_PRAKTEK']
            cols = [c for c in cols if c in filtered_data.columns]
            st.dataframe(filtered_data[cols].sort_values('CLUSTER'), 
                        use_container_width=True, height=500)
        else:
            cluster_num = int(selected.split()[-1])
            cluster_data = filtered_data[filtered_data['CLUSTER'] == cluster_num]
            interp = get_cluster_interpretation(cluster_num)
            
            st.markdown(f"## {interp['emoji']} {interp['title']}")
            st.markdown(f"*{interp['desc']}*")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Jumlah", len(cluster_data))
            with col2:
                st.metric("IPK", f"{cluster_data['IPK'].mean():.2f}")
            with col3:
                st.metric("Presensi", f"{cluster_data['PRESENSI'].mean():.1%}")
            with col4:
                avg_kuis = cluster_data[['RATA_TEORI', 'RATA_PRAKTEK']].mean().mean()
                st.metric("Kuisioner", f"{avg_kuis:.2f}")
            
            st.markdown("---")
            
            # Detail dari Excel (jika ada)
            if len(detail_cluster[detail_cluster['CLUSTER'] == cluster_num]) > 0:
                st.subheader("📋 Statistik Detail")
                detail_row = detail_cluster[detail_cluster['CLUSTER'] == cluster_num].iloc[0]
                st.dataframe(detail_row.to_frame().T, use_container_width=True)
                st.markdown("---")
            
            # Daftar mahasiswa
            st.subheader("👥 Daftar Mahasiswa dalam Cluster")
            cols = ['NAMA', 'ANGKATAN', 'JKEL', 'IPK', 'PRESENSI', 'RATA_TEORI', 'RATA_PRAKTEK']
            cols = [c for c in cols if c in cluster_data.columns]
            st.dataframe(cluster_data[cols], use_container_width=True, height=400)
    
    # HALAMAN 4: DATA EXPLORER
    elif page == "🔍 Data Explorer":
        st.header("🔍 Eksplorasi Data")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            search = st.text_input("🔎 Cari Nama Mahasiswa", "")
        with col2:
            sort_by = st.selectbox("Urutkan", ['IPK', 'PRESENSI', 'CLUSTER'])
        
        display_data = filtered_data.copy()
        if search:
            display_data = display_data[display_data['NAMA'].str.contains(search, case=False, na=False)]
        
        display_data = display_data.sort_values(sort_by, ascending=False)
        
        st.dataframe(display_data, use_container_width=True, height=500)
        
        # Download
        csv = display_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download CSV",
            csv,
            "data_mahasiswa.csv",
            "text/csv"
        )

if __name__ == "__main__":
    main()