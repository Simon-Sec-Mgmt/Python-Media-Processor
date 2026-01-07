import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import os
import subprocess
import threading
import sys

# --- CONFIGURATION DU DESIGN ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class YouTubeApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuration de la fenêtre principale
        self.title("YT-DLP ULTRA - V3")
        self.geometry("700x500")
        self.resizable(False, False)

        # -- LAYOUT --
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.main_frame = ctk.CTkFrame(self, corner_radius=20)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)

        # TITRE
        self.label_title = ctk.CTkLabel(self.main_frame, text="YOUTUBE CONVERTER", 
                                        font=("Roboto Medium", 24, "bold"), text_color="#3B8ED0")
        self.label_title.grid(row=0, column=0, pady=(30, 10))

        self.label_subtitle = ctk.CTkLabel(self.main_frame, text="Organisation par Album & Playlist", 
                                             font=("Roboto", 12), text_color="gray")
        self.label_subtitle.grid(row=1, column=0, pady=(0, 20))

        # ZONE URL
        self.entry_url = ctk.CTkEntry(self.main_frame, placeholder_text="Coller le lien Playlist ou Vidéo ici...", 
                                      width=400, height=40, corner_radius=10, border_width=2)
        self.entry_url.grid(row=2, column=0, pady=10)

        # ZONE FORMAT
        self.label_format = ctk.CTkLabel(self.main_frame, text="CHOISIR LE FORMAT", font=("Roboto", 12, "bold"))
        self.label_format.grid(row=3, column=0, pady=(20, 5))

        self.format_var = ctk.StringVar(value="MP3")
        self.seg_button = ctk.CTkSegmentedButton(self.main_frame, values=["MP3", "WAV", "MP4"], 
                                                 variable=self.format_var, width=200, dynamic_resizing=False)
        self.seg_button.grid(row=4, column=0, pady=10)

        # PROGRESS BAR
        self.progressbar = ctk.CTkProgressBar(self.main_frame, width=400, mode="indeterminate")
        self.progressbar.grid(row=5, column=0, pady=(30, 10))
        self.progressbar.set(0)

        # BOUTON
        self.btn_download = ctk.CTkButton(self.main_frame, text="LANCER LE TÉLÉCHARGEMENT", 
                                          command=self.lancer_thread, width=250, height=50, 
                                          corner_radius=25, font=("Roboto Medium", 14))
        self.btn_download.grid(row=6, column=0, pady=20)

        # STATUS
        self.label_status = ctk.CTkLabel(self.main_frame, text="Prêt.", text_color="gray")
        self.label_status.grid(row=7, column=0, pady=10)

    # --- LOGIQUE BACKEND ---

    def get_base_path(self, format_type):
        user_path = os.path.expanduser("~")
        # On retourne juste la racine (Music ou Videos)
        if format_type == 'MP4':
            return os.path.join(user_path, "Videos")
        else:
            return os.path.join(user_path, "Music")

    def run_yt_dlp(self, url, format_choisi):
        base_path = self.get_base_path(format_choisi)
        
        # On s'assure que le dossier racine existe
        if not os.path.exists(base_path):
             os.makedirs(base_path)

        # --- LOGIQUE INTELLIGENTE DES DOSSIERS ---
        # La syntaxe %(a|b|c)s dit à yt-dlp : "Essaie A, si vide essaie B, sinon prends C"
        
        if format_choisi == 'MP4':
            # Pour la vidéo : Priorité Nom Playlist -> Sinon "YouTube Videos"
            subfolder_template = "%(playlist_title|YouTube Videos)s"
        else:
            # Pour la musique : Priorité Playlist -> Album -> "YouTube Music"
            # Si yt-dlp trouve le nom de l'album, il créera le dossier automatiquement
            subfolder_template = "%(playlist_title|album|YouTube Music)s"

        # On construit le template final : C:\Users\...\Music \ [Album] \ [Titre].mp3
        output_template = os.path.join(base_path, subfolder_template, "%(title)s.%(ext)s")

        # Commande
        cmd = [sys.executable, "-m", "yt_dlp", "--no-keep-video", "-o", output_template]
        
        # Options de format
        if format_choisi == 'MP4':
             cmd.extend(["-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best", "--merge-output-format", "mp4"])
        elif format_choisi in ['MP3', 'WAV']:
            cmd.extend(["--extract-audio", "--audio-format", format_choisi.lower(), "--audio-quality", "0"])
        
        # Option pour télécharger toute la playlist si le lien en est une
        cmd.append("--yes-playlist")
        cmd.append(url)

        try:
            creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            subprocess.run(cmd, check=True, creationflags=creationflags)
            
            # Message de succès générique (car le dossier change selon la vidéo)
            self.after(0, lambda: self.finish_download(True, f"Téléchargement terminé !\nVérifiez vos dossiers dans : {base_path}"))
        except Exception as e:
            self.after(0, lambda: self.finish_download(False, str(e)))

    def lancer_thread(self):
        url = self.entry_url.get().strip()
        if not url:
            self.label_status.configure(text="Erreur : URL manquante !", text_color="#FF5555")
            return

        self.btn_download.configure(state="disabled", text="TRAITEMENT EN COURS...")
        self.progressbar.start()
        self.label_status.configure(text="Analyse de la Playlist/Vidéo...", text_color="#3B8ED0")

        format_choisi = self.format_var.get()
        t = threading.Thread(target=self.run_yt_dlp, args=(url, format_choisi))
        t.start()

    def finish_download(self, success, message):
        self.progressbar.stop()
        self.progressbar.set(0 if not success else 1)
        self.btn_download.configure(state="normal", text="LANCER LE TÉLÉCHARGEMENT")
        
        if success:
            self.label_status.configure(text="Succès !", text_color="#2CC985")
            messagebox.showinfo("Terminé", message)
        else:
            self.label_status.configure(text="Erreur", text_color="#FF5555")
            if "ffmpeg" in str(message).lower() or "return code 1" in str(message):
                 messagebox.showerror("Erreur", "Erreur lors de la conversion.\nVérifiez que FFmpeg est bien installé !")
            else:
                 messagebox.showerror("Erreur", message)

# --- LANCEMENT ---
if __name__ == "__main__":
    try:
        creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        subprocess.run([sys.executable, "-m", "yt_dlp", "--version"], capture_output=True, creationflags=creationflags)
    except FileNotFoundError:
        print("ERREUR CRITIQUE: yt-dlp n'est pas installé.")
    
    app = YouTubeApp()
    app.mainloop()