# 🤖 DiTom Site Manager v50 "Total Swarm"

![Platform](https://img.shields.io/badge/Platform-Windows-blue)
![Language](https://img.shields.io/badge/Language-Python_3.12-yellow)
![GUI](https://img.shields.io/badge/GUI-CustomTkinter-green)
![Architecture](https://img.shields.io/badge/Architecture-Serverless%20Swarm-purple)

**Dezentrales Baustellen-Management & Dokumentations-System für Kanalsanierungs-Roboter.**

Der **DiTom Site Manager** ist eine spezialisierte Desktop-Applikation, die entwickelt wurde, um die Dokumentation (Videos, Aufmaße, Berichte) auf Baustellen zu automatisieren und zwischen mehreren Anlagen (Robotern) zu synchronisieren – **ohne** einen zentralen Server zu benötigen.

---

## 🚀 Features

### 🧠 Live Swarm Intelligence
*   **Dezentrale Synchronisation:** Nutzt GitHub als "Datenbank". Kein SQL-Server oder AWS nötig.
*   **Globaler Status:** Jeder Roboter sieht den Fortschritt aller anderen Anlagen (welche Haltung wurde bearbeitet? Welche Videos existieren schon?).
*   **Konfliktvermeidung:** Das System prüft vor dem Erstellen neuer Dateien (z.B. "Video Nr. 3"), ob ein Kollege diese Nummer bereits vergeben hat, selbst wenn die Datei lokal noch nicht existiert.

### ⚡ Smart Automation
*   **Intelligente Dateibenennung:** Automatische Benennung von Videos und Excel-Dateien basierend auf dem Projektstatus (z.B. `3 nach san.mp4` oder `Aufmaß Teil 2.xlsx`).
*   **Auto-Folder-Structure:** Erstellt automatisch die korrekte Verzeichnisstruktur nach DIN/Firmenstandard (Jahr > KW > Datum > Projekt > Straße > Haltung).
*   **Ghost Data:** Importiert Ordnerstrukturen von Kollegen per Mausklick, ohne Gigabytes an Videodaten herunterladen zu müssen.

### 🎥 Media & OBS Integration
*   **OBS Studio Overlay:** Schreibt Live-Daten (Straße, Haltung, DN) in eine `obs_live.txt`, die direkt als Textquelle in OBS eingebunden werden kann.
*   **Drag & Drop Work:** Einfaches Zuweisen von Aufnahmen zu Haltungen.

### 🎨 Modern UI
*   **Bio-Neural Dark Mode:** Augenfreundliches Interface für dunkle Arbeitsumgebungen (Regiewagen).
*   **Touch-Optimiert:** Große Buttons für Bedienung auf Touchscreens.
*   **Taskbar Integration:** Korrektes Verhalten als Windows-Applikation (Minimieren/Maximieren).

---

## 🛠️ Technische Architektur

Das System verfolgt einen **Local-First** Ansatz mit einer **Serverless-Cloud-Komponente**:

1.  **Lokal:** Alle "schweren" Daten (Videos, Bilder) bleiben lokal auf dem Rechner des Roboters.
2.  **Cloud (GitHub API):** Metadaten (Ordnerstrukturen, Dateinamen, Fortschritt) werden in einem JSON-Objekt gespeichert, das in eine `index.html` injiziert wird.
3.  **Sync:** Beim Start und auf Knopfdruck lädt der Client den "World State" herunter.
    *   *Vorteil:* 0€ Hosting-Kosten, funktioniert offline, volle Datenhoheit.
    *   *Visualisierung:* Die `index.html` dient gleichzeitig als Web-Dashboard für Bauleiter/Kunden.

---

## 📦 Installation & Setup

### Voraussetzungen
*   Windows 10/11
*   Python 3.10+ (für Entwickler)
*   Git

### Für Entwickler (Source Code)

1.  **Repository klonen:**
    ```bash
    git clone https://github.com/DEIN_USER/katiproplan-live.git
    cd katiproplan-live
    ```

2.  **Abhängigkeiten installieren:**
    ```bash
    pip install customtkinter requests packaging pyinstaller
    ```

3.  **Konfiguration:**
    Erstelle eine `ditom_config.json` (wird beim ersten Start automatisch erstellt) oder nutze das Settings-Menü in der App, um deinen GitHub Token und Anlagennamen einzutragen.

4.  **Starten:**
    ```bash
    python ditom_manager.py
    ```

### Als EXE kompilieren (Build)

Da `CustomTkinter` spezielle Asset-Dateien benötigt, nutze das beiliegende Build-Skript:

1.  Führe das Build-Skript aus:
    ```bash
    python build_exe.py
    ```
2.  Die fertige `.exe` befindet sich im Ordner `dist/`.
3.  **WICHTIG:** Kopiere folgende Dateien manuell in den `dist/` Ordner zur `.exe`:
    *   `roboter.ico`
    *   `template.html`

---

## 📖 Bedienungsanleitung

### 1. Projekt Starten
*   Gib im Dashboard **Projekt-Nr** und **Stadt** ein.
*   Klicke auf `AUSFÜHREN`. Der Tagesordner wird automatisch erstellt.

### 2. Arbeiten (Lokal)
*   Wähle im Reiter "BEARBEITUNG" die **Straße** und **Haltung**.
*   Erstelle Ordner für Schäden (z.B. "Stutzen", "Riss") über die Buttons.
*   Drücke `REC` (startet Simulation/Kopie), um ein Video zu speichern. Das System wählt automatisch die nächste freie Nummer.

### 3. Cloud Sync (Swarm)
*   Gehe auf "ÜBERSICHT" -> "CLOUD SWARM".
*   Klicke `CLOUD SYNC`. Deine Fortschritte werden hochgeladen, Fortschritte der Kollegen werden heruntergeladen.
*   **Import:** Siehst du ein Projekt eines Kollegen (Blau markiert)? Doppelklick auf eine Haltung importiert dessen Struktur zu dir ("Ghost Mode"), damit du nahtlos weiterarbeiten kannst.

### 4. OBS Einbindung
*   Füge in OBS eine "Text (GDI+)" Quelle hinzu.
*   Wähle "Aus Datei lesen" und verweise auf die `obs_live.txt` im Programmordner.
*   Die Einblendung aktualisiert sich automatisch, wenn du die Haltung wechselst.

---

## 📂 Dateistruktur

```text
/
├── ditom_manager.py       # Hauptanwendung
├── build_exe.py           # PyInstaller Skript
├── template.html          # Web-Dashboard Vorlage
├── roboter.ico            # App Icon
├── ditom_config.json      # Lokale Einstellungen (Ignored by Git)
├── ditom_cloud_state.json # Cache des Schwarm-Wissens
└── obs_live.txt           # Output für OBS Studio
```

---

## ⚠️ Bekannte Hinweise

*   **GitHub Token:** Das Token wird lokal in der `ditom_config.json` gespeichert. Gib diese Datei nicht weiter!
*   **Konflikte:** Wenn zwei Roboter exakt zur gleichen Sekunde syncen, gewinnt der letzte. Dank "Optimistic Locking" (SHA-Check) warnt das System jedoch meistens vor Konflikten.

---

## 📝 Lizenz

Dieses Projekt ist proprietäre Software für den internen Gebrauch.
Copyright © 2024-2026 - DiTom Site Manager Team.

---

*Made with 🐍 Python & CustomTkinter.*
