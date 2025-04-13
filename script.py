import tkinter as tk
from tkinter import filedialog, messagebox
import yt_dlp
import os


def get_video_options(url):
    """Obține lista de opțiuni de calitate disponibile (minim 480p)"""
    try:
        ydl_opts = {'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            resolutions = sorted(set(f"{f['height']}p" for f in formats if f.get('height') and f['height'] >= 480),
                                 reverse=True)
            return resolutions
    except Exception as e:
        messagebox.showerror("Eroare", f"Nu am putut obține opțiunile video: {e}")
        return []


def update_quality_options():
    """Actualizează meniul drop-down cu opțiunile de calitate disponibile"""
    url = url_entry.get()
    if not url:
        messagebox.showerror("Eroare", "Introduceți un link valid!")
        return

    quality_options = get_video_options(url)
    if quality_options:
        quality_var.set(quality_options[0])  # Selectează cea mai mare rezoluție
        quality_menu['menu'].delete(0, 'end')
        for quality in quality_options:
            quality_menu['menu'].add_command(label=quality, command=tk._setit(quality_var, quality))
    else:
        messagebox.showerror("Eroare", "Nu s-au găsit opțiuni de calitate!")


def download_video():
    """Descarcă videoclipul cu sunet la calitate maximă"""
    url = url_entry.get()
    if not url:
        messagebox.showerror("Eroare", "Introduceți un link valid!")
        return

    save_path = filedialog.askdirectory()
    if not save_path:
        return

    selected_quality = quality_var.get()
    selected_format = format_var.get()

    # Alegem formatul corect (MP4 doar dacă e disponibil H.264)
    format_filter = "mp4" if selected_format == "mp4" else "mkv"

    try:
        ydl_opts = {
            'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
            'format': f'bestvideo[height={selected_quality[:-1]}]+bestaudio/best',
            'merge_output_format': selected_format
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            messagebox.showinfo("Descărcare", f"Descărcarea a început... ({selected_format})")
            info = ydl.extract_info(url, download=True)

            # Dacă nu a putut descărca MP4, oferă o alternativă MKV
            if selected_format == "mp4" and info['ext'] != "mp4":
                messagebox.showwarning("Avertisment",
                                       "Formatul MP4 nu este disponibil la această rezoluție. Se descarcă MKV.")
                selected_format = "mkv"
                ydl_opts['merge_output_format'] = "mkv"
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

            messagebox.showinfo("Succes", f"Descărcare finalizată!\nRezoluție: {info['height']}p ({selected_format})")
    except Exception as e:
        messagebox.showerror("Eroare", f"A apărut o problemă: {e}")


def download_audio():
    """Descarcă doar audio, la calitate maximă"""
    url = url_entry.get()
    if not url:
        messagebox.showerror("Eroare", "Introduceți un link valid!")
        return

    save_path = filedialog.askdirectory()
    if not save_path:
        return

    try:
        ydl_opts = {
            'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
            'format': 'bestaudio/best',  # Selectează cea mai bună calitate posibilă
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'opus',  # Format superior MP3
                'preferredquality': '0',  # Calitate maximă
            }],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            messagebox.showinfo("Descărcare", "Descărcarea a început...")
            ydl.download([url])
            messagebox.showinfo("Succes", "Descărcarea audio la calitate maximă a fost finalizată!")
    except Exception as e:
        messagebox.showerror("Eroare", f"A apărut o problemă: {e}")


# Creare interfață grafică
root = tk.Tk()
root.title("YouTube Downloader")
root.geometry("450x350")

tk.Label(root, text="Introduceți link-ul YouTube:").pack(pady=5)
url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=5)

tk.Button(root, text="Verifică opțiuni video", command=update_quality_options).pack(pady=5)

# Meniu pentru alegerea calității video
quality_var = tk.StringVar(root)
quality_var.set("Selectează calitatea")
quality_menu = tk.OptionMenu(root, quality_var, "")
quality_menu.pack(pady=5)

# Meniu pentru alegerea formatului video
format_var = tk.StringVar(root)
format_var.set("mp4")  # Format implicit
tk.Label(root, text="Alege formatul video:").pack(pady=5)
format_menu = tk.OptionMenu(root, format_var, "mp4", "mkv")
format_menu.pack(pady=5)

tk.Button(root, text="Descarcă Video", command=download_video).pack(pady=5)
tk.Button(root, text="Descarcă Audio (calitate maximă)", command=download_audio).pack(pady=5)
tk.Button(root, text="Ieșire", command=root.quit).pack(pady=5)

root.mainloop()
