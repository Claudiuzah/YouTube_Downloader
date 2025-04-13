import tkinter as tk
from tkinter import filedialog, messagebox
import yt_dlp
import os
import re
import threading


def is_valid_url(url):
    youtube_regex = r"^(https?:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+"
    return re.match(youtube_regex, url) is not None


def get_video_info(url):
    try:
        ydl_opts = {'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Titlu necunoscut')
            is_playlist = info.get('_type', '') == 'playlist'
            formats = info.get('formats', []) if not is_playlist else []
            resolutions = sorted(set(f"{f['height']}p" for f in formats if f.get('height') and f['height'] >= 480),
                                 reverse=True)
            return title, resolutions, is_playlist
    except Exception as e:
        return "", [], False


def update_video_info():
    url = url_entry.get()
    if not url or not is_valid_url(url):
        messagebox.showerror("Eroare", "Introduceți un link YouTube valid!")
        return

    def fetch_info():
        title, quality_options, is_playlist = get_video_info(url)
        root.after(0, lambda: title_label.config(text=f"Titlu: {title} ({'Playlist' if is_playlist else 'Video'})"))

        if quality_options:
            root.after(0, lambda: quality_var.set(quality_options[0]))
            root.after(0, lambda: quality_menu['menu'].delete(0, 'end'))
            for quality in quality_options:
                root.after(0, lambda q=quality: quality_menu['menu'].add_command(label=q,
                                                                                 command=tk._setit(quality_var, q)))

    threading.Thread(target=fetch_info, daemon=True).start()


def download_video():
    url = url_entry.get()
    if not url or not is_valid_url(url):
        messagebox.showerror("Eroare", "Introduceți un link YouTube valid!")
        return

    save_path = filedialog.askdirectory()
    if not save_path:
        return

    selected_quality = quality_var.get()
    selected_format = format_var.get()

    def download():
        ydl_opts = {
            'outtmpl': os.path.join(save_path,
                                    '%(playlist_title)s/%(title)s.%(ext)s') if 'playlist' in url else os.path.join(
                save_path, '%(title)s.%(ext)s'),
            'format': f'bestvideo[height={selected_quality[:-1]}]+bestaudio/best' if selected_quality else 'best',
            'merge_output_format': selected_format,
            'ignoreerrors': True  # Skip files with errors
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            pass

    threading.Thread(target=download, daemon=True).start()


def download_audio():
    url = url_entry.get()
    if not url or not is_valid_url(url):
        messagebox.showerror("Eroare", "Introduceți un link YouTube valid!")
        return

    save_path = filedialog.askdirectory()
    if not save_path:
        return

    def download():
        ydl_opts = {
            'outtmpl': os.path.join(save_path,
                                    '%(playlist_title)s/%(title)s.%(ext)s') if 'playlist' in url else os.path.join(
                save_path, '%(title)s.%(ext)s'),
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '0',
            }],
            'ignoreerrors': True  # Skip files with errors
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            pass

    threading.Thread(target=download, daemon=True).start()


def paste_from_clipboard():
    url_entry.delete(0, tk.END)
    url_entry.insert(0, root.clipboard_get())
    update_video_info()


# Creare interfață grafică
root = tk.Tk()
root.title("YouTube Downloader")
root.geometry("500x400")

tk.Label(root, text="Introduceți link-ul YouTube:").pack(pady=5)
url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=5)

tk.Button(root, text="Lipește link", command=paste_from_clipboard).pack(pady=5)
tk.Button(root, text="Verifică informațiile video", command=update_video_info).pack(pady=5)

title_label = tk.Label(root, text="Titlu: ")
title_label.pack(pady=5)

quality_var = tk.StringVar(root)
quality_var.set("Selectează calitatea")
quality_menu = tk.OptionMenu(root, quality_var, "")
quality_menu.pack(pady=5)

format_var = tk.StringVar(root)
format_var.set("mp4")
tk.Label(root, text="Alege formatul video:").pack(pady=5)
format_menu = tk.OptionMenu(root, format_var, "mp4", "mkv")
format_menu.pack(pady=5)

tk.Button(root, text="Descarcă Video", command=download_video).pack(pady=5)
tk.Button(root, text="Descarcă Audio", command=download_audio).pack(pady=5)

tk.Button(root, text="Ieșire", command=root.quit).pack(pady=5)

root.mainloop()
