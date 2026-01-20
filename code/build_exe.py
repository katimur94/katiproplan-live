import PyInstaller.__main__
import os

# 1. Konfiguration
MAIN_SCRIPT = "main.py"
APP_NAME = "DiTom_Site_Manager_v53" # <--- Geändert auf v53
ICON_FILE = "roboter.ico"
VERSION_FILE = "file_version_info.txt" 

# 2. Build-Befehl
args = [
    MAIN_SCRIPT,
    f'--name={APP_NAME}',
    '--onedir',
    '--noconsole',
    '--clean',
    '--collect-all=customtkinter',
]

# Icon hinzufügen
if os.path.exists(ICON_FILE):
    print(f"🎨 Icon gefunden: {ICON_FILE}")
    args.append(f'--icon={ICON_FILE}')
    args.append(f'--add-data={ICON_FILE};.')

# --- SIGNATUR (METADATEN) HINZUFÜGEN ---
if os.path.exists(VERSION_FILE):
    print(f"✍️ Signiere mit Version 53...") # <--- Text-Update
    args.append(f'--version-file={VERSION_FILE}')
else:
    print("⚠️ Warnung: Keine Versions-Datei gefunden. EXE wird nackt gebaut.")

print("🔨 Baue EXE...")
PyInstaller.__main__.run(args)
print(f"✅ Fertig! Deine signierte App liegt in 'dist/{APP_NAME}.exe'")