import streamlit as st
import pandas as pd
import re

# Konfigurasi halaman
st.set_page_config(page_title="Lyric Emotion Analyzer", page_icon="🎵", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
    }
    .stButton>button {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 5px;
        font-weight: bold;
        font-size: 16px;
    }
    .info-box {
        background: rgba(255,255,255,0.9);
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 5px solid #667eea;
    }
    .warning-box {
        background: #FFF3CD;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 5px solid #FFC107;
    }
    .lyric-box {
        background: rgba(255,255,255,0.95);
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        white-space: pre-line;
        font-family: 'Courier New', monospace;
        font-size: 14px;
        line-height: 1.8;
        border-left: 5px solid #667eea;
    }
    </style>
    """, unsafe_allow_html=True)

# Judul
st.title("🎵 Lyric Emotion Analyzer")
st.markdown("### Analisis Emosi dari Lirik Lagu Pop Indonesia")
st.markdown("---")

# ⚠️ DISCLAIMER TEKNIS
st.markdown("""
<div class="warning-box">
<b>⚠️ CATATAN TEKNIS:</b><br>
File audio (MP3/WAV) tidak menyimpan lirik dalam file. 
Untuk analisis ini, <b>lirik perlu diinput manual</b> atau dipilih dari sample.
<br><br>
<i>Future Work: Integrasi Speech-to-Text API untuk auto-extract lirik dari audio</i>
</div>
""", unsafe_allow_html=True)

# Lexicon Emosi
@st.cache_data
def load_emotion_lexicon():
    lexicon = {
        'sedih': ['sedih', 'tangis', 'menangis', 'nangis', 'haru', 'sendu', 'duka', 
                  'galau', 'patah', 'hancur', 'luka', 'pergi', 'tinggal', 'kehilangan',
                  'sendiri', 'sepi', 'sunyi', 'sakit', 'perih', 'air mata', 'derita'],
        'bahagia': ['bahagia', 'senang', 'gembira', 'suka', 'ceria', 'senyum', 'tawa',
                    'cinta', 'kasih', 'sayang', 'indah', 'sempurna', 'bersyukur', 'damai'],
        'marah': ['marah', 'benci', 'dendam', 'kesal', 'jengkel', 'geram', 'gila',
                  'hancurkan', 'kacau', 'rusak'],
        'rindu': ['rindu', 'kangen', 'ingat', 'kenang', 'kenangan', 'jauh', 'tunggu',
                  'menunggu', 'harap', 'harapan', 'doa', 'bayang', 'mimpi'],
        'kecewa': ['kecewa', 'bohong', 'tipu', 'janji', 'ingkar', 'khianat', 'dusta',
                   'sia-sia', 'percuma', 'gagal', 'hilang']
    }
    return lexicon

emotion_lexicon = load_emotion_lexicon()

# Fungsi analisis
def analyze_emotion(lyrics, lexicon):
    lyrics_lower = lyrics.lower()
    lyrics_clean = re.sub(r'[^\w\s]', ' ', lyrics_lower)
    words = lyrics_clean.split()
    
    emotion_scores = {}
    emotion_words_found = {}
    
    for emotion, keywords in lexicon.items():
        score = 0
        found_words = []
        for word in words:
            if word in keywords:
                score += 1
                found_words.append(word)
        emotion_scores[emotion] = score
        emotion_words_found[emotion] = found_words
    
    total = sum(emotion_scores.values())
    
    emotion_percentage = {}
    if total > 0:
        for emotion, score in emotion_scores.items():
            emotion_percentage[emotion] = round((score / total) * 100, 1)
    else:
        emotion_percentage = {emotion: 0 for emotion in lexicon.keys()}
    
    if total > 0:
        dominant_emotion = max(emotion_scores, key=emotion_scores.get)
        confidence = emotion_percentage[dominant_emotion]
    else:
        dominant_emotion = "Netral/Tidak Terdeteksi"
        confidence = 0
    
    return {
        'scores': emotion_scores,
        'percentage': emotion_percentage,
        'dominant': dominant_emotion,
        'confidence': confidence,
        'total_words': len(words),
        'matched_words': total,
        'found_words': emotion_words_found
    }

# Database Sample Lagu
@st.cache_data
def load_song_database():
    songs = {
        "🎵 Sample 1: Hati Yang Luka (Sedih)": {
            'lyrics': """Kau pergi tinggalkan aku
