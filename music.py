import streamlit as st
import pandas as pd
from collections import Counter
import re
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np

# Konfigurasi halaman
st.set_page_config(
    page_title="Lirik Analyzer AI",
    page_icon="🎵",
    layout="wide"
)

# Fungsi Sentimen Analysis TANPA TextBlob (Custom)
def analyze_sentiment(word):
    """
    Analisis sentimen sederhana berbasis dictionary
    """
    # Dictionary sentimen positif dan negatif (Bahasa Indonesia + Inggris)
    positive_words = {
        'cinta', 'sayang', 'kasih', 'love', 'happy', 'senang', 'bahagia', 
        'indah', 'cantik', 'beautiful', 'selamanya', 'forever', 'terbaik',
        'hebat', 'great', 'amazing', 'wonderful', 'terima', 'terima kasih',
        'terima kasih', 'mantap', 'keren', 'suka', 'like', 'ingin', 'mau'
    }
    
    negative_words = {
        'sakit', 'hati', 'putus', 'pisah', 'benci', 'hate', 'sedih', 'sad',
        'patah', 'hilang', 'mati', 'dead', 'bohong', 'lie', 'dusta', 'sakit hati',
        'pergi', 'tinggal', 'sendiri', 'alone', 'kesepian', 'luka', 'blood',
        'air mata', 'cry', 'tangis'
    }
    
    word_lower = word.lower().strip()
    
    if word_lower in positive_words:
        return 0.8, "😊 Positif"
    elif word_lower in negative_words:
        return -0.8, "😢 Negatif"
    elif any(neg in word_lower for neg in ['hati', 'sakit', 'luka', 'patah']):
        return -0.6, "😢 Negatif"
    elif any(pos in word_lower for pos in ['cinta', 'sayang', 'love']):
        return 0.7, "😊 Positif"
    else:
        return 0.0, "😐 Netral"

st.title("🎵 **Lirik Analyzer AI**")
st.markdown("---")

# Sidebar
st.sidebar.header("📝 Input Lirik Lagu")
lirik = st.sidebar.text_area(
    "Masukkan lirik lagu:",
    height=200,
    placeholder="Kau bilang cinta itu hanya permainan\nKau bilang cinta itu hanya kebohongan..."
)

if st.sidebar.button("🚀 Analisis Sekarang", type="primary"):
    if lirik.strip():
        # Preprocessing
        lirik_clean = re.sub(r'[^\w\s]', ' ', lirik.lower())
        lirik_clean = re.sub(r'\s+', ' ', lirik_clean).strip()
        kata_list = [k for k in lirik_clean.split() if len(k) > 2]
        
        # Analisis per kata
        data = []
        for i, kata in enumerate(kata_list):
            sentimen_score, emosi = analyze_sentiment(kata)
            subjektivitas = np.random.uniform(0.3, 0.8)  # Simulasi subjektivitas
            
            data.append({
                'No': i+1,
                'Kata': kata.capitalize(),
                'Sentimen': round(sentimen_score, 3),
                'Subjektivitas': round(subjektivitas, 3),
                'Emosi': emosi
            })
        
        df = pd.DataFrame(data)
        
        # Layout
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 **Analisis Per Kata**")
            st.dataframe(df, use_container_width=True, height=400)
            
            # Download CSV
            csv = df.to_csv(index=False)
            st.download_button(
                "📥 Download CSV",
                csv,
                f"lirik_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "text/csv"
            )
            
            # Stats
            st.subheader("📈 **Statistik**")
            col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
            with col_stat1:
                st.metric("Total Kata", len(kata_list))
            with col_stat2:
                rata_sentimen = df['Sentimen'].mean()
                st.metric("Rata Sentimen", f"{rata_sentimen:.3f}")
            with col_stat3:
                st.metric("Positif", len(df[df['Sentimen'] > 0]))
            with col_stat4:
                st.metric("Negatif", len(df[df['Sentimen'] < 0]))
        
        with col2:
            # Histogram
            st.subheader("🎭 **Distribusi Sentimen**")
            fig_hist = px.histogram(
                df, x='Sentimen', nbins=15,
                title="Distribusi Sentimen",
                color='Emosi',
                color_discrete_map={'😊 Positif': '#10B981', '😢 Negatif': '#EF4444', '😐 Netral': '#6B7280'}
            )
            st.plotly_chart(fig_hist, use_container_width=True)
            
            # Pie chart
            st.subheader("🥧 **Komposisi Emosi**")
            emosi_count = df['Emosi'].value_counts()
            fig_pie = px.pie(
                values=emosi_count.values,
                names=emosi_count.index,
                color_discrete_map={'😊 Positif': '#10B981', '😢 Negatif': '#EF4444', '😐 Netral': '#6B7280'}
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            
            # WordCloud
            st.subheader("☁️ **Word Cloud**")
            word_freq = Counter(kata_list)
            wordcloud = WordCloud(
                width=400, height=300,
                background_color='white',
                colormap='viridis',
                max_words=30
            ).generate_from_frequencies(dict(word_freq.most_common(30)))
            
            fig_wc, ax = plt.subplots(figsize=(6, 4))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig_wc)
        
        # Kesimpulan
        st.markdown("---")
        st.subheader("🎯 **KESIMPULAN**")
        
        total_pos = len(df[df['Sentimen'] > 0])
        total_neg = len(df[df['Sentimen'] < 0])
        persen_pos = (total_pos/len(kata_list))*100
        
        col_k1, col_k2 = st.columns(2)
        with col_k1:
            st.error(f"**Sentimen:** {'🟢 POSITIF' if rata_sentimen > 0 else '🔴 NEGATIF'}")
            st.success(f"**Positif:** {persen_pos:.1f}%")
        with col_k2:
            kata_top = ', '.join([w[0].capitalize() for w in word_freq.most_common(3)])
            st.info(f"**Top Words:** {kata_top}")
        
        st.markdown(f"""
        **Tema Lagu:** {'💚 Romantis/Bahagia' if rata_sentimen > 0 else '💔 Sedih/Putus Asa'}
        **Intensitas:** {'🔥 Tinggi' if df['Subjektivitas'].mean() > 0.6 else '😌 Sedang'}
        """)
        
        st.balloons()
    else:
        st.warning("❌ Masukkan lirik lagu dulu!")

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #666;'>🎵 Lirik Analyzer AI | No TextBlob needed!</p>",
    unsafe_allow_html=True
)
