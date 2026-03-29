import streamlit as st
import pandas as pd
import re
import base64

# Konfigurasi halaman
st.set_page_config(page_title="Auto Lyric Analyzer", page_icon="🎵", layout="wide")

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
    .music-player {
        background: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
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
    .song-card {
        background: white;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        cursor: pointer;
        transition: transform 0.2s;
    }
    .song-card:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .emotion-badge {
        display: inline-block;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        margin: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# Judul
st.title("🎵 Auto Lyric Emotion Analyzer")
st.markdown("### Pilih Lagu → Lirik Otomatis Muncul → Analisis Emosi")
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

# DATABASE LAGU SAMPLE (Bundling: Judul + Lirik + Info Emosi + Audio Reference)
@st.cache_data
def load_song_database():
    songs = {
        "🎵 Sample 1: Hati Yang Luka (Melankolis)": {
            'lyrics': """Kau pergi tinggalkan aku
Sendiri di sini menunggu
Air mata jatuh membasahi
Hatiku hancur kau sakiti

Mengapa kau pergi tanpa pamit
Tinggalkan aku yang mencintai
Kini hanya sepi yang ada
Dalam hatiku yang terluka

Kini ku belajar ikhlas
Melepaskan semua kenangan
Meski sakit yang ku rasa
Ku coba untuk bertahan""",
            'emotion_hint': 'sedih',
            'emotion_color': '#FF6B6B',
            'tempo': 'Lambat',
            'year': '2024',
            'audio_note': '🎹 Piano & Strings'
        },
        "🎵 Sample 2: Cinta Sempurna (Bahagia)": {
            'lyrics': """Bersamamu ku merasa bahagia
Bersamamu ku merasa lengkap
Kau adalah segalanya bagiku
Cinta yang slalu ada untukku

Senyummu maniskan hariku
Tawamu hiburkan jiwaku
Bersyukur ku padamu
Cinta sempurna dari tuhan

Tak ada yang bisa pisahkan
Kita berdua selamanya
Kau dan aku satu jiwa
Dalam cinta yang nyata""",
            'emotion_hint': 'bahagia',
            'emotion_color': '#4ECDC4',
            'tempo': 'Sedang',
            'year': '2024',
            'audio_note': '🎸 Acoustic Guitar'
        },
        "🎵 Sample 3: Menunggu Kamu (Rindu)": {
            'lyrics': """Ku menunggu kamu di sini
Di tempat yang sama kita dulu
Ku berharap kamu kembali
Untuk melengkapi hatiku

Waktu terus berlalu pergi
Namun cintaku tetap di sini
Menunggu kamu yang tak pasti
Rindu ini tak pernah berakhir

Setiap malam ku bermimpi
Tentang dirimu yang jauh
Kapan kita bertemu lagi
Menghapus semua rindu""",
            'emotion_hint': 'rindu',
            'emotion_color': '#95E1D3',
            'tempo': 'Lambat',
            'year': '2024',
            'audio_note': '🎹 Piano Ballad'
        },
        "🎵 Sample 4: Pengkhianatan (Kecewa)": {
            'lyrics': """Janji yang kau ucapkan dulu
Kini tinggal kenangan saja
Kau ingkari semua kata
Tinggalkan aku yang percaya

Sakit hati yang ku rasa
Saat kau bersamanya
Khianat yang kau berikan
Hancurkan semua harapan""",
            'emotion_hint': 'kecewa',
            'emotion_color': '#F38181',
            'tempo': 'Sedang',
            'year': '2024',
            'audio_note': '🎸 Electric Guitar'
        },
        "🎵 Sample 5: Semangat Baru (Marah/Motivasi)": {
            'lyrics': """Ku tak akan menyerah lagi
Meski dunia melawan aku
Akan ku buktikan pada semua
Bahwa ku bisa meraih mimpi

Bakar semua keraguan
Hancurkan semua batasan
Ku akan bangkit kembali
Lebih kuat dari sebelumnya""",
            'emotion_hint': 'marah',
            'emotion_color': '#AA96DA',
            'tempo': 'Cepat',
            'year': '2024',
            'audio_note': '🥁 Rock Drums'
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
st.sidebar.header("🔊 Audio Playback")

audio_mode = st.sidebar.radio(
    "Pilih Mode Audio:",
    ["📀 Sample Audio Info", "📤 Upload File Sendiri", "📺 YouTube Link"]
)

if audio_mode == "📤 Upload File Sendiri":
    uploaded_file = st.sidebar.file_uploader(
        "Upload file musik (MP3, WAV, M4A):",
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
    if youtube_url:
        st.sidebar.success("✅ Link tersimpan")

# Main Content - Song Selection
st.markdown("### 🎤 Pilih Lagu untuk Dianalisis")
st.markdown("*Lirik akan otomatis muncul saat lagu dipilih*")

selected_song = st.selectbox(
    "Pilih dari Database Lagu:",
    list(song_database.keys()),
    key="song_selector"
)

# Auto-load lirik saat lagu dipilih
if selected_song:
    song_data = song_database[selected_song]
    st.session_state.selected_song = selected_song
    st.session_state.current_lyrics = song_data['lyrics']
    st.session_state.current_hint = song_data['emotion_hint']
    st.session_state.current_color = song_data['emotion_color']
    st.session_state.current_tempo = song_data['tempo']
    st.session_state.current_year = song_data['year']
    st.session_state.current_audio_note = song_data['audio_note']
    st.session_state.analyzed = False  # Reset analisis saat ganti lagu
    st.session_state.hasil = None

# Tampilkan Info Lagu & Lirik
if st.session_state.current_lyrics:
    song_data = song_database[st.session_state.selected_song]
    
    st.markdown("---")
    
    # Info Card
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="song-card">
        <b>🎭 Emosi</b><br>
        <span class="emotion-badge" style="background: {song_data['emotion_color']}">
        {song_data['emotion_hint'].upper()}
        </span>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="song-card">
        <b>🎵 Tempo</b><br>
        {song_data['tempo']}
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="song-card">
        <b>📅 Tahun</b><br>
        {song_data['year']}
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="song-card">
        <b>🎹 Instrumen</b><br>
        {song_data['audio_note']}
        </div>
        """, unsafe_allow_html=True)
    
    # Lirik Box
    st.markdown("### 📝 Lirik Lagu")
    st.markdown(f"""
    <div class="lyric-box">
    {st.session_state.current_lyrics}
    </div>
    """, unsafe_allow_html=True)
    
    # Audio Player Section
    st.markdown("### 🔊 Audio Playback")
    
    if audio_mode == "📀 Sample Audio Info":
        st.info(f"""
        🎵 **{st.session_state.selected_song}**
        
        **Catatan Audio:** {st.session_state.current_audio_note}
        
        💡 *Untuk demo ini, silakan upload file musik Anda sendiri atau gunakan YouTube link untuk mendengarkan sambil melihat analisis lirik.*
        
        **Alternatif:** Cari lagu dengan mood serupa di YouTube Music / Spotify
        """)
        
    elif audio_mode == "📤 Upload File Sendiri":
        if st.session_state.get('uploaded_file'):
            st.audio(st.session_state.uploaded_file, format='audio/mp3')
            st.success("🎵 File musik sedang diputar")
        else:
            st.warning("⚠️ Upload file musik di sidebar terlebih dahulu")
            
    elif audio_mode == "📺 YouTube Link":
        if st.session_state.get('youtube_url'):
            url = st.session_state.youtube_url
            if 'youtube.com' in url or 'youtu.be' in url:
                st.markdown(f"""
                <div class="music-player">
                <h4>📺 YouTube Player</h4>
                <p>🔗 <a href="{url}" target="_blank">Klik untuk buka di YouTube</a></p>
                <p><i>Dengarkan musik di tab baru sambil melihat analisis di sini</i></p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("⚠️ Link YouTube tidak valid")
        else:
            st.warning("⚠️ Masukkan link YouTube di sidebar terlebih dahulu")
    
    # Tombol Analisis
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔍 ANALISIS EMOSI LIRIK", use_container_width=True, type="primary"):
            hasil = analyze_emotion(st.session_state.current_lyrics, emotion_lexicon)
            st.session_state.analyzed = True
            st.session_state.hasil = hasil

# Tampilkan Hasil Analisis
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
    
    # Metric Cards
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
    
    # Bar Chart
    st.markdown("### 📈 Distribusi Emosi")
    
    df_emosi = pd.DataFrame({
        'Emosi': list(hasil['percentage'].keys()),
        'Persentase': list(hasil['percentage'].values())
    })
    
    st.bar_chart(df_emosi.set_index('Emosi'), use_container_width=True)
    
    # Progress Bars
    st.markdown("### 📊 Detail Skor Emosi")
    
    for emosi, persentase in sorted(hasil['percentage'].items(), key=lambda x: x[1], reverse=True):
        emoji = emotion_emoji.get(emosi, '😐')
        st.markdown(f"**{emoji} {emosi.capitalize()}: {persentase}%**")
        st.progress(int(persentase))
    
    # Kata Kunci
    st.markdown("---")
    st.markdown("### 🔑 Kata Kunci Emosi yang Ditemukan")
    
    for emosi, words in hasil['found_words'].items():
        if words:
            with st.expander(f"{emotion_emoji.get(emosi, '😐')} {emosi.capitalize()} ({len(words)} kata)"):
                st.write(f"**Kata ditemukan:** {', '.join(words)}")
    
    # Interpretasi
    st.markdown("---")
    st.markdown("### 💡 Interpretasi Hasil")
    
    interpretasi = {
        'sedih': "🎵 **Nuansa:** MELANKOLIS | Cocok untuk: Refleksi, melepaskan kesedihan, momen galau",
        'bahagia': "🎵 **Nuansa:** POSITIF & CERIA | Cocok untuk: Meningkatkan mood, semangat, perayaan",
        'marah': "🎵 **Nuansa:** AGRESIF/MOTIVASI | Cocok untuk: Melepaskan emosi, workout, motivasi",
        'rindu': "🎵 **Nuansa:** ROMANTIS | Cocok untuk: Momen kenangan, LDR, nostalgia",
        'kecewa': "🎵 **Nuansa:** KEKECEWAAN | Cocok untuk: Cerita pengkhianatan, move on",
        'Netral/Tidak Terdeteksi': "🎵 **Nuansa:** NETRAL | Emosi tidak terdeteksi jelas, mungkin lagu instrumental atau lexicon perlu diperluas"
    }
    
    st.info(interpretasi.get(hasil['dominant'], interpretasi['Netral/Tidak Terdeteksi']))
    
    # Compare dengan Hint
    if st.session_state.get('current_hint'):
        st.markdown("---")
        st.markdown("### 🎯 Validasi Hasil")
        
        if hasil['dominant'] == st.session_state.current_hint:
            st.success(f"✅ **HASIL SESUAI!** Emosi terdeteksi ({hasil['dominant']}) cocok dengan label lagu ({st.session_state.current_hint})")
        else:
            st.warning(f"⚠️ **HASIL BERBEDA!** Terdeteksi: {hasil['dominant']}, Label: {st.session_state.current_hint}")
            st.info("Ini bisa terjadi karena lexicon perlu penyesuaian atau lagu memiliki emosi campuran")
    
    # Reset Button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Pilih Lagu Lain", use_container_width=True):
            st.session_state.analyzed = False
            st.session_state.hasil = None
            st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<center>
<b>🎵 Auto Lyric Emotion Analyzer - Skripsi S1 Ilmu Komputer</b><br>
Metode: Lexicon-Based Sentiment Analysis | Built with Streamlit & Python<br><br>
<i>⚠️ Sample lagu untuk tujuan EDUKASI & DEMO skripsi saja</i>
</center>
""", unsafe_allow_html=True)
