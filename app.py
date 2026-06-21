import os
import json
import re
import subprocess
import sys
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
        song_title = parts[0].strip()
        artist = parts[1].strip()
    else:
        song_title = title.strip()
        artist = "Unknown Artist"
        
    return song_title, artist

def get_multiline_input(prompt):
    print(prompt)
    print("👉 (පේස්ට් කරලා ඉවර වුණාම අලුත් පේළියකට ගොස් 'Ctrl+Z' ඔබලා Enter කරන්න. Skip කරන්න අවශ්‍ය නම් නිකන්ම Ctrl+Z ඔබලා Enter කරන්න)")
    try:
        lines = sys.stdin.read()
        return lines.strip()
    except:
        return ""

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
            "lyrics": "",
            "chords": "",
            "lyricsFile": "lyrics.txt",
            "chordsFile": "chords.pdf",
            "trending": True,
            "isAvailableOnSite": True,
            "views": 0
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
            print("-" * 50)
            print("👁️ YouTube එකෙන් හඳුනාගත් දත්ත පරීක්ෂා කරන්න:")
            
            print(f"  [වත්මන් Title එක]: {song_data['title']}")
            user_title = input("👉 නිවැරදි සින්දුවේ නම (Title) ඇතුළත් කරන්න (හරි නම් නිකන්ම Enter කරන්න): ").strip()
            if user_title:
                song_data['title'] = user_title
                
            print(f"  [වත්මන් Artist එක]: {song_data['artist']}")
            user_artist = input("👉 නිවැරදි ගායකයාගේ නම (Artist) ඇතුළත් කරන්න (හරි නම් නිකන්ම Enter කරන්න): ").strip()
            if user_artist:
                song_data['artist'] = user_artist

            print("-" * 50)
            print(f"🔥 අවසන් තීරණය: {song_data['title']} | Artist: {song_data['artist']}")
            print("-" * 50)
            
            lyrics_input = get_multiline_input(f"📝 1. '{song_data['title']}' ගීතයේ පද (Lyrics) මෙතනට Paste කරන්න:")
            print("-" * 50)
            chords_input = get_multiline_input(f"🎸 2. '{song_data['title']}' ගීතයේ Chords මෙතනට Paste කරන්න:")
            
            song_data["lyrics"] = lyrics_input if lyrics_input else "🚫 මෙම ගීතය සඳහා පද (Lyrics) තවමත් ඇතුළත් කර නැත."
            song_data["chords"] = chords_input if chords_input else "🚫 මෙම ගීතය සඳහා Chords තවමත් ඇතුළත් කර නැත."
            
            inject_and_push_to_cloud(song_data)
        except Exception as e:
            print(f"❌ දෝෂයක් සිදු විය: {e}")
    else:
        print("❌ වැරදි YouTube ලින්ක් එකක්.")