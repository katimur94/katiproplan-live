import customtkinter as ctk
import tkinter as tk 
import sys
from tkinter import messagebox, filedialog, ttk
import threading
import os
import shutil
import datetime
import glob
import re
import subprocess
import webbrowser
import json

# Eigene Module
from config import ConfigManager, THEMES
from backend_swarm import SwarmConnector
from file_manager import LocalFileManager

class ModernGauge(ctk.CTkCanvas):
    # 1. Hier "ring_color" als Parameter ergänzen:
    def __init__(self, master, width=250, height=250, title="", value=0, unit="", 
                 accent_color="#00ff66", text_color="#fff", card_color="#222", 
                 ring_color="#333", **kwargs): # <--- NEU!
        
        super().__init__(master, width=width, height=height, bg=card_color, highlightthickness=0, **kwargs)
        self.width = width
        self.height = height
        self.title = title
        self.value = value
        self.unit = unit
        self.accent_color = accent_color
        self.text_color = text_color
        self.card_color = card_color
        self.ring_color = ring_color # <--- WICHTIG: Farbe speichern
        
        self.arc_width = 20
        self.radius = (min(width, height) / 2) - 30
        self.cx = width / 2
        self.cy = height / 2
        
        self.draw()

    def update_colors(self, accent, text, card, ring): # <--- Auch hier 'ring' dazu
        self.accent_color = accent
        self.text_color = text
        self.card_color = card
        self.ring_color = ring # <--- Update
        self.configure(bg=card)
        self.draw()

    def set_value(self, new_val):
        self.value = new_val
        self.draw()

    def draw(self):
        self.delete("all")
        # Hintergrund Kreis - HIER WAR DER FEHLER (Hardcoded Color)
        # Jetzt nutzen wir self.ring_color statt "#2b2b2b"
        self.create_oval(self.cx - self.radius, self.cy - self.radius,
                         self.cx + self.radius, self.cy + self.radius,
                         outline=self.ring_color, width=self.arc_width) # <--- Dynamische Farbe!
        
        # Fortschritt
        max_visual = 2000 if "Stutzen" in self.title else 50
        pct = min(self.value / max_visual, 1.0)
        extent = -359.9 * pct 
        if self.value > 0:
            self.create_arc(self.cx - self.radius, self.cy - self.radius,
                            self.cx + self.radius, self.cy + self.radius,
                            start=90, extent=extent, style="arc", outline=self.accent_color, width=self.arc_width)
        # Text
        self.create_text(self.cx, self.cy - 15, text=str(self.value), fill=self.text_color, font=("Impact", 48))
        self.create_text(self.cx, self.cy + 35, text=self.unit, fill="gray", font=("Arial", 14, "bold"))
        self.create_text(self.cx, self.height - 25, text=self.title.upper(), fill="#888", font=("Consolas", 11, "bold"))

class DiTomApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.cfg = ConfigManager()
        self.swarm = SwarmConnector(self.cfg)
        self.file_mgr = LocalFileManager(self.cfg)
        self.colors = self.cfg.get_colors()

        self.active_project = {"nr": "", "city": "", "path": None}
        self.local_structure = {} 
        self.ghost_cache = {}     
        self.current_street = ""
        self.current_haltung = ""
        self.current_folder_path = None
        self.tachos = [] 
        self.cached_city_list = [] 

        self.title(f"DiTom Site Manager v51 - {self.cfg.data['system_name']}")
        # 1. Gespeicherte Größe/Position laden (oder Standard nehmen)
        saved_geo = self.cfg.data.get("window_geometry", "1400x950")
        self.geometry(saved_geo)
        
        # 2. Das "X" oben rechts abfangen, um zu speichern
        self.protocol("WM_DELETE_WINDOW", self.on_close_app)
        # --------------------------------------------------
        
        ctk.set_appearance_mode("Dark")
        self.configure(fg_color=self.colors["bg"])

        if os.path.exists("roboter.ico"):
            try: self.iconbitmap("roboter.ico")
            except: pass 

        self.setup_ui()
        self.after(1000, lambda: threading.Thread(target=self.preload_cloud_data, daemon=True).start())

    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # SIDEBAR
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color=self.colors["card"])
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        # Logo Bereich
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(pady=(40, 20))
        
        # 1. Großes Icon (Optional, wirkt aber mächtig)
        # Wenn du kein Bild laden willst, nimm ein Emoji in RIESIG:
        ctk.CTkLabel(logo_frame, text="🤖", font=("Segoe UI Emoji", 84)).pack(pady=(0, 10))

        # 2. Titel (Noch etwas größer)
        ctk.CTkLabel(logo_frame, text="DITOM", font=("Impact", 65), 
                     text_color=self.colors["accent"]).pack()
        
        # 3. Akzent-Linie (Macht es professionell)
        ctk.CTkFrame(logo_frame, height=3, width=120, fg_color=self.colors["border"]).pack(pady=8)

        # 4. Untertitel mit "Letter Spacing" (Leerzeichen zwischen Buchstaben)
        # Das lässt es wie ein teures Design wirken
        spaced_text = "S  I  T  E     M  A  N  A  G  E  R"
        ctk.CTkLabel(logo_frame, text=spaced_text, 
                     font=("Arial", 15, "bold"), 
                     text_color=self.colors["text_dim"]).pack()
        
        ctk.CTkFrame(self.sidebar, height=2, fg_color=self.colors["border"]).pack(fill="x", padx=20, pady=20)
        self.create_nav_btn("📊 DASHBOARD", self.show_dashboard)
        self.create_nav_btn("🛠 BEARBEITUNG", self.show_work)
        self.create_nav_btn("🌍 CLOUD SYNC", self.show_sync_dialog)
        self.create_nav_btn("⚙️ Config", self.open_settings)
        
        # Copyright Label ganz unten in der Sidebar
        ctk.CTkLabel(self.sidebar, 
                     text="© 2026 Timur Kalayci", 
                     text_color=self.colors["text_dim"], # <--- Passt sich jetzt dem Theme an!
                     font=("Arial", 14)                  # Optional: Schrift etwas kleiner/feiner
                     ).pack(side="bottom", pady=20)

        # MAIN AREA
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.show_dashboard()

    def create_nav_btn(self, text, command):
        btn = ctk.CTkButton(self.sidebar, text=text, command=command, fg_color="transparent", 
                            text_color=self.colors["text"], 
                            hover_color=self.colors["accent"], # <--- Nimmt die Randfarbe (dezent)
                            # ODER wenn es knallen soll: hover_color=self.colors["accent"],
                            anchor="w", height=50, font=("Consolas", 21, "bold"))
        btn.pack(fill="x", pady=5, padx=10)

    def clear_main(self):
        self.tachos = [] 
        for w in self.main_frame.winfo_children(): w.destroy()

    # --- DASHBOARD (Aus main2.py) ---
    def show_dashboard(self):
        self.clear_main()
        
        # Stats Cockpit
        stats_frame = ctk.CTkFrame(self.main_frame, fg_color=self.colors["card"], corner_radius=15)
        stats_frame.pack(fill="x", pady=(0, 20))

        top_bar = ctk.CTkFrame(stats_frame, fg_color="transparent")
        top_bar.pack(fill="x", padx=30, pady=20)
        ctk.CTkLabel(top_bar, text="PERFORMANCE ÜBERSICHT", font=("Arial", 14, "bold"), text_color=self.colors["text_dim"]).pack(side="left")
        
        right_area = ctk.CTkFrame(top_bar, fg_color="transparent"); right_area.pack(side="right")
        ctk.CTkButton(right_area, text="🗺️ KARTE ÖFFNEN", command=self.action_open_map, width=160, height=35, 
                      fg_color=self.colors["border"],       # <--- Farbe wenn inaktiv
                      hover_color=self.colors["accent"]).pack(side="left", padx=(0, 15)) # <--- Farbe bei Maus-Trigger

        years = set()
        raw_data = self.file_mgr.scan_local_projects()
        for p in raw_data.values():
            try: years.add(p["last_date"].split("-")[0])
            except: pass
        year_list = sorted(list(years), reverse=True)
        combo_vals = ["Gesamt (Alles)", f"Dieses Jahr ({datetime.datetime.now().year})"] + year_list
        
        # --- FIX: Styling für den Jahres-Filter ---
        combo_style = {
            "fg_color": self.colors["card"],       # Kachel-Farbe (nicht bg)
            "border_color": self.colors["border"], # Passender Rand
            "button_color": self.colors["border"], # Farbe des Pfeil-Buttons
            "button_hover_color": self.colors["accent"], # Leuchtet bei Maus-Hover
            "dropdown_fg_color": self.colors["card"],    # Farbe der aufgeklappten Liste
            "dropdown_hover_color": self.colors["accent"], # Auswahl-Farbe in der Liste
            "dropdown_text_color": self.colors["text"],
            "text_color": self.colors["text"]
        }

        self.combo_stats = ctk.CTkComboBox(right_area, values=combo_vals, width=220, height=35, 
                                           command=self.update_cockpit, **combo_style) # <--- Styles anwenden
        
        self.combo_stats.set(f"Dieses Jahr ({datetime.datetime.now().year})")
        self.combo_stats.pack(side="left")

        # --- TACHO AREA MIT NAMEN IN DER MITTE ---
        tacho_area = ctk.CTkFrame(stats_frame, fg_color="transparent")
        tacho_area.pack(fill="x", pady=(10, 30), padx=20)
        
        # Wir machen 3 Spalten: Links Tacho, Mitte Name, Rechts Tacho
        tacho_area.grid_columnconfigure(0, weight=1) # Platz links
        tacho_area.grid_columnconfigure(1, weight=0) # Platz Mitte (nur so breit wie nötig)
        tacho_area.grid_columnconfigure(2, weight=1) # Platz rechts

        # 1. Linker Tacho (Spalte 0)
        self.g_stutzen = ModernGauge(
            tacho_area, 
            title="SANIERT (STUTZEN)", 
            unit="Stück", 
            accent_color=self.colors["accent"], 
            text_color=self.colors["text"], 
            card_color=self.colors["card"], 
            ring_color=self.colors["border"]
        )
        self.g_stutzen.grid(row=0, column=0)
        self.tachos.append(self.g_stutzen)

        # 2. Der coole Name in der Mitte (Spalte 1)
        name_frame = ctk.CTkFrame(tacho_area, fg_color="transparent")
        name_frame.grid(row=0, column=1, padx=40) # Abstand zu den Tachos
        
        # Kleines Label "OPERATOR / SYSTEM"
        ctk.CTkLabel(name_frame, text="OPERATOR", 
                     font=("Consolas", 22, "bold"), 
                     text_color=self.colors["text_dim"]).pack(pady=(0, 5))
        
        # Der eigentliche Name (RIESIG und in Theme-Farbe)
        sys_name = self.cfg.data.get("system_name", "ROBOTER").upper()
        ctk.CTkLabel(name_frame, text=sys_name, 
                     font=("Impact", 72),       # Schön dicke Schrift
                     text_color=self.colors["accent"]).pack() # Leuchtet in deiner Farbe
        
        # Kleiner "ONLINE" Indikator
        self.lbl_status = ctk.CTkLabel(name_frame, text="● PRÜFE...", 
                                       font=("Arial", 16, "bold"), 
                                       text_color="gray")
        self.lbl_status.pack(pady=(5,0))

        # Startet den Check im Hintergrund (stürzt nicht ab, wenn GUI hängt)
        threading.Thread(target=self.loop_internet_check, daemon=True).start()

        # 3. Rechter Tacho (Spalte 2)
        self.g_projects = ModernGauge(
            tacho_area, 
            title="PROJEKTE GEFAHREN", 
            unit="Baustellen", 
            accent_color=self.colors["accent"], # Nimmt jetzt auch Theme-Farbe!
            text_color=self.colors["text"], 
            card_color=self.colors["card"], 
            ring_color=self.colors["border"]
        )
        self.g_projects.grid(row=0, column=2)
        self.tachos.append(self.g_projects)

        # Neues Projekt
        box = ctk.CTkFrame(self.main_frame, fg_color=self.colors["card"], corner_radius=10)
        box.pack(fill="x", pady=(0, 20), padx=0)
        header = ctk.CTkFrame(box, fg_color="transparent"); header.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(header, text="NEUE AUFGABE STARTEN", font=("Arial", 14, "bold"), text_color=self.colors["accent"]).pack(side="left")
        
        row = ctk.CTkFrame(box, fg_color="transparent"); row.pack(pady=(0, 20), padx=20, fill="x")
# In show_dashboard:
        self.entry_nr = ctk.CTkEntry(row, placeholder_text="Projekt Nr.", width=120, height=40,
                                     fg_color=self.colors["card"],      # <--- Theme Farbe
                                     border_color=self.colors["border"], # <--- Theme Rand
                                     text_color=self.colors["text"])     # <--- Theme Text
        self.entry_nr.pack(side="left", padx=(0, 10))
        
        self.entry_city = ctk.CTkEntry(row, placeholder_text="Stadt / Ort", width=250, height=40,
                                       fg_color=self.colors["card"],      # <--- Theme Farbe
                                       border_color=self.colors["border"],
                                       text_color=self.colors["text"])
        self.entry_city.pack(side="left", padx=(0, 10))
        ctk.CTkButton(row, text="AUSFÜHREN ▶", command=self.start_project, height=40, width=150, fg_color=self.colors["accent"], text_color=self.colors["bg"]).pack(side="left")

        # Tabs
        self.tab_view = ctk.CTkTabview(self.main_frame, fg_color="transparent",
                                       segmented_button_fg_color=self.colors["bg"],           # Hintergrund der Leiste
                                       segmented_button_selected_color=self.colors["accent"], # Aktiver Tab
                                       segmented_button_unselected_color=self.colors["card"], # Inaktiver Tab
                                       text_color=self.colors["text"])                        # Textfarbe
        self.tab_view.pack(fill="both", expand=True)

        # --- HIER IST DER TRICK FÜR GRÖSSERE TABS ---
        # 1. Schrift vergrößern (Macht die Tabs automatisch breiter)
        self.tab_view._segmented_button.configure(font=("Segoe UI Emoji", 20, "bold"))
        
        # 2. Höhe der Leiste manuell setzen (Standard ist ca. 30)
        self.tab_view._segmented_button.configure(height=45) 
        # --------------------------------------------

        self.setup_local_tree(self.tab_view.add("📂LOKAL📂"))
        self.setup_cloud_tree(self.tab_view.add("☁CLOUD☁"))
        
        self.update_cockpit()


    def loop_internet_check(self):
        import socket
        import time
        
        # Warten wir kurz beim Start, damit das GUI sicher geladen ist
        time.sleep(1)

        # Endlosschleife (läuft im Hintergrund weiter)
        while True:
            online = False
            try:
                # Versuche Google DNS zu erreichen (Port 53) - Timeout nach 3 Sek
                socket.create_connection(("8.8.8.8", 53), timeout=3)
                online = True
            except:
                online = False
            
            # GUI Update (Nur wenn das Label auch existiert!)
            # Das ist wichtig, falls du gerade im "Bearbeiten"-Tab bist
            try:
                if hasattr(self, "lbl_status") and self.lbl_status.winfo_exists():
                    if online:
                        self.lbl_status.configure(text="● ONLINE", text_color="#00ff66") # Hellgrün
                    else:
                        self.lbl_status.configure(text="● OFFLINE", text_color="#ff5555") # Hellrot
                else:
                    # Wenn wir nicht im Dashboard sind, hören wir auf zu prüfen (spart Ressourcen)
                    # Oder wir lassen es laufen, falls du zurückkehrst. 
                    # Hier brechen wir ab, da show_dashboard den Thread eh neu startet.
                    break 
            except:
                break
                
            time.sleep(30) # 30 Sekunden Pause
            
    def update_cockpit(self, _=None):
        selection = self.combo_stats.get()
        target_year = None
        if "Dieses Jahr" in selection: target_year = str(datetime.datetime.now().year)
        elif "Gesamt" in selection: target_year = None
        else: target_year = selection

        def calc():
            total_stutzen = 0; total_projects = 0; city_set = set()
            raw_data = self.file_mgr.scan_local_projects()
            regex_stutzen = re.compile(r"^\d+[,.]\d+m\s+Stutzen", re.IGNORECASE)

            for proj_name, info in raw_data.items():
                proj_counted = False
                city_name = proj_name.split(" ", 1)[1] if " " in proj_name else ""
                
                for path_entry in info["paths"]:
                    if target_year and path_entry["date"].split("-")[0] != target_year: continue
                    proj_counted = True
                    p_path = path_entry["path"]
                    if os.path.exists(p_path):
                        try:
                            for s in os.listdir(p_path):
                                s_path = os.path.join(p_path, s)
                                if os.path.isdir(s_path):
                                    for h in os.listdir(s_path):
                                        h_path = os.path.join(s_path, h)
                                        if os.path.isdir(h_path):
                                            for dmg in os.listdir(h_path):
                                                if os.path.isdir(os.path.join(h_path, dmg)) and regex_stutzen.match(dmg):
                                                    total_stutzen += 1
                        except: pass
                if proj_counted: 
                    total_projects += 1
                    if city_name: city_set.add(city_name)

            self.cached_city_list = list(city_set)
            self.after(0, lambda: self.g_stutzen.set_value(total_stutzen))
            self.after(0, lambda: self.g_projects.set_value(total_projects))
        threading.Thread(target=calc, daemon=True).start()


    def action_open_map(self):
        if not self.cached_city_list:
            messagebox.showinfo("Karte", "Keine Städte im Filter gefunden.")
            return
        
        cities_js = json.dumps(self.cached_city_list)
        c = self.colors 
        
        # --- HIER IST DAS UPGRADE: GOOGLE SATELLIT ---
        # Wir nutzen 'lyrs=y' -> Das bedeutet "Hybrid" (Satellit + Straßennamen)
        # 'hl=de' -> Deutsche Beschriftung
        tile_url = "https://mt0.google.com/vt/lyrs=y&hl=de&x={x}&y={y}&z={z}"
        
        html = f"""<!DOCTYPE html>
        <html>
        <head>
            <title>DiTom Satellite Map</title>
            <meta charset="utf-8"/>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css"/>
            <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
            <style>
                body{{margin:0;padding:0;background:{c['bg']}}}
                #map{{width:100%;height:100vh;background:{c['bg']}}}
                
                /* Design für die Popups (Sprechblasen) */
                .leaflet-popup-content-wrapper {{
                    background: {c['card']};
                    color: {c['text']};
                    border-left: 5px solid {c['accent']}; /* Schicker Farbbalken links */
                    border-radius: 4px;
                }}
                .leaflet-popup-tip {{ background: {c['card']}; }}
                .leaflet-popup-content {{ margin: 10px; font-family: 'Segoe UI', sans-serif; }}
            </style>
        </head>
        <body>
            <div id="map"></div>
            <script>
                // Startpunkt: Mitte Deutschland, Zoom etwas näher
                var map = L.map('map').setView([51.1657, 10.4515], 6);
                
                // --- GOOGLE SATELLITE LAYER ---
                L.tileLayer('{tile_url}', {{
                    maxZoom: 20,
                    attribution: '© Google Maps'
                }}).addTo(map);

                var cities = {cities_js};

                async function plot() {{
                    for(const city of cities) {{
                        try {{
                            // Wir fragen Nominatim nach Koordinaten
                            let r = await fetch(`https://nominatim.openstreetmap.org/search?city=${{city}}&country=Germany&format=json`);
                            let d = await r.json();
                            
                            if(d && d.length > 0) {{
                                // Marker setzen
                                L.marker([d[0].lat, d[0].lon]).addTo(map)
                                .bindPopup(`
                                    <div style="min-width: 120px;">
                                        <b style="font-size: 14px; color: {c['accent']}">${{city}}</b><br>
                                        <span style="font-size: 11px; color: {c['text_dim']}">📍 Projektstandort</span>
                                    </div>
                                `);
                            }}
                        }} catch(e) {{ console.log(e); }}
                        
                        // Kurze Pause um die API nicht zu überlasten
                        await new Promise(r => setTimeout(r, 600)); 
                    }}
                }}
                plot();
            </script>
        </body>
        </html>"""
        
        # Datei schreiben und öffnen
        with open("map_view.html", "w", encoding="utf-8") as f: 
            f.write(html)
        webbrowser.open("file://" + os.path.abspath("map_view.html"))

    # --- TREEVIEW LOCAL ---
    def setup_local_tree(self, parent):
        search_frame = ctk.CTkFrame(parent, fg_color="transparent"); search_frame.pack(fill="x", pady=(0, 10))
        self.entry_search = ctk.CTkEntry(search_frame, placeholder_text="Suche...",
                                         fg_color=self.colors["card"],       # Nimmt die Kachel-Farbe
                                         border_color=self.colors["border"], # Nimmt die Rand-Farbe
                                         text_color=self.colors["text"])     # Nimmt die Text-Farbe
        # -----------------------------

        self.entry_search.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry_search.bind("<Return>", lambda e: self.perform_search()) 
        # Such-Button (Lupe)
        ctk.CTkButton(search_frame, text="🔍", width=50, command=self.perform_search,
                      fg_color=self.colors["border"],      # Grundfarbe: Rahmenfarbe (dezent)
                      text_color=self.colors["text"],      # Textfarbe
                      hover_color=self.colors["accent"]    # Hover: Leuchtet in Theme-Farbe
                      ).pack(side="right")

        # Reset-Button (X)
        ctk.CTkButton(search_frame, text="✖", width=40, command=self.reset_search,
                      fg_color=self.colors["card"],        # Grundfarbe: Kachelfarbe (unsichtbar)
                      text_color=self.colors["text"],
                      hover_color=self.colors["error"]     # Hover: Wird Rot (Löschen-Signal)
                      ).pack(side="right", padx=(5,0))

        tree_frame = ctk.CTkFrame(parent, fg_color="transparent"); tree_frame.pack(fill="both", expand=True)
        self.setup_tree_style()
        self.tree = ttk.Treeview(tree_frame, columns=("path", "type"), show="tree", selectmode="browse")
        
        # --- HIER EINFÜGEN: SPALTEN VERSTECKEN ---
        # "path" wird 0 Pixel breit -> Unsichtbar, aber Daten sind noch da!
        self.tree.column("path", width=0, stretch=False)
        self.tree.column("type", width=0, stretch=False) # "type" verstecken wir am besten auch
        # -----------------------------------------
        
        # 2. Hauptspalte (#0) konfigurieren (Das ist die Ordner-Struktur)
        self.tree.heading("#0", text="Lokale Daten", anchor="w"); self.tree.column("#0", stretch=True, width=400)
        
        # 3. Scrollbar und Rest
        sb = ctk.CTkScrollbar(tree_frame, orientation="vertical", command=self.tree.yview); self.tree.configure(yscroll=sb.set)
        self.tree.pack(side="left", fill="both", expand=True); sb.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewOpen>>", self.on_tree_expand); self.tree.bind("<Button-3>", self.show_context_menu)    
        
        self.context_menu = tk.Menu(self, tearoff=0, 
                                    bg=self.colors["card"],        # Hintergrund passend zur Kachel
                                    fg=self.colors["text"],        # Textfarbe
                                    activebackground=self.colors["accent"], # Hover-Hintergrund (Leuchtet!)
                                    activeforeground=self.colors["bg"],     # Hover-Text (Dunkel für Kontrast)
                                    font=("Consolas", 16, "bold"), # Passende Schriftart
                                    relief="flat",                 # Flacher Look
                                    bd=0)                          # Kein hässlicher 3D-Rand
        
        self.context_menu.add_command(label="🚀 HIER ARBEITEN", command=self.ctx_continue_work)
        self.context_menu.add_command(label="📂 Im Explorer öffnen", command=self.ctx_open_explorer)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="✏️ Umbenennen", command=self.ctx_rename) 
        self.context_menu.add_command(label="🗑️ Löschen", command=self.ctx_delete)

        self.populate_tree_smart_years()

    # --- TREEVIEW CLOUD ---
    def setup_cloud_tree(self, parent):
        # --- FIX: Button Style ---
        ctk.CTkButton(parent, text="🔄 CLOUD DATEN LADEN", command=self.reload_cloud_tree_data, height=30,
                      fg_color=self.colors["border"],      # Dezent im Normalzustand
                      text_color=self.colors["text"],      # Text passend zum Theme
                      hover_color=self.colors["accent"]    # Leuchtet in Theme-Farbe beim Hover
                      ).pack(fill="x", pady=(0,10))
        
        tree_frame = ctk.CTkFrame(parent, fg_color="transparent"); tree_frame.pack(fill="both", expand=True)
        
        self.tree_cloud = ttk.Treeview(tree_frame, columns=("info", "type"), show="tree", selectmode="browse")
        self.tree_cloud.heading("#0", text="Cloud Daten", anchor="w"); self.tree_cloud.column("#0", stretch=True, width=400)
        
        sb = ctk.CTkScrollbar(tree_frame, orientation="vertical", command=self.tree_cloud.yview); self.tree_cloud.configure(yscroll=sb.set)
        self.tree_cloud.pack(side="left", fill="both", expand=True); sb.pack(side="right", fill="y")
        self.tree_cloud.bind("<Double-1>", self.on_cloud_double_click)
        
        if self.swarm.last_world_state: self.populate_cloud_tree()

    def setup_tree_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        # --- EINSTELLUNGEN FÜR GRÖSSE ---
        # Ändere diese zwei Werte, wenn es noch größer sein soll:
        SCHRIFT_GROESSE = 16   # Vorher: 12
        ZEILEN_HOEHE = 40      # Vorher: Standard (ca. 20). WICHTIG damit nichts verrutscht!
        # --------------------------------

        # Farben laden
        bg = self.colors["bg"]
        card = self.colors["card"]
        fg = self.colors["text"]
        sel_bg = self.colors["accent"]
        sel_fg = self.colors["bg"]
        
        # 1. Haupt-Style für den Inhalt
        style.configure("Treeview", 
                        background=card, 
                        foreground=fg, 
                        fieldbackground=card, 
                        borderwidth=0, 
                        font=("Consolas", SCHRIFT_GROESSE), # <--- Größere Schrift
                        rowheight=ZEILEN_HOEHE)             # <--- WICHTIG: Platz pro Zeile
        
        style.map("Treeview", background=[('selected', sel_bg)], foreground=[('selected', sel_fg)])
        
        # 2. Style für die Überschriften (Header)
        style.configure("Treeview.Heading", 
                        background=self.colors["border"], 
                        foreground=self.colors["text"], 
                        font=("Arial", SCHRIFT_GROESSE, "bold"), # Auch Header größer machen
                        relief="flat")
        
        style.map("Treeview.Heading", background=[('active', self.colors["accent"])])

    # --- TREE LOGIC ---
    def perform_search(self): self.populate_tree_smart_years(filter_term=self.entry_search.get().strip())
    def reset_search(self): self.entry_search.delete(0, 'end'); self.populate_tree_smart_years()
    def check_path_match(self, path, term):
        if not term: return True
        t = term.lower(); 
        if t in path.lower(): return True
        try:
            for item in os.listdir(path):
                if t in item.lower(): return True
                if os.path.isdir(os.path.join(path, item)):
                    for s in os.listdir(os.path.join(path, item)): 
                        if t in s.lower(): return True
        except: pass
        return False
    
    def populate_tree_smart_years(self, filter_term=""):
        self.tree.delete(*self.tree.get_children())
        raw_data = self.file_mgr.scan_local_projects()
        years_map = {}; filter_mode = len(filter_term) > 0; term = filter_term.lower()
        for proj_name, info in raw_data.items():
            last_date = info["last_date"]; year = last_date.split("-")[0] if "-" in last_date else "Unbekannt"
            if year not in years_map: years_map[year] = []
            valid_paths = []
            for p in info["paths"]:
                if not filter_mode: valid_paths.append(p)
                else:
                    if term in proj_name.lower() or term in p["date"] or self.check_path_match(p["path"], term): valid_paths.append(p)
            if valid_paths: years_map[year].append((proj_name, valid_paths))
        for year in sorted(years_map.keys(), reverse=True):
            y_open = filter_mode or (not filter_mode and year == str(datetime.datetime.now().year))
            y_id = self.tree.insert("", "end", text=f"📅 {year}", values=("", "year"), open=y_open)
            sorted_projs = sorted(years_map[year], key=lambda x: max([d['date'] for d in x[1]]), reverse=True)
            for proj_name, paths in sorted_projs:
                p_id = self.tree.insert(y_id, "end", text=f"📂 {proj_name}", values=("", "project"), open=filter_mode)
                for p in sorted(paths, key=lambda x: x["date"], reverse=True):
                    d_id = self.tree.insert(p_id, "end", text=f"   📆 {p['date']}", values=(p['path'], "folder"))
                    self.tree.insert(d_id, "end", text="Lade...", values=("", "dummy"))
                    if filter_mode: self.tree.item(d_id, open=True); self.on_tree_expand_manual(d_id, p['path'])

    def on_tree_expand_manual(self, item_id, path):
        children = self.tree.get_children(item_id)
        if len(children) == 1 and self.tree.item(children[0], "text") == "Lade...":
            self.tree.delete(children[0])
            items = self.file_mgr.get_directory_content(path)
            for it in items:
                oid = self.tree.insert(item_id, "end", text=f"{it['icon']} {it['name']}", values=(it['path'], "folder" if it['is_dir'] else "file"), open=False)
                if it['is_dir']: self.tree.insert(oid, "end", text="Lade...", values=("", "dummy"))
    def on_tree_expand(self, event):
        item_id = self.tree.focus(); values = self.tree.item(item_id, "values")
        if values and values[1] not in ["year", "project"] and os.path.exists(values[0]): self.on_tree_expand_manual(item_id, values[0])

    def preload_cloud_data(self):
        self.swarm.fetch_world_state()
        if hasattr(self, 'tree_cloud') and self.swarm.last_world_state: self.populate_cloud_tree()
    def reload_cloud_tree_data(self):
        data, err = self.swarm.fetch_world_state()
        if data: self.populate_cloud_tree(); messagebox.showinfo("Cloud", "Aktualisiert.")
        else: messagebox.showerror("Fehler", f"{err}")
    def populate_cloud_tree(self):
        self.tree_cloud.delete(*self.tree_cloud.get_children())
        if not self.swarm.last_world_state: return
        world = self.swarm.last_world_state.get("json", {})
        my_name = self.cfg.data["system_name"]

        for user, content in world.items():
            if user == "SHARES" or user == my_name: continue
            if not isinstance(content, dict): continue
            
            user_id = self.tree_cloud.insert("", "end", text=f"👤 {user} ({content.get('last_update', '?')})", open=True)
            projects = content.get("data", {}).get("projects", {})
            
            for p_name, p_data in projects.items():
                p_id = self.tree_cloud.insert(user_id, "end", text=f"☁️ {p_name}", values=(p_name, "project"))
                
                for s_name, s_data in p_data.get("streets", {}).items():
                    s_id = self.tree_cloud.insert(p_id, "end", text=f"🛣️ {s_name}", values=(p_name, "street"))
                    
                    for h_name, h_data in s_data.items():
                        h_id = self.tree_cloud.insert(s_id, "end", text=f"🕳️ {h_name}", values=(p_name, "haltung"))
                        
                        # --- HIER IST DIE ÄNDERUNG (Logik aus main.py) ---
                        for item_name, item_data in h_data.items():
                            # 1. Unterscheidung ob Dokumente oder Schaden
                            if item_name == "📄 DOKUMENTE": 
                                f_id = self.tree_cloud.insert(h_id, "end", text=f"📄 DOKUMENTE", values=(p_name, "files"))
                            else: 
                                f_id = self.tree_cloud.insert(h_id, "end", text=f"📁 {item_name}", values=(p_name, "dmg_folder"))
                            
                            # 2. Dateien anzeigen (das fehlte in main2)
                            for f in item_data.get("files", []):
                                self.tree_cloud.insert(f_id, "end", text=f"   🎬 {f['name']}", values=(p_name, "file"))

    def on_cloud_double_click(self, event):
        item_id = self.tree_cloud.identify_row(event.y)
        if not item_id: return
        vals = self.tree_cloud.item(item_id, "values")
        if vals: 
            if messagebox.askyesno("Cloud Import", f"An Projekt '{vals[0]}' weiterarbeiten?"): self.start_project_from_string(vals[0])

    def start_project(self):
        if self.entry_nr.get() and self.entry_city.get(): self.start_project_from_string(f"{self.entry_nr.get()} {self.entry_city.get()}")
    def start_project_from_string(self, proj_full_name):
        clean = proj_full_name.replace("📂 ", "").replace("☁️ ", "").strip()
        nr, city = clean.split(" ", 1) if " " in clean else (clean, "")
        today_path = self.file_mgr.get_smart_daily_path(nr, city)
        if today_path: self.active_project = {"nr": nr, "city": city, "path": today_path}; self.show_work()
        else: messagebox.showerror("Fehler", "Pfadfehler.")

    # --- KONTEXT ACTIONS ---
    def ctx_continue_work(self): self.start_project_from_string(self.tree.item(self.tree.selection()[0], "text"))
    def ctx_open_explorer(self):
        try:
            path = self.tree.item(self.tree.selection()[0], "values")[0]
            if os.path.exists(path): os.startfile(path)
        except: pass
    def show_context_menu(self, event):
        item_id = self.tree.identify_row(event.y)
        if item_id: self.tree.selection_set(item_id); self.context_menu.post(event.x_root, event.y_root)
    
    def ctx_rename(self):
        item_id = self.tree.selection()[0]; vals = self.tree.item(item_id, "values")
        if vals[1] in ["project", "year"]: return 
        new_name = ctk.CTkInputDialog(text="Neuer Name:", title="Umbenennen").get_input()
        if new_name: 
            self.file_mgr.rename_item(vals[0], new_name); self.populate_tree_smart_years()
    
    def ctx_delete(self):
        if messagebox.askyesno("Löschen", "Sicher?"):
            self.file_mgr.delete_item(self.tree.item(self.tree.selection()[0], "values")[0])
            self.tree.delete(self.tree.selection()[0])

    def log_system(self, message):
        if hasattr(self, 'log_console'):
            self.log_console.configure(state="normal")
            self.log_console.insert("end", f"[{datetime.datetime.now().strftime('%H:%M:%S')}] > {message}\n")
            self.log_console.see("end"); self.log_console.configure(state="disabled")

    # --- WORK & TOOLS ---
    def show_work(self):
        self.clear_main()
        if not self.active_project["path"]: self.show_dashboard(); return
        
        proj_name = f"{self.active_project['nr']} {self.active_project['city']}"
        
        # Header
        top = ctk.CTkFrame(self.main_frame, fg_color=self.colors["card"], height=60)
        top.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(top, text=f"AKTIV: {proj_name}", font=("Consolas", 20, "bold"), text_color=self.colors["accent"]).pack(side="left", padx=20, pady=15)
        
        self.refresh_project_data_logic(proj_name)
        grid = ctk.CTkFrame(self.main_frame, fg_color="transparent"); grid.pack(fill="both", expand=True)

        # SPALTE 1: Navigation (LINKS)
        col1 = ctk.CTkFrame(grid, fg_color=self.colors["card"], width=300)
        col1.pack(side="left", fill="y", padx=(0, 20), ipadx=10)
        
        # Einheitliche Einstellungen für ALLES in dieser Spalte
        # Damit alles gleich aussieht:
        std_layout = {"fill": "x", "padx": 20, "pady": 5} # Immer volle Breite, 5px Abstand
        
        ctk.CTkLabel(col1, text="1. ZIEL", text_color=self.colors["text_dim"], 
                     font=("Arial", 12, "bold"), anchor="w").pack(fill="x", padx=20, pady=(20,5))
                     
                     # --- FIX: Comboboxen Theme ---
        combo_args = {

            "fg_color": self.colors["card"],

            "border_color": self.colors["border"],

            "button_color": self.colors["border"],

            "button_hover_color": self.colors["accent"],

            "dropdown_fg_color": self.colors["card"],

            "dropdown_hover_color": self.colors["accent"],

            "dropdown_text_color": self.colors["text"],

            "text_color": self.colors["text"]

        }
        
        # Dropdowns (Comboboxes)
        self.combo_street = ctk.CTkComboBox(col1, height=40, command=self.on_street_change, **combo_args)
        self.combo_street.pack(**std_layout)
        
        self.combo_haltung = ctk.CTkComboBox(col1, height=40, **combo_args)
        self.combo_haltung.pack(**std_layout)
        
        self.update_street_combo()
        
        # Trennlinie (optional, aber schick)
        ctk.CTkFrame(col1, height=2, fg_color=self.colors["border"]).pack(fill="x", padx=20, pady=15)

        # Button: Ordner Öffnen
        ctk.CTkButton(col1, text="ORDNER ÖFFNEN 📂", command=self.set_active_folder, height=40,
                      fg_color=self.colors["border"], hover_color=self.colors["accent"], 
                      text_color=self.colors["text"]).pack(**std_layout)
        
        ctk.CTkLabel(col1, text="WERKZEUGE", text_color=self.colors["text_dim"], 
                     font=("Arial", 12, "bold"), anchor="w").pack(fill="x", padx=20, pady=(20,5))
        
        # Button: Smart Aufmaß
        ctk.CTkButton(col1, text="📄 SMART AUFMASS", command=self.action_copy_aufmass, height=40,
                      fg_color="transparent", border_width=1, 
                      border_color=self.colors["border"], text_color=self.colors["text"],
                      hover_color=self.colors["accent"]).pack(**std_layout)
        
        # Button: Bericht
        ctk.CTkButton(col1, text="BERICHT (HTML)", command=self.action_create_report, height=40,
                      fg_color="transparent", border_width=1, 
                      border_color=self.colors["border"], text_color=self.colors["text"],
                      hover_color=self.colors["accent"]).pack(**std_layout)
        
        # Ganz unten: Zurück Button (Mit etwas mehr Abstand nach oben, damit er sich abhebt)
        ctk.CTkFrame(col1, fg_color="transparent").pack(fill="y", expand=True) # Platzhalter schiebt Button nach unten
        
        ctk.CTkButton(col1, text="< ZURÜCK", command=self.show_dashboard, height=40,
                      fg_color="transparent", text_color=self.colors["error"], 
                      hover_color=self.colors["card"]).pack(fill="x", padx=20, pady=20)

        # SPALTE 2: Maßnahmen & Video
        col2 = ctk.CTkFrame(grid, fg_color="transparent"); col2.pack(side="left", fill="both", expand=True)
        
        box_dmg = ctk.CTkFrame(col2, fg_color=self.colors["card"]); box_dmg.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(box_dmg, text="2. MASSNAHMEN", text_color=self.colors["text_dim"], font=("Arial", 12, "bold")).pack(pady=(10,5))
        
        dmg_row = ctk.CTkFrame(box_dmg, fg_color="transparent"); dmg_row.pack(pady=10)
        
        # --- FIX: Entry & Combo ---
        self.entry_meter = ctk.CTkEntry(dmg_row, width=80, placeholder_text="M",
                                        fg_color=self.colors["bg"], border_color=self.colors["border"], text_color=self.colors["text"])
        self.entry_meter.pack(side="left", padx=5)
        
        self.combo_dmg = ctk.CTkComboBox(dmg_row, values=["Stutzen", "K-Liner", "Riss", "Muffe", "Schacht", "Loch"], width=150, **combo_args)
        self.combo_dmg.pack(side="left", padx=5)
        
        ctk.CTkButton(dmg_row, text="[+] ORDNER", width=80, command=self.create_dmg_folder, 
                      fg_color=self.colors["accent"], text_color=self.colors["bg"], hover_color=self.colors["text"]).pack(side="left", padx=5)
        
        box_rec = ctk.CTkFrame(col2, fg_color=self.colors["card"], border_width=1, border_color=self.colors["border"]); box_rec.pack(fill="x", pady=0)
        ctk.CTkLabel(box_rec, text="VIDEO AUFNAHME", text_color=self.colors["text_dim"], font=("Arial", 12, "bold")).pack(pady=(10,5))
        
        # --- FIX: Video Combos ---
        self.combo_target_folder = ctk.CTkComboBox(box_rec, values=[], width=300, **combo_args)
        self.combo_target_folder.pack(pady=5)
        
        self.combo_phase = ctk.CTkComboBox(box_rec, values=["vor san", "nach fräsen", "nach san", "nach verschließen"], width=300, **combo_args)
        self.combo_phase.pack(pady=5)
        
        btn_row = ctk.CTkFrame(box_rec, fg_color="transparent"); btn_row.pack(pady=20)
        
        self.entry_dn = ctk.CTkEntry(btn_row, width=60, placeholder_text="DN",
                                     fg_color=self.colors["bg"], border_color=self.colors["border"], text_color=self.colors["text"])
        self.entry_dn.pack(side="left", padx=10)
        
        ctk.CTkButton(btn_row, text="🔴 REC", command=self.action_record, width=120, height=40, 
                      fg_color=self.colors["error"], hover_color="#ff5555").pack(side="left", padx=10)
        
        # --- FIX: OBS Button Hover ---
        self.btn_obs = ctk.CTkButton(btn_row, text="📡 OBS UPDATE", command=self.action_update_obs, width=120, height=40, 
                                     fg_color="transparent", border_width=1, 
                                     border_color=self.colors["accent"], text_color=self.colors["text"],
                                     hover_color=self.colors["accent"]) # <--- Hover Fix
        self.btn_obs.pack(side="left", padx=10)

        # SPALTE 3: Historie
        col3 = ctk.CTkFrame(grid, fg_color=self.colors["card"], width=200); col3.pack(side="right", fill="y", padx=(20, 0), ipadx=10)
        ctk.CTkLabel(col3, text="HISTORIE", text_color=self.colors["text_dim"], font=("Arial", 12, "bold")).pack(pady=(20,10))
        self.history_scroll = ctk.CTkScrollableFrame(col3, fg_color="transparent", width=180); self.history_scroll.pack(fill="both", expand=True)

        ctk.CTkFrame(self.main_frame, height=2, fg_color=self.colors["border"]).pack(fill="x", pady=(10, 5))
        
        # --- FIX: Log Console (hatten wir schon, aber sicher ist sicher) ---
        self.log_console = ctk.CTkTextbox(self.main_frame, height=120, fg_color=self.colors["card"], text_color=self.colors["accent"], font=("Consolas", 21))
        self.log_console.pack(fill="x", padx=0, pady=(0, 20)); self.log_console.configure(state="disabled")
        self.log_system("System bereit.")

    # --- LOGIC METHODS ---
    def refresh_project_data_logic(self, proj_name):
        self.local_structure = {}
        all_projects = self.file_mgr.scan_local_projects()
        if proj_name in all_projects:
            for entry in all_projects[proj_name]["paths"]:
                if os.path.exists(entry["path"]):
                    for s in os.listdir(entry["path"]):
                        if os.path.isdir(os.path.join(entry["path"], s)):
                            if s not in self.local_structure: self.local_structure[s] = set()
                            for h in os.listdir(os.path.join(entry["path"], s)):
                                if os.path.isdir(os.path.join(entry["path"], s, h)): self.local_structure[s].add(h)
        for s in self.local_structure: self.local_structure[s] = list(self.local_structure[s])
        self.ghost_cache = self.swarm.get_project_ghost_structure(proj_name)
        
    def update_street_combo(self):
        all_streets = set(self.local_structure.keys()) | set(self.ghost_cache.keys())
        sorted_streets = sorted(list(all_streets))
        self.combo_street.configure(values=sorted_streets)
        if sorted_streets: self.combo_street.set(sorted_streets[0]); self.on_street_change(sorted_streets[0])
        else: self.combo_street.set(""); self.combo_haltung.set("")
        
    def on_street_change(self, selected_street):
        local_h = set(self.local_structure.get(selected_street, []))
        ghost_h = self.ghost_cache.get(selected_street, set())
        all_h = sorted(list(local_h | ghost_h)); self.combo_haltung.configure(values=all_h)
        if all_h: self.combo_haltung.set(all_h[0])
        else: self.combo_haltung.set("")
        
    def set_active_folder(self):
        s = self.combo_street.get(); h = self.combo_haltung.get()
        if s and h:
            full_path = os.path.join(self.active_project["path"], s, h)
            if not os.path.exists(full_path): os.makedirs(full_path)
            self.current_street = s; self.current_haltung = h; self.current_folder_path = full_path
            self.refresh_folder_list(); self.refresh_history_panel(); self.action_update_obs()
            self.log_system(f"Ordner geöffnet: {s} / {h}")
            
    def create_dmg_folder(self, name_override=None):
        if not self.current_folder_path: return
        name = name_override if name_override else f"{self.entry_meter.get()}m {self.combo_dmg.get()}"
        self.file_mgr.create_damage_folder(self.active_project["path"], self.current_street, self.current_haltung, name)
        self.refresh_folder_list(); self.refresh_history_panel(); self.combo_target_folder.set(name)
        self.log_system(f"Erstellt: {name}")
        
    def refresh_folder_list(self):
        if not self.current_folder_path: return
        try:
            subs = [d for d in os.listdir(self.current_folder_path) if os.path.isdir(os.path.join(self.current_folder_path, d))]
            self.combo_target_folder.configure(values=subs)
            if subs: self.combo_target_folder.set(subs[-1])
        except: pass
        
    def refresh_history_panel(self):
        for w in self.history_scroll.winfo_children(): w.destroy()
        folders_map = {}
        proj_name = f"{self.active_project['nr']} {self.active_project['city']}"
        all_data = self.file_mgr.scan_local_projects()
        if proj_name in all_data:
            for entry in all_data[proj_name]["paths"]:
                check_path = os.path.join(entry["path"], self.current_street, self.current_haltung)
                if os.path.exists(check_path):
                    for d in os.listdir(check_path):
                        if os.path.isdir(os.path.join(check_path, d)): folders_map[d] = "lokal"
        world = self.swarm.last_world_state.get("json", {})
        for user, content in world.items():
            if isinstance(content, dict):
                h_data = content.get("data", {}).get("projects", {}).get(proj_name, {}).get("streets", {}).get(self.current_street, {}).get(self.current_haltung, {})
                for folder in h_data.keys():
                    if folder != "📄 DOKUMENTE":
                        if folder in folders_map: folders_map[folder] = "beides"
                        else: folders_map[folder] = "cloud"
        for f_name in sorted(folders_map.keys()):
            typ = folders_map[f_name]
            col = self.colors["text"]
            if typ == "cloud": col = "#00aaff"
            elif typ == "beides": col = "#00ff66"
            ctk.CTkButton(self.history_scroll, text=f"{'☁️' if typ!='lokal' else '◇'} {f_name}", command=lambda f=f_name: self.create_dmg_folder(f), fg_color="transparent", text_color=col, anchor="w", height=25).pack(fill="x")
    
    # --- INTELLIGENTE HYBRID LOGIK (Aus main.py wiederhergestellt) ---
    def action_record(self):
        target_sub = self.combo_target_folder.get()
        if not self.current_folder_path or not target_sub: 
            self.log_system("FEHLER: Kein Zielordner ausgewählt!")
            return
            
        src_file = filedialog.askopenfilename()
        if not src_file: return

        self.log_system(f"Starte Analyse für '{target_sub}'...")
        
        max_num = 0
        proj_name = f"{self.active_project['nr']} {self.active_project['city']}"
        
        # 1. Lokal Check
        local_hits = 0
        all_data = self.file_mgr.scan_local_projects()
        if proj_name in all_data:
            for entry in all_data[proj_name]["paths"]:
                p = os.path.join(entry["path"], self.current_street, self.current_haltung, target_sub)
                if os.path.exists(p):
                    for f in os.listdir(p):
                        m = re.match(r"^(\d+)", f)
                        if m: 
                            num = int(m.group(1))
                            if num > max_num: max_num = num
                            local_hits += 1
        
        # 2. Cloud Check
        cloud_hits = 0
        cloud_max = 0
        world = self.swarm.last_world_state.get("json", {})
        for user, content in world.items():
            if isinstance(content, dict):
                dmg_data = content.get("data", {}).get("projects", {}).get(proj_name, {}).get("streets", {}).get(self.current_street, {}).get(self.current_haltung, {}).get(target_sub, {})
                for f in dmg_data.get("files", []):
                    m = re.match(r"^(\d+)", f["name"])
                    if m: 
                        num = int(m.group(1))
                        if num > max_num: max_num = num
                        if num > cloud_max: cloud_max = num
                        cloud_hits += 1
        
        next_num = max_num + 1
        self.log_system(f"Lokal: {local_hits}, Cloud: {cloud_hits}. Nächste Nr: {next_num}")

        dest_folder = os.path.join(self.current_folder_path, target_sub)
        if not os.path.exists(dest_folder): os.makedirs(dest_folder)
        
        new_name = f"{next_num} {self.combo_phase.get()}{os.path.splitext(src_file)[1]}"
        shutil.copy2(src_file, os.path.join(dest_folder, new_name))
        self.log_system(f"✅ Video gespeichert: {new_name}")

    def action_copy_aufmass(self):
        if not self.current_folder_path: 
            self.log_system("Fehler: Bitte erst einen Ordner öffnen."); return

        self.log_system("Suche nach letztem Aufmaß (Lokal & Cloud)...")
        proj_name = f"{self.active_project['nr']} {self.active_project['city']}"
        max_teil = 0
        last_found_local = None 
        base_exists = False 
        
        # 1. LOKAL
        all_projects = self.file_mgr.scan_local_projects()
        if proj_name in all_projects:
            for entry in all_projects[proj_name]["paths"]:
                check_path = os.path.join(entry["path"], self.current_street, self.current_haltung)
                if os.path.exists(check_path):
                    for f in glob.glob(os.path.join(check_path, "*Aufma*.xls*")):
                        m = re.search(r"Teil\s*(\d+)", os.path.basename(f), re.IGNORECASE)
                        if m: 
                            num = int(m.group(1))
                            if num > max_teil: max_teil = num; last_found_local = f
                        else: base_exists = True; last_found_local = f 

        # 2. CLOUD
        if self.swarm.last_world_state:
            world = self.swarm.last_world_state.get("json", {})
            for user, content in world.items():
                if isinstance(content, dict):
                    h_data = content.get("data", {}).get("projects", {}).get(proj_name, {}).get("streets", {}).get(self.current_street, {}).get(self.current_haltung, {})
                    files = h_data.get("📄 DOKUMENTE", {}).get("files", [])
                    for file_info in files:
                         fname = file_info.get("name", "")
                         if "aufma" in fname.lower() and ".xls" in fname.lower():
                            m = re.search(r"Teil\s*(\d+)", fname, re.IGNORECASE)
                            if m:
                                num = int(m.group(1))
                                if num > max_teil: max_teil = num
                            else: base_exists = True

        next_num = 0
        if max_teil > 0: next_num = max_teil + 1
        elif base_exists: next_num = 2 
        else: next_num = 0 
        
        self.log_system(f"--> Gefunden: Teil {max_teil}. Erstelle: Teil {next_num if next_num > 0 else 1}")

        safe = self.current_haltung.replace("/", "_").replace("\\", "_")
        if next_num == 0: target_name = f"Aufmaß Roboter {safe}.xlsx"
        else: target_name = f"Aufmaß Roboter {safe} - Teil {next_num}.xlsx"

        target_path = os.path.join(self.current_folder_path, target_name)
        source_path = None
        
        if last_found_local: source_path = last_found_local
        else:
            msg = f"Cloud hat Teil {max_teil}. Wähle Vorlage:" if max_teil > 0 else "Erstes Aufmaß: Bitte Vorlage wählen:"
            source_path = filedialog.askopenfilename(title=msg, filetypes=[("Excel", "*.xls*")])

        if source_path and os.path.exists(source_path):
            try:
                shutil.copy2(source_path, target_path)
                self.log_system(f"✅ ERFOLG: {target_name} erstellt.")
                os.startfile(target_path)
            except Exception as e: self.log_system(f"❌ FEHLER: {str(e)}")

    def action_create_report(self):
        if not self.current_folder_path: return
        ok, path = self.file_mgr.generate_html_report(self.current_folder_path, self.current_street, self.current_haltung)
        if ok: os.startfile(path)
        
    def show_sync_dialog(self):
        self.clear_main()
        
        # Titel auch anpassen
        ctk.CTkLabel(self.main_frame, text="CLOUD SWARM SYNC", font=("Impact", 48), 
                     text_color=self.colors["text"]).pack(pady=40)
        
        self.lbl_sync = ctk.CTkLabel(self.main_frame, text="Bereit.", text_color=self.colors["text_dim"])
        self.lbl_sync.pack()
        
        # --- FIX: Sync Button Style ---
        ctk.CTkButton(self.main_frame, text="JETZT SYNCHRONISIEREN", command=self.perform_full_sync, height=50,
                      fg_color=self.colors["accent"],      # Knallige Akzentfarbe
                      text_color=self.colors["bg"],        # Text dunkel (Kontrast)
                      hover_color=self.colors["text"],     # Helle Farbe beim Hover
                      font=("Arial", 21, "bold")
                      ).pack(pady=20)
    
    def perform_full_sync(self):
        self.lbl_sync.configure(text="⏳ Sync läuft...")
        def _t():
            d, e = self.swarm.fetch_world_state()
            if not d: self.lbl_sync.configure(text=f"Fehler: {e}"); return
            
            my_exp = self.file_mgr.scan_for_cloud_export()
            full = d["json"]
            full[self.cfg.data["system_name"]] = {
                "user": self.cfg.data["system_name"],
                "password": self.cfg.data.get("admin_password", "1234"),
                "last_update": datetime.datetime.now().strftime("%d.%m.%Y %H:%M Uhr"),
                "data": my_exp
            }
            
            # --- WICHTIG: LOKALES TEMPLATE PRÜFEN ---
            final_template = d["html_template"]
            if os.path.exists("template.html"):
                try:
                    with open("template.html", "r", encoding="utf-8") as f:
                        final_template = f.read()
                except: pass
            
            ok, msg = self.swarm.push_world_state(full, d["sha"], final_template)
            if ok: self.lbl_sync.configure(text="✅ Sync OK!", text_color=self.colors["accent"]); self.swarm.last_world_state = {"json": full}
            else: self.lbl_sync.configure(text=f"Upload Fehler: {msg}")
        threading.Thread(target=_t, daemon=True).start()

    # --- CONFIG ---
    def open_settings(self):
        self.clear_main()
        ctk.CTkLabel(self.main_frame, text="SYSTEM KONFIGURATION", font=("Impact", 24), text_color=self.colors["accent"]).pack(pady=(20, 10))
        
        scroll = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=10)

        # Standard-Style für Eingaben
        entry_args = {"height": 40, "fg_color": self.colors["card"], "border_color": self.colors["border"], "text_color": self.colors["text"]}
        combo_args = {
            "height": 40,
            "fg_color": self.colors["card"], "border_color": self.colors["border"],
            "button_color": self.colors["border"], "button_hover_color": self.colors["accent"],
            "dropdown_fg_color": self.colors["card"], "dropdown_hover_color": self.colors["accent"],
            "dropdown_text_color": self.colors["text"], "text_color": self.colors["text"]
        }

        self.add_setting_label(scroll, "SYSTEM / ROBOTER NAME")
        self.entry_sys_name = ctk.CTkEntry(scroll, **entry_args)
        self.entry_sys_name.pack(fill="x", pady=(0, 15))
        self.entry_sys_name.insert(0, self.cfg.data.get("system_name", "Roboter 1"))

        self.add_setting_label(scroll, "WEB PASSWORT")
        self.entry_admin_pass = ctk.CTkEntry(scroll, **entry_args)
        self.entry_admin_pass.pack(fill="x", pady=(0, 15))
        self.entry_admin_pass.insert(0, self.cfg.data.get("admin_password", "1234"))

        self.add_setting_label(scroll, "THEME / DESIGN")
        self.combo_theme = ctk.CTkComboBox(scroll, values=list(THEMES.keys()), **combo_args)
        self.combo_theme.pack(fill="x", pady=(0, 15))
        if self.cfg.data.get("theme") in THEMES: self.combo_theme.set(self.cfg.data.get("theme"))

        self.add_setting_label(scroll, "ORDNER STRUKTUR")
        self.combo_struct = ctk.CTkComboBox(scroll, values=["KW Jahr (z.B. KW2 2026)", "Jahr/KW (z.B. 2026/KW2)"], width=300, **combo_args)
        self.combo_struct.pack(fill="x", pady=(0, 15))
        self.combo_struct.set(self.cfg.data.get("folder_structure", "KW Jahr (z.B. KW2 2026)"))

        self.add_setting_label(scroll, "BASIS PFAD")
        path_row = ctk.CTkFrame(scroll, fg_color="transparent"); path_row.pack(fill="x", pady=(0, 15))
        
        self.entry_path = ctk.CTkEntry(path_row, **entry_args)
        self.entry_path.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry_path.insert(0, self.cfg.data.get("base_path", ""))
        
        ctk.CTkButton(path_row, text="📂 WÄHLEN", width=100, height=40, command=self.browse_path_action, 
                      fg_color=self.colors["border"], hover_color=self.colors["accent"], text_color=self.colors["text"]).pack(side="right")

        self.add_setting_label(scroll, "GITHUB TOKEN")
        self.entry_token = ctk.CTkEntry(scroll, show="*", **entry_args)
        self.entry_token.pack(fill="x", pady=(0, 15))
        self.entry_token.insert(0, self.cfg.data.get("github_token", ""))

        ctk.CTkButton(self.main_frame, text="💾 SPEICHERN & NEUSTART", height=50, command=self.save_settings_logic, 
                      fg_color=self.colors["accent"], text_color=self.colors["bg"], 
                      hover_color=self.colors["text"], font=("Arial", 14, "bold")).pack(fill="x", padx=20, pady=20)
        
        danger_box = ctk.CTkFrame(scroll, fg_color="#330000", border_color="red", border_width=1)
        danger_box.pack(fill="x", pady=40, padx=5, ipady=10)
        ctk.CTkLabel(danger_box, text="⚠️ GEFAHRENZONE", text_color="red", font=("Arial", 12, "bold")).pack()
        ctk.CTkButton(danger_box, text="🔥 DATEN AUS CLOUD ENTFERNEN", command=self.action_delete_cloud_data, fg_color="red", hover_color="#880000").pack(pady=10)

    def add_setting_label(self, parent, text): ctk.CTkLabel(parent, text=text, anchor="w", font=("Arial", 12, "bold"), text_color=self.colors["text"]).pack(fill="x", pady=(5, 2))
    
    def browse_path_action(self): 
        p = filedialog.askdirectory(); 
        if p: self.entry_path.delete(0, "end"); self.entry_path.insert(0, p)
        
    def save_settings_logic(self):
        self.cfg.data["system_name"] = self.entry_sys_name.get()
        self.cfg.data["admin_password"] = self.entry_admin_pass.get()
        self.cfg.data["theme"] = self.combo_theme.get()
        self.cfg.data["base_path"] = self.entry_path.get()
        self.cfg.data["github_token"] = self.entry_token.get()
        self.cfg.data["folder_structure"] = self.combo_struct.get()
        self.cfg.save_config()
        
        messagebox.showinfo("Neustart", "Einstellungen gespeichert.\nDas Programm startet jetzt neu.")
        
        self.destroy() # Fenster schließen 

        executable = sys.executable
        args = sys.argv

        if getattr(sys, 'frozen', False):
            # Wenn es eine EXE ist: Starte neuen Prozess und beende aktuellen 
            import subprocess
            subprocess.Popen([executable] + args[1:])
            sys.exit() 
        else:
            # Wenn es ein Skript ist: Nutze os.execl 
            import os
            os.execl(executable, executable, *args)
        
    def on_close_app(self):
        """Speichert Position beim Schließen"""
        
        # ACHTUNG: Das 'if' beginnt hier:
        if self.state() != "zoomed":
            # WICHTIG: Diese beiden Zeilen müssen EINGERÜCKT sein (Tab-Taste drücken)!
            self.cfg.data["window_geometry"] = self.geometry()
            self.cfg.save_config()
        
        # Diese Zeilen gehören nicht mehr zum 'if', also wieder zurück nach links:
        self.destroy() # Fenster schließen
        sys.exit()     # Programm beenden
        
    def action_delete_cloud_data(self):
        name = self.cfg.data["system_name"]
        if not messagebox.askyesno("WARNUNG", f"Wirklich alle Cloud-Daten von '{name}' löschen?"): return
        d, err = self.swarm.fetch_world_state()
        if not d: messagebox.showerror("Fehler", err); return
        full_json = d["json"]
        if name in full_json:
            del full_json[name]
            ok, msg = self.swarm.push_world_state(full_json, d["sha"], d["html_template"])
            if ok: messagebox.showinfo("Erfolg", "Daten gelöscht.")
            else: messagebox.showerror("Fehler", msg)
        else: messagebox.showinfo("Info", "Keine Daten gefunden.")
    def action_update_obs(self):
        if not self.active_project["path"]: return
        city = self.active_project["city"]; street = self.combo_street.get(); haltung = self.combo_haltung.get(); dn = self.entry_dn.get()
        success = self.file_mgr.update_obs_txt(city, street, haltung, dn)
        if success:
            orig = "📡 OBS UPDATE"; self.btn_obs.configure(text="✅ GESENDET", fg_color=self.colors["accent"], text_color=self.colors["bg"])
            self.after(2000, lambda: self.btn_obs.configure(text=orig, fg_color="transparent", text_color=self.colors["text"]))
            self.log_system(f"OBS Update: {city}, {street}...")
        else: self.log_system("FEHLER bei OBS txt")
        
       

if __name__ == "__main__":
    app = DiTomApp()
    app.mainloop()