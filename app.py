import os
import json
import re
import subprocess
from yt_dlp import YoutubeDL

HTML_FILE = "index.html"

def clean_youtube_title(title):
    title = re.sub(r'\[.*?\]|\(.*?\)', '', title).strip()
    parts = []
    if " - " in title:
        parts = title.split(" - ")
    elif " | " in title:
        parts = title.split(" | ")
        
    if len(parts) >= 2:
        artist = parts[0].strip()
        song_title = parts[1].strip()
    else:
        artist = "Unknown Artist"
        song_title = title.strip()
        
    return song_title, artist

def extract_youtube_data(url):
    ydl_opts = {'skip_download': True}
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        video_id = info.get('id')
        raw_title = info.get('title')
        upload_date = info.get('upload_date')
        
        year = upload_date[:4] if upload_date else "2026"
        duration_sec = info.get('duration', 0)
        duration = f"{duration_sec // 60}:{duration_sec % 60:02d}"
        
        song_title, artist = clean_youtube_title(raw_title)
        thumbnail = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
        
        return {
            "id": f"s_{video_id}",
            "title": song_title,
            "artist": artist,
            "year": year,
            "duration": duration,
            "thumbnail": thumbnail,
            "youtubeUrl": f"https://youtu.be/{video_id}",
            "audioUrl": "downloaded_song.mp3",
            "karaokeSiteUrl": "",
            "lyrics": f"{song_title} lyrics will be updated soon...",
            "chords": f"[C] Chords for {song_title} will be updated soon...",
            "lyricsFile": "lyrics.txt",
            "chordsFile": "chords.pdf",
            "trending": True,
            "isAvailableOnSite": True
        }

def inject_and_push_to_cloud(new_song):
    if not os.path.exists(HTML_FILE):
        print(f"❌ {HTML_FILE} සොයාගත නොහැක!")
        return False

    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        html_content = f.read()

    pattern = r'(const\s+songs\s*=\s*\[)(.*?)(\];)'
    match = re.search(pattern, html_content, re.DOTALL)

    if not match:
        print("❌ HTML එක ඇතුළේ 'const songs = [];' කොටස හඳුනාගත නොහැකි විය!")
        return False

    existing_songs_str = match.group(2).strip()
    new_song_js = json.dumps(new_song, indent=16, ensure_ascii=False)
    new_song_js = new_song_js.strip().replace('\n', '\n' + ' ' * 12)

    if existing_songs_str:
        updated_songs_str = f"{existing_songs_str}\n{',' if not existing_songs_str.endswith(',') else ''}{new_song_js},"
    else:
        updated_songs_str = f"\n{new_song_js},"

    new_html_content = html_content.replace(match.group(0), f"const songs = [{updated_songs_str}\n        ];")

    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(new_html_content)
        
    print("==> 🎵 සින්දුව index.html එකට ඇතුළත් කළා. දැන් Cloud එකට Live Publish කරමින් පවතී...")

    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", f"Auto added song: {new_song['title']}"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("⚡🔥 Boom! GitHub එක හරහා මුළු වෙබ් අඩවියම ස්වයංක්‍රීයව ලයිව් අප්ඩේට් වුණා මචං!")
        return True
    except Exception as e:
        print(f"❌ Cloud එකට Push කිරීමට නොහැකි විය: {e}")
        return False

if __name__ == "__main__":
    print("====== LKSongs ULTRA CLOUD AUTOMATION TOOL ======")
    yt_url = input("🔗 YouTube Song Link එක මෙතනට Paste කරන්න: ").strip()
    
    if "youtube.com" in yt_url or "youtu.be" in yt_url:
        try:
            print("⏳ YouTube එකෙන් දත්ත ලබාගනිමින් පවතී...")
            song_data = extract_youtube_data(yt_url)
            print(f"👁️ හමු වූ විස්තර: {song_data['title']} | Artist: {song_data['artist']}")
            inject_and_push_to_cloud(song_data)
        except Exception as e:
            print(f"❌ දෝෂයක් සිදු විය: {e}")
    else:
        print("❌ වැරදි YouTube ලින්ක් එකක්.")