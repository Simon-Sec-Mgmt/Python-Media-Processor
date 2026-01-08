import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import os
import subprocess
import threading
import sys

# --- PALETTE NEUMORPHIC (LIGHT THEME) ---
# Le secret du Neumorphism c'est le faible contraste entre le fond et les éléments
COLORS = {
    "bg": "#E3E7F1",        # Gris bleuté très clair (Fond principal)
    "card": "#E3E7F1",      # Même couleur pour l'effet de fusion
    "text_main": "#3E4C59", # Gris foncé pour la lisibilité
    "text_sub": "#7D8CA3",  # Gris moyen pour les sous-titres
    "accent": "#6C5CE7",    # Violet/Bleu moderne pour l'action principale
    "accent_hover": "#5649C0",
    "white_shadow": "#FFFFFF",
    "dark_shadow": "#BEC5D5"
}

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("dark-blue") # On override les couleurs manuellement de toute façon

class NeumorphicCard(ctk.CTkFrame):
    """Un cadre personnalisé pour simuler une carte en relief"""
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLORS["card"], corner_radius=30, 
                         border_width=2, border_color=COLORS["white_shadow"], **kwargs)
        # L'effet d'ombre est simulé par la bordure blanche interne et le fond

class YouTubeApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- CONFIGURATION FENÊTRE ---
        self.title("XEKYEL CONVERTER // V4 NEURO")
        self.geometry("1000x700")
        self.configure(fg_color=COLORS["bg"])
        
        # Centrer la fenêtre au lancement ou maximiser selon l'OS
        if sys.platform == "win32":
            self.state("zoomed")
        
        # --- GRID LAYOUT ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- CONTENEUR CENTRAL (CARD) ---
        self.center_card = NeumorphicCard(self, width=600, height=500)
        self.center_card.grid(row=0, column=0, padx=40, pady=40)
        self.center_card.grid_propagate(False) # Force la taille fixe pour le look "Carte"
        
        # Grid interne de la carte
        self.center_card.grid_columnconfigure(0, weight=1)

        # --- ÉLÉMENTS UI ---
        self.create_widgets()

    def create_widgets(self):
        # 1. HEADER "3D"
        self.label_title = ctk.CTkLabel(
            self.center_card, 
            text="CONVERTISSEUR ULTRA", 
            font=("Montserrat", 32, "bold"), 
            text_color=COLORS["text_main"]
        )
        self.label_title.grid(row=0, column=0, pady=(50, 5))

        self.label_subtitle = ctk.CTkLabel(
            self.center_card, 
            text="Moteur yt-dlp intégré • Audio HD • Tri Intelligent", 
            font=("Roboto", 14), 
            text_color=COLORS["text_sub"]
        )
        self.label_subtitle.grid(row=1, column=0, pady=(0, 40))

        # 2. INPUT NEUMORPHIC
        # On utilise un cadre pour simuler l'effet "creusé" (inner shadow)
        self.input_frame = ctk.CTkFrame(self.center_card, fg_color="#D1D9E6", corner_radius=15, height=60)
        self.input_frame.grid(row=2, column=0, pady=10, padx=50, sticky="ew")
        self.input_frame.grid_propagate(False)

        self.entry_url = ctk.CTkEntry(
            self.input_frame, 
            placeholder_text="Coller le lien YouTube (Playlist ou Vidéo)...",
            placeholder_text_color=COLORS["text_sub"],
            text_color=COLORS["text_main"],
            fg_color="transparent", 
            border_width=0,
            font=("Roboto", 14),
            height=50
        )
        self.entry_url.pack(fill="both", expand=True, padx=20, pady=5)

        # 3. SÉLECTEUR DE FORMAT (Segmented Button)
        self.format_var = ctk.StringVar(value="MP3")
        self.seg_button = ctk.CTkSegmentedButton(
            self.center_card, 
            values=["MP3", "WAV", "MP4"], 
            variable=self.format_var,
            font=("Roboto", 13, "bold"),
            fg_color="#D1D9E6",             # Couleur fond désactivé
            selected_color=COLORS["accent"], # Couleur activée
            selected_hover_color=COLORS["accent_hover"],
            text_color=COLORS["text_sub"],
            corner_radius=20,
            height=40,
            dynamic_resizing=False,
            width=300
        )
        self.seg_button.grid(row=3, column=0, pady=25)

        # 4. PROGRESS BAR "LIQUIDE"
        self.progressbar = ctk.CTkProgressBar(
            self.center_card, 
            width=400, 
            height=15, 
            corner_radius=10,
            progress_color=COLORS["accent"],
            fg_color="#D1D9E6", # Fond creusé
            mode="indeterminate"
        )
        self.progressbar.grid(row=4, column=0, pady=(10, 20))
        self.progressbar.set(0)

        # 5. BOUTON ACTION PRINCIPAL
        self.btn_download = ctk.CTkButton(
            self.center_card, 
            text="LANCER L'EXTRACTION", 
            command=self.lancer_thread, 
            width=300, 
            height=55, 
            corner_radius=27, 
            font=("Montserrat", 15, "bold"),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            # Effet d'ombre portée subtile via border (hack)
            border_width=2,
            border_color="white" 
        )
        self.btn_download.grid(row=5, column=0, pady=20)

        # 6. STATUS
        self.label_status = ctk.CTkLabel(
            self.center_card, 
            text="Système prêt.", 
            font=("Roboto Medium", 12),
            text_color=COLORS["text_sub"]
        )
        self.label_status.grid(row=6, column=0, pady=10)

        # Footer Version
        self.label_ver = ctk.CTkLabel(self, text="XEKYEL LABS © 2026", text_color="#A0AEC0", font=("Arial", 10))
        self.label_ver.grid(row=1, column=0, pady=10)

    # --- LOGIQUE BACKEND (Inchangée mais optimisée) ---

    def get_base_path(self, format_type):
        user_path = os.path.expanduser("~")
        if format_type == 'MP4':
            return os.path.join(user_path, "Videos")
        else:
            return os.path.join(user_path, "Music")

    def run_yt_dlp(self, url, format_choisi):
        base_path = self.get_base_path(format_choisi)
        if not os.path.exists(base_path): os.makedirs(base_path)

        if format_choisi == 'MP4':
            subfolder_template = "%(playlist_title|YouTube Videos)s"
        else:
            subfolder_template = "%(playlist_title|album|YouTube Music)s"

        output_template = os.path.join(base_path, subfolder_template, "%(title)s.%(ext)s")
        cmd = [sys.executable, "-m", "yt_dlp", "--no-keep-video", "-o", output_template]
        
        if format_choisi == 'MP4':
             cmd.extend(["-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best", "--merge-output-format", "mp4"])
        elif format_choisi in ['MP3', 'WAV']:
            cmd.extend(["--extract-audio", "--audio-format", format_choisi.lower(), "--audio-quality", "0"])
        
        cmd.append("--yes-playlist")
        cmd.append(url)

        try:
            # Flags pour cacher la console noire sous Windows
            creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            subprocess.run(cmd, check=True, creationflags=creationflags)
            self.after(0, lambda: self.finish_download(True, f"Fichiers sauvegardés dans :\n{base_path}"))
        except Exception as e:
            self.after(0, lambda: self.finish_download(False, str(e)))

    def lancer_thread(self):
        url = self.entry_url.get().strip()
        if not url:
            self.shake_animation() # Petit effet visuel si erreur
            self.label_status.configure(text="Erreur : Veuillez entrer un lien valide.", text_color="#FF6B6B")
            return

        self.btn_download.configure(state="disabled", text="TRAITEMENT EN COURS...")
        self.progressbar.start()
        self.label_status.configure(text="Analyse du flux distant...", text_color=COLORS["accent"])

        format_choisi = self.format_var.get()
        t = threading.Thread(target=self.run_yt_dlp, args=(url, format_choisi))
        t.start()

    def finish_download(self, success, message):
        self.progressbar.stop()
        self.progressbar.set(0 if not success else 1)
        self.btn_download.configure(state="normal", text="LANCER L'EXTRACTION")
        
        if success:
            self.label_status.configure(text="Terminé avec succès.", text_color="#20BF6B")
            messagebox.showinfo("Succès", message)
        else:
            self.label_status.configure(text="Échec de l'opération.", text_color="#FF6B6B")
            if "ffmpeg" in str(message).lower():
                 messagebox.showerror("Erreur Système", "FFmpeg manquant.\nInstallez FFmpeg pour la conversion audio.")
            else:
                 messagebox.showerror("Erreur", message)

    def shake_animation(self):
        # Petite animation si l'input est vide (déplace la carte un peu)
        x = self.center_card.winfo_x()
        for i in range(2):
            self.center_card.place(x=x+5)
            self.update()
            self.after(50)
            self.center_card.place(x=x-5)
            self.update()
            self.after(50)
        # Remet la grid (place casse la grid parfois, donc on re-grid propre)
        self.center_card.grid(row=0, column=0, padx=40, pady=40)

if __name__ == "__main__":
    try:
        creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        subprocess.run([sys.executable, "-m", "yt_dlp", "--version"], capture_output=True, creationflags=creationflags)
    except FileNotFoundError:
        print("ERREUR CRITIQUE: 'pip install yt-dlp' requis.")
    
    app = YouTubeApp()
    app.mainloop()
