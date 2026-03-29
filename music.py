import streamlit as st
import pandas as pd
import re
from collections import Counter
import base64

# Konfigurasi halaman
st.set_page_config(page_title="Analisis Emosi Lirik & Musik", page_icon="🎵", layout="wide")

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
        padding: 10px 24px;
        border-radius: 5px;
        font-weight: bold;
    }
    .music-player {
        background: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .lyric-box {
        background: rgba(255,255,255,0.9);
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        white-space: pre-line;
    }
    </style>
    """, unsafe_allow_html=True)

# Judul
st.title("🎵 Analisis Emosi Lirik & Musik Pop Indonesia")
st.markdown("### Deteksi Emosi Dominan dengan Audio Playback")
st.markdown("---")

# Lexicon Emosi (Bahasa Indonesia)
@st.cache_data
def load_emotion_lexicon():
    lexicon = {
        'sedih': [
            'sedih', 'sedihnya', 'tangis', 'menangis', 'nangis', 'pilus', 
            'haru', 'sendu', 'duka', 'nestapa', 'galau', 'patah', 'hancur', 'luka',
            'pergi', 'tinggal', 'kehilangan', 'kalah', 'gagal', 'putus', 'cerai',
            'sendiri', 'sepi', 'sunyi', 'kesepian', 'merana', 'sakit', 'perih',
            'air mata', 'airmata', 'ratap', 'keluh', 'derita', 'siksa'
        ],
        'bahagia': [
            'bahagia', 'senang', 'gembira', 'suka', 'ceria', 'riang', 'happy',
            'senyum', 'tersenyum', 'tawa', 'tertawa', 'ketawa', 'bangga', 'puas',
            'cinta', 'kasih', 'sayang', 'rindu', 'kangen', 'indah', 'manis',
            'sempurna', 'beruntung', 'bersyukur', 'damai', 'tenang', 'nyaman',
            'bersama', 'peluk', 'cium', 'dekapan', 'hangat', 'merona'
        ],
        'marah': [
            'marah', 'marahnya', 'marahi', 'benci', 'bencinya', 'dendam', 'kesal',
            'jengkel', 'geram', 'murka', 'nafsu', 'gila', 'ganas', 'buas',
            'sakit hati', 'balas', 'hancurkan', 'binasakan', 'lenyap',
            'kacau', 'berantakan', 'rusak', 'hancur'
        ],
        'rindu': [
            'rindu', 'rinduku', 'kangen', 'kangennya', 'kangenmu',
            'ingat', 'teringat', 'kenang', 'kenangan', 'masa lalu', 'dulu',
            'jauh', 'jauhnya', 'pisahnya', 'berpisah', 'jarak', 'waktu',
            'tunggu', 'menunggu', 'harap', 'harapan', 'doa',
            'bayang', 'bayangan', 'mimpi', 'impian', 'khayal'
        ],
        'kecewa': [
            'kecewa', 'kecewanya', 'kecewaku', 'kecewamu',
            'khayal', 'khayalan', 'bohong', 'bohongi', 'tipu', 'tipu daya',
            'janji', 'ingkar', 'khianat', 'selingkuh', 'dusta', 'palsu',
            'sia-sia', 'sia sia', 'percuma', 'gagal', 'hilang', 'lenyap'
        ]
    }
    return lexicon

emotion_lexicon = load_emotion_lexicon()

# Fungsi analisis emosi
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

# Sample data dengan info audio
sample_songs = {
    "Sample 1 - Melankolis (Copyright-Free)": {
        'lyrics': """Kau pergi tinggalkan aku
Sendiri di sini menunggu
Air mata jatuh membasahi
Hatiku hancur kau sakiti

Mengapa kau pergi tanpa pamit
Tinggalkan aku yang mencintai
Kini hanya sepi yang ada
Dalam hatiku yang terluka""",
        'emotion_hint': 'sedih',
        'audio_type': 'sample',
        'youtube_id': ''  # Bisa diisi ID YouTube jika ada
    },
    "Sample 2 - Bahagia (Copyright-Free)": {
        'lyrics': """Bersamamu ku merasa bahagia
Bersamamu ku merasa lengkap
Kau adalah segalanya bagiku
Cinta yang slalu ada untukku

Senyummu maniskan hariku
Tawamu hiburkan jiwaku
Bersyukur ku padamu
Cinta sempurna dari tuhan""",
        'emotion_hint': 'bahagia',
        'audio_type': 'sample',
        'youtube_id': ''
    },
    "Sample 3 - Rindu (Copyright-Free)": {
        'lyrics': """Ku menunggu kamu di sini
Di tempat yang sama kita dulu
Ku berharap kamu kembali
Untuk melengkapi hatiku

Waktu terus berlalu pergi
Namun cintaku tetap di sini
Menunggu kamu yang tak pasti
Rindu ini tak pernah berakhir""",
        'emotion_hint': 'rindu',
        'audio_type': 'sample',
        'youtube_id': ''
    }
}

# Sidebar
st.sidebar.header("🎵 Player Musik")

# Pilihan input audio
audio_option = st.sidebar.radio(
    "Pilih Sumber Audio:",
    ["Upload File Sendiri", "Gunakan Sample", "YouTube Link"]
)

audio_file = None
youtube_url = ""

if audio_option == "Upload File Sendiri":
    uploaded_file = st.sidebar.file_uploader(
        "Upload file musik (MP3, WAV, M4A):",
        type=['mp3', 'wav', 'm4a', 'ogg']
    )
    if uploaded_file:
        audio_file = uploaded_file
        st.sidebar.success(f"✅ File: {uploaded_file.name}")
        
elif audio_option == "Gunakan Sample":
    st.sidebar.info("📝 Sample audio akan tersedia setelah pilih lagu")
    
elif audio_option == "YouTube Link":
    youtube_url = st.sidebar.text_input(
        "Masukkan link YouTube (opsional):",
        placeholder="https://www.youtube.com/watch?v=..."
    )
    if youtube_url:
        st.sidebar.success("✅ Link YouTube disimpan")

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Pengaturan Analisis")

show_analysis = st.sidebar.checkbox("Tampilkan Analisis Detail", value=True)
show_word_cloud = st.sidebar.checkbox("Tampilkan Kata Kunci", value=True)
auto_analyze = st.sidebar.checkbox("Auto Analisis saat Upload", value=False)

# Main content
st.markdown("### 🎤 Pilih atau Input Lirik Lagu")

selected_sample = st.selectbox(
    "Pilih Sample Lagu (Copyright-Free):",
    list(sample_songs.keys())
)

# Auto-fill lirik dari sample
if selected_sample:
    song_data = sample_songs[selected_sample]
    st.session_state.current_song = selected_sample
    st.session_state.current_lyrics = song_data['lyrics']
    st.session_state.current_hint = song_data['emotion_hint']

lyrics_input = st.text_area(
    "Masukkan/Editar lirik lagu:",
    value=st.session_state.get('current_lyrics', ''),
    height=200,
    placeholder="Paste lirik lagu di sini..."
)

# Simpan lirik
st.session_state.lyrics = lyrics_input

# Audio Player Section
st.markdown("---")
st.markdown("### 🔊 Audio Player")

col1, col2 = st.columns([2, 1])

with col1:
    if audio_option == "Upload File Sendiri" and audio_file:
        st.audio(audio_file, format='audio/mp3')
        st.success("🎵 File musik sedang diputar")
        
    elif audio_option == "Gunakan Sample" and selected_sample:
        # Generate sample audio (placeholder - bisa diganti dengan file asli)
        st.info("📝 Untuk demo ini, silakan upload file musik Anda sendiri atau gunakan YouTube link")
        st.markdown("""
        **Catatan Copyright:**
        - Lagu komersial memiliki hak cipta
        - Untuk skripsi/demo, gunakan:
          - Musik copyright-free
          - Upload file pribadi (fair use)
          - YouTube embed (link saja)
        """)
        
    elif audio_option == "YouTube Link" and youtube_url:
        # Extract YouTube ID
        if 'youtube.com' in youtube_url or 'youtu.be' in youtube_url:
            st.markdown(f"""
            <div class="music-player">
            <h4>📺 YouTube Player</h4>
            <p>Link: {youtube_url[:50]}...</p>
            <p><i>Buka link di tab baru untuk mendengarkan sambil melihat analisis</i></p>
            <a href="{youtube_url}" target="_blank" style="background: #FF0000; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">🎬 Buka YouTube</a>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ Link YouTube tidak valid")
    else:
        st.info("👈 Pilih sumber audio dari sidebar")

with col2:
    st.markdown("### 📊 Info Lagu")
    if selected_sample:
        st.markdown(f"**Judul:** {selected_sample}")
        st.markdown(f"**Emosi Hint:** {sample_songs[selected_sample]['emotion_hint']}")
    if st.session_state.get('lyrics', ''):
        word_count = len(st.session_state.lyrics.split())
        st.markdown(f"**Jumlah Kata:** {word_count}")

# Tombol analisis
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    analyze_btn = st.button("🔍 Analisis Emosi Lirik", use_container_width=True)

# Session state untuk hasil
if 'analyzed' not in st.session_state:
    st.session_state.analyzed = False
if 'hasil' not in st.session_state:
    st.session_state.hasil = None

if analyze_btn and lyrics_input.strip():
    hasil = analyze_emotion(lyrics_input, emotion_lexicon)
    st.session_state.analyzed = True
    st.session_state.hasil = hasil
elif auto_analyze and lyrics_input.strip() and not st.session_state.analyzed:
    hasil = analyze_emotion(lyrics_input, emotion_lexicon)
    st.session_state.analyzed = True
    st.session_state.hasil = hasil

# Tampilkan hasil analisis
if st.session_state.analyzed and st.session_state.hasil:
    hasil = st.session_state.hasil
    
    st.markdown("---")
    st.markdown("### 📊 Hasil Analisis Emosi")
    st.markdown("---")
    
    # Emosi Dominan
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
    
    st.markdown("---")
    
    # Grafik
    st.markdown("### 📈 Distribusi Emosi")
    
    df_emosi = pd.DataFrame({
        'Emosi': list(hasil['percentage'].keys()),
        'Persentase': list(hasil['percentage'].values())
    })
    
    st.bar_chart(df_emosi.set_index('Emosi'), use_container_width=True)
    
    # Progress bar
    st.markdown("### 📊 Detail Skor Emosi")
    
    for emosi, persentase in sorted(hasil['percentage'].items(), key=lambda x: x[1], reverse=True):
        emoji = emotion_emoji.get(emosi, '😐')
        st.markdown(f"**{emoji} {emosi.capitalize()}: {persentase}%**")
        st.progress(int(persentase))
    
    # Kata kunci
    if show_analysis and hasil['matched_words'] > 0:
        st.markdown("---")
        st.markdown("### 🔑 Kata Kunci Emosi yang Ditemukan")
        
        for emosi, words in hasil['found_words'].items():
            if words:
                with st.expander(f"{emotion_emoji.get(emosi, '😐')} {emosi.capitalize()} ({len(words)} kata)"):
                    st.write(f"**Kata ditemukan:** {', '.join(words)}")
    
    # Interpretasi
    st.markdown("---")
    st.markdown("### 💡 Interpretasi Hasil")
    
    if hasil['dominant'] == 'sedih':
        st.info("🎵 **Nuansa:** MELANKOLIS | Cocok untuk: Refleksi, melepaskan kesedihan")
    elif hasil['dominant'] == 'bahagia':
        st.success("🎵 **Nuansa:** POSITIF & CERIA | Cocok untuk: Meningkatkan mood, semangat")
    elif hasil['dominant'] == 'marah':
        st.warning("🎵 **Nuansa:** AGRESIF | Cocok untuk: Melepaskan emosi, motivasi")
    elif hasil['dominant'] == 'rindu':
        st.info("🎵 **Nuansa:** ROMANTIS | Cocok untuk: Momen kenangan, galau")
    elif hasil['dominant'] == 'kecewa':
        st.warning("🎵 **Nuansa:** KEKECEWAAN | Cocok untuk: Cerita pengkhianatan")
    else:
        st.info("🎵 **Nuansa:** NETRAL | Emosi tidak terdeteksi jelas")
    
    # Tombol reset
    st.markdown("---")
    if st.button("🔄 Reset Analisis"):
        st.session_state.analyzed = False
        st.session_state.hasil = None
        st.rerun()

else:
    st.markdown("---")
    st.markdown("### 💡 Cara Menggunakan:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **1️⃣ Pilih Audio**
        - Upload file musik
        - Atau gunakan sample
        - Atau YouTube link
        """)
    
    with col2:
        st.markdown("""
        **2️⃣ Input Lirik**
        - Pilih sample lagu
        - Atau paste lirik sendiri
        """)
    
    with col3:
        st.markdown("""
        **3️⃣ Analisis**
        - Klik tombol analisis
        - Lihat hasil emosi
        - Dengarkan musik
        """)

# Disclaimer
st.markdown("---")
st.markdown("""
<center>
<b>⚠️ DISCLAIMER:</b><br>
Demo ini untuk tujuan EDUCATIONAL & SKRIPSI saja.<br>
Semua lagu komersial memiliki hak cipta masing-masing pemilik.<br>
Untuk penggunaan pribadi, silakan upload file musik Anda sendiri.<br><br>
<b>🎵 Analisis Emosi Lirik Lagu Pop Indonesia - Skripsi S1 Ilmu Komputer</b><br>
Metode: Lexicon-Based Sentiment Analysis | Built with Streamlit & Python
</center>
""", unsafe_allow_html=True)