Sendiri di sini menunggu
Air mata jatuh membasahi
Hatiku hancur kau sakiti""",
            'emotion': 'sedih',
            'artist': 'Sample Artist'
        },
        "🎵 Sample 2: Cinta Sempurna (Bahagia)": {
            'lyrics': """Bersamamu ku merasa bahagia
Bersamamu ku merasa lengkap
Kau adalah segalanya bagiku
Cinta yang slalu ada untukku""",
            'emotion': 'bahagia',
            'artist': 'Sample Artist'
        },
        "🎵 Sample 3: Menunggu Kamu (Rindu)": {
            'lyrics': """Ku menunggu kamu di sini
Di tempat yang sama kita dulu
Ku berharap kamu kembali
Untuk melengkapi hatiku""",
            'emotion': 'rindu',
            'artist': 'Sample Artist'
        }
    }
    return songs

song_database = load_song_database()

# Session State
if 'selected_song' not in st.session_state:
    st.session_state.selected_song = None
if 'current_lyrics' not in st.session_state:
    st.session_state.current_lyrics = None
if 'analyzed' not in st.session_state:
    st.session_state.analyzed = False
if 'hasil' not in st.session_state:
    st.session_state.hasil = None

# Sidebar - Audio Options
st.sidebar.header("🔊 Audio Playback (Opsional)")

audio_mode = st.sidebar.radio(
    "Pilih Mode Audio:",
    ["📤 Upload File Sendiri", "📺 YouTube Link", "⏭️ Skip Audio"]
)

if audio_mode == "📤 Upload File Sendiri":
    uploaded_file = st.sidebar.file_uploader(
        "Upload file musik (MP3, WAV):",
        type=['mp3', 'wav', 'm4a', 'ogg']
    )
    if uploaded_file:
        st.sidebar.success(f"✅ {uploaded_file.name}")
        st.session_state.uploaded_file = uploaded_file
    else:
        st.session_state.uploaded_file = None
        
elif audio_mode == "📺 YouTube Link":
    youtube_url = st.sidebar.text_input(
        "Paste link YouTube:",
        placeholder="https://www.youtube.com/watch?v=..."
    )
    st.session_state.youtube_url = youtube_url if youtube_url else None

# Main Content - Input Method
st.markdown("### 📝 Input Lirik Lagu")

input_method = st.radio(
    "Pilih Metode Input:",
    ["📚 Pilih dari Sample Database", "✏️ Input Lirik Manual"]
)

if input_method == "📚 Pilih dari Sample Database":
    selected_song = st.selectbox(
        "Pilih Lagu Sample:",
        list(song_database.keys())
    )
    
    if selected_song:
        song_data = song_database[selected_song]
        st.session_state.current_lyrics = song_data['lyrics']
        st.session_state.selected_song = selected_song
        st.session_state.current_emotion = song_data['emotion']
        
elif input_method == "✏️ Input Lirik Manual":
    st.session_state.current_lyrics = st.text_area(
        "Paste lirik lagu di sini:",
        height=200,
        placeholder="Contoh: Kau pergi tinggalkan aku..."
    )
    st.session_state.selected_song = "Custom Input"
    st.session_state.current_emotion = None

# Tampilkan Lirik
if st.session_state.current_lyrics:
    st.markdown("---")
    st.markdown("### 🎤 Lirik yang Akan Dianalisis")
    st.markdown(f"""
    <div class="lyric-box">
    {st.session_state.current_lyrics}
    </div>
    """, unsafe_allow_html=True)
    
    # Audio Player (Optional)
    st.markdown("### 🔊 Audio Playback (Opsional)")
    
    if audio_mode == "📤 Upload File Sendiri" and st.session_state.get('uploaded_file'):
        st.audio(st.session_state.uploaded_file, format='audio/mp3')
        st.info("🎵 Putar musik sambil melihat analisis lirik")
        
    elif audio_mode == "📺 YouTube Link" and st.session_state.get('youtube_url'):
        url = st.session_state.youtube_url
        if 'youtube.com' in url or 'youtu.be' in url:
            st.markdown(f"""
            <div class="info-box">
            📺 <a href="{url}" target="_blank">Klik untuk buka YouTube</a>
            <br><i>Dengarkan di tab baru sambil melihat analisis</i>
            </div>
            """, unsafe_allow_html=True)
    
    # Tombol Analisis
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔍 ANALISIS EMOSI", use_container_width=True, type="primary"):
            hasil = analyze_emotion(st.session_state.current_lyrics, emotion_lexicon)
            st.session_state.analyzed = True
            st.session_state.hasil = hasil

# Tampilkan Hasil
if st.session_state.analyzed and st.session_state.hasil:
    hasil = st.session_state.hasil
    
    st.markdown("---")
    st.markdown("### 📊 Hasil Analisis Emosi")
    st.markdown("---")
    
    emotion_emoji = {
        'sedih': '😢',
        'bahagia': '😊',
        'marah': '😠',
        'rindu': '💕',
        'kecewa': '💔',
        'Netral/Tidak Terdeteksi': '😐'
    }
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Emosi Dominan",
            value=f"{emotion_emoji.get(hasil['dominant'], '😐')} {hasil['dominant'].upper()}",
            delta=f"Confidence: {hasil['confidence']}%"
        )
    
    with col2:
        st.metric("Total Kata", hasil['total_words'])
    
    with col3:
        st.metric("Kata Terdeteksi", hasil['matched_words'])
    
    with col4:
        coverage = round((hasil['matched_words'] / hasil['total_words']) * 100, 1) if hasil['total_words'] > 0 else 0
        st.metric("Coverage Lexicon", f"{coverage}%")
    
    # Grafik
    st.markdown("### 📈 Distribusi Emosi")
    df_emosi = pd.DataFrame({
        'Emosi': list(hasil['percentage'].keys()),
        'Persentase': list(hasil['percentage'].values())
    })
    st.bar_chart(df_emosi.set_index('Emosi'), use_container_width=True)
    
    # Progress Bars
    st.markdown("### 📊 Detail Skor")
    for emosi, persentase in sorted(hasil['percentage'].items(), key=lambda x: x[1], reverse=True):
        emoji = emotion_emoji.get(emosi, '😐')
        st.markdown(f"**{emoji} {emosi.capitalize()}: {persentase}%**")
        st.progress(int(persentase))
    
    # Kata Kunci
    st.markdown("---")
    st.markdown("### 🔑 Kata Kunci Ditemukan")
    for emosi, words in hasil['found_words'].items():
        if words:
            with st.expander(f"{emotion_emoji.get(emosi, '😐')} {emosi.capitalize()} ({len(words)} kata)"):
                st.write(f"**Kata:** {', '.join(words)}")
    
    # Validasi
    if st.session_state.get('current_emotion'):
        st.markdown("---")
        st.markdown("### 🎯 Validasi")
        if hasil['dominant'] == st.session_state.current_emotion:
            st.success(f"✅ **SESUAI!** Terdeteksi: {hasil['dominant']} = Label: {st.session_state.current_emotion}")
        else:
            st.warning(f"⚠️ **BERBEDA!** Terdeteksi: {hasil['dominant']}, Label: {st.session_state.current_emotion}")
    
    # Reset
    st.markdown("---")
    if st.button("🔄 Reset"):
        st.session_state.analyzed = False
        st.session_state.hasil = None
        st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<center>
<b>🎵 Lyric Emotion Analyzer - Skripsi S1 Ilmu Komputer</b><br>
Metode: Lexicon-Based Sentiment Analysis | Built with Streamlit & Python<br><br>
<i>⚠️ Lirik diinput manual karena file audio tidak menyimpan teks lirik</i><br>
<i>🔮 Future Work: Integrasi Speech-to-Text API untuk auto-extraction</i>
</center>
""", unsafe_allow_html=True)
