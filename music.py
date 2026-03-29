import streamlit as st
import pandas as pd
from collections import Counter
import re
from textblob import TextBlob
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from datetime import datetime

# Konfigurasi halaman
st.set_page_config(
    page_title="Lirik Analyzer AI",
    page_icon="🎵",
    layout="wide"
)

st.title("🎵 **Lirik Analyzer AI**")
st.markdown("---")

# Sidebar untuk input
st.sidebar.header("📝 Input Lirik Lagu")
lirik = st.sidebar.text_area(
    "Masukkan lirik lagu di sini:",
    height=200,
    placeholder="Contoh:\nKau bilang cinta itu hanya permainan\nKau bilang cinta itu hanya kebohongan..."
)

# Opsi analisis
analisis_sentimen = st.sidebar.checkbox("Analisis Sentimen", value=True)
analisis_emosi = st.sidebar.checkbox("Analisis Emosi", value=True)
analisis_frekuensi = st.sidebar.checkbox("Frekuensi Kata", value=True)

if st.sidebar.button("🚀 Analisis Sekarang", type="primary"):
    if lirik.strip():
        # Bersihkan lirik
        lirik_clean = re.sub(r'[^\w\s]', ' ', lirik.lower())
        lirik_clean = re.sub(r'\s+', ' ', lirik_clean).strip()
        kata_list = lirik_clean.split()
        
        # Buat DataFrame untuk analisis per kata
        data = []
        for i, kata in enumerate(kata_list):
            blob = TextBlob(kata)
            sentimen = blob.sentiment.polarity
            subjektivitas = blob.sentiment.subjectivity
            
            # Klasifikasi emosi sederhana
            if sentimen > 0.1:
                emosi = "😊 Positif"
            elif sentimen < -0.1:
                emosi = "😢 Negatif"
            else:
                emosi = "😐 Netral"
            
            data.append({
                'No': i+1,
                'Kata': kata.capitalize(),
                'Sentimen': round(sentimen, 3),
                'Subjektivitas': round(subjektivitas, 3),
                'Emosi': emosi
            })
        
        df = pd.DataFrame(data)
        
        # Layout 2 kolom
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 **Analisis Per Kata**")
            st.dataframe(df, use_container_width=True, height=400)
            
            # Statistik umum
            st.subheader("📈 **Statistik Umum**")
            col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
            
            with col_stat1:
                st.metric("Total Kata", len(kata_list))
            with col_stat2:
                rata_sentimen = df['Sentimen'].mean()
                st.metric("Rata-rata Sentimen", f"{rata_sentimen:.3f}")
            with col_stat3:
                st.metric("Kata Positif", len(df[df['Sentimen'] > 0.1]))
            with col_stat4:
                st.metric("Kata Negatif", len(df[df['Sentimen'] < -0.1]))
        
        with col2:
            st.subheader("🎭 **Distribusi Sentimen**")
            
            # Chart sentimen
            fig_sentimen = px.histogram(
                df, x='Sentimen', nbins=20,
                title="Distribusi Sentimen Kata",
                color='Emosi'
            )
            st.plotly_chart(fig_sentimen, use_container_width=True)
            
            # WordCloud
            if analisis_frekuensi:
                st.subheader("☁️ **Word Cloud**")
                word_freq = Counter(kata_list)
                wordcloud = WordCloud(
                    width=400, height=300,
                    background_color='white',
                    colormap='viridis'
                ).generate_from_frequencies(word_freq)
                
                fig_wc, ax = plt.subplots(figsize=(8, 6))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig_wc)
        
        # Kesimpulan akhir
        st.markdown("---")
        st.subheader("🎯 **KESIMPULAN ANALISIS**")
        
        total_positif = len(df[df['Sentimen'] > 0.1])
        total_negatif = len(df[df['Sentimen'] < -0.1])
        total_netral = len(df[df['Sentimen'].between(-0.1, 0.1)])
        
        kesimpulan = f"""
        **Tema Utama Lagu:**
        - **Sentimen Dominan:** {'🟢 POSITIF' if rata_sentimen > 0 else '🔴 NEGATIF' if rata_sentimen < 0 else '🟡 NETRAL'}
        - **Komposisi:** {total_positif} Positif | {total_negatif} Negatif | {total_netral} Netral
        
        **Analisis Detail:**
        - **Intensitas Emosi:** {'Tinggi' if df['Subjektivitas'].mean() > 0.5 else 'Sedang'}
        - **Kata Kunci:** {', '.join(word_freq.most_common(5))}
        - **Rata-rata Sentimen:** {rata_sentimen:.3f}
        
        **Interpretasi:**
        Lagu ini cenderung mengekspresikan **{('kegembiraan/cinta' if rata_sentimen > 0 else 'kesedihan/putus asa' if rata_sentimen < 0 else 'refleksi/ambivalensi')}**
        dengan **{total_positif/len(kata_list)*100:.1f}%** elemen positif.
        """
        
        st.markdown(kesimpulan)
        st.balloons()
        
    else:
        st.warning("❌ Silakan masukkan lirik lagu terlebih dahulu!")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    🎵 Dibuat dengan ❤️ untuk pecinta musik | Powered by Streamlit & AI
</div>
""")

# Install requirements
st.sidebar.markdown("""
### 📦 Install Dependencies
```bash
pip install streamlit pandas textblob plotly wordcloud matplotlib
