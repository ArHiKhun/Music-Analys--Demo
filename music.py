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
import io

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
        kata_list = [k for k in lirik_clean.split() if len(k) > 2]  # Filter kata pendek
        
        # Buat DataFrame untuk analisis per kata
        data = []
        for i, kata in enumerate(kata_list):
            blob = TextBlob(kata)
            sentimen = blob.sentiment.polarity
            subjektivitas = blob.sentiment.subjectivity
            
            # Klasifikasi emosi sederhana
            if sentimen > 0.1:
                emosi = "😊 Positif"
                warna = "green"
            elif sentimen < -0.1:
                emosi = "😢 Negatif"
                warna = "red"
            else:
                emosi = "😐 Netral"
                warna = "gray"
            
            data.append({
                'No': i+1,
                'Kata': kata.capitalize(),
                'Sentimen': round(sentimen, 3),
                'Subjektivitas': round(subjektivitas, 3),
                'Emosi': emosi,
                'Warna': warna
            })
        
        df = pd.DataFrame(data)
        
        # Layout 2 kolom
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 **Analisis Per Kata**")
            st.dataframe(df, use_container_width=True, height=400)
            
            # Tombol download CSV
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f'lirik_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                mime='text/csv'
            )
            
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
                color='Emosi',
                color_discrete_map={'😊 Positif': 'green', '😢 Negatif': 'red', '😐 Netral': 'gray'}
            )
            fig_sentimen.update_layout(showlegend=False)
            st.plotly_chart(fig_sentimen, use_container_width=True)
            
            # Pie chart emosi
            st.subheader("🥧 **Komposisi Emosi**")
            emosi_count = df['Emosi'].value_counts()
            fig_pie = px.pie(
                values=emosi_count.values,
                names=emosi_count.index,
                title="Persentase Emosi",
                color_discrete_map={'😊 Positif': 'green', '😢 Negatif': 'red', '😐 Netral': 'gray'}
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            
            # WordCloud
            if analisis_frekuensi:
                st.subheader("☁️ **Word Cloud**")
                word_freq = Counter(kata_list)
                wordcloud = WordCloud(
                    width=400, height=300,
                    background_color='white',
                    colormap='viridis',
                    max_words=50
                ).generate_from_frequencies(dict(word_freq.most_common(50)))
                
                fig_wc, ax = plt.subplots(figsize=(8, 6))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                ax.set_title("Kata Paling Sering Muncul", fontsize=14, pad=20)
                st.pyplot(fig_wc)
        
        # Kesimpulan akhir
        st.markdown("---")
        st.subheader("🎯 **KESIMPULAN ANALISIS**")
        
        total_positif = len(df[df['Sentimen'] > 0.1])
        total_negatif = len(df[df['Sentimen'] < -0.1])
        total_netral = len(df[df['Sentimen'].between(-0.1, 0.1)])
        persen_positif = (total_positif/len(kata_list))*100
        
        tema = "kegembiraan/cinta" if rata_sentimen > 0 else "kesedihan/putus asa" if rata_sentimen < 0 else "refleksi/ambivalensi"
        intensitas = "Tinggi" if df['Subjektivitas'].mean() > 0.5 else "Sedang" if df['Subjektivitas'].mean() > 0.3 else "Rendah"
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.error(f"**Sentimen:** {'🟢 POSITIF' if rata_sentimen > 0 else '🔴 NEGATIF' if rata_sentimen < 0 else '🟡 NETRAL'}")
            st.success(f"**Positif:** {persen_positif:.1f}%")
        with col2:
            st.info(f"**Intensitas Emosi:** {intensitas}")
            kata_kunci = ', '.join([word[0].capitalize() for word in word_freq.most_common(5)])
            st.info(f"**Kata Kunci:** {kata_kunci}")
        with col3:
            st.warning(f"**Total Kata:** {len(kata_list)}")
            st.info(f"**Rata Sentimen:** {rata_sentimen:.3f}")
        
        st.markdown("---")
        st.markdown(f"""
        ## 🎼 **Interpretasi Lagu**
        Lagu ini cenderung mengekspresikan **{tema}** dengan komposisi:
        - ✅ **Positif:** {total_positif} kata ({persen_positif:.1f}%)
        - ❌ **Negatif:** {total_negatif} kata ({(total_negatif/len(kata_list))*100:.1f}%)
        - ➖ **Netral:** {total_netral} kata
        
        **Rekomendasi Genre:** {'Pop/Romantis' if rata_sentimen > 0 else 'Rock/Ballad Sedih' if rata_sentimen < 0 else 'Indie/Alternative'}
        """)
        
        st.balloons()
        
    else:
        st.warning("❌ Silakan masukkan lirik lagu terlebih dahulu!")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; padding: 20px;'>"
    "🎵 Dibuat dengan ❤️ untuk pecinta musik | Powered by Streamlit & AI"
    "</div>", 
    unsafe_allow_html=True
)

# Instructions di sidebar
with st.sidebar.expander("📋 Cara Pakai"):
    st.markdown("""
    1. **Copy-paste lirik lagu** di textarea
    2. **Klik "Analisis Sekarang"**
    3. **Lihat hasil** analisis per kata + kesimpulan
    4. **Download CSV** untuk data lengkap
    """)
