import tkinter as tk
from tkinter import filedialog, messagebox
import yt_dlp
import os
import re


def is_valid_url(url):
    youtube_regex = r"^(https?:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+"
    return re.match(youtube_regex, url) is not None


def get_video_info(url):
    try:
        ydl_opts = {'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Titlu necunoscut')
            formats = info.get('formats', [])
            resolutions = sorted(set(f"{f['height']}p" for f in formats if f.get('height') and f['height'] >= 480),
                                 reverse=True)
            return title, resolutions
    except Exception as e:
        messagebox.showerror("Eroare", f"Nu am putut obține informațiile video: {e}")
        return "", []


def update_video_info():
    url = url_entry.get()
    if not url or not is_valid_url(url):
        messagebox.showerror("Eroare", "Introduceți un link YouTube valid!")
        return

    title, quality_options = get_video_info(url)
    title_label.config(text=f"Titlu: {title}")

    if quality_options:
        quality_var.set(quality_options[0])
        quality_menu['menu'].delete(0, 'end')
        for quality in quality_options:
            quality_menu['menu'].add_command(label=quality, command=tk._setit(quality_var, quality))
    else:
        messagebox.showerror("Eroare", "Nu s-au găsit opțiuni de calitate!")


def download_video():
    url = url_entry.get()
    if not url or not is_valid_url(url):
        messagebox.showerror("Eroare", "Introduceți un link YouTube valid!")
        return

    save_path = filedialog.askdirectory()
    if not save_path:
        return

    update_video_info()
    selected_quality = quality_var.get()
    selected_format = format_var.get()

    ydl_opts = {
        'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
        'format': f'bestvideo[height={selected_quality[:-1]}]+bestaudio/best',
        'merge_output_format': selected_format
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            messagebox.showinfo("Succes", "Descărcare finalizată!")
    except Exception as e:
        messagebox.showerror("Eroare", f"A apărut o problemă: {e}")


def download_audio():
    url = url_entry.get()
    if not url or not is_valid_url(url):
        messagebox.showerror("Eroare", "Introduceți un link YouTube valid!")
        return

    save_path = filedialog.askdirectory()
    if not save_path:
        return

    ydl_opts = {
        'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '0',
        }]
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            messagebox.showinfo("Succes", "Descărcare audio finalizată!")
    except Exception as e:
        messagebox.showerror("Eroare", f"A apărut o problemă: {e}")


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
