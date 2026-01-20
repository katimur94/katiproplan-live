# 🤖 DiTom Site Manager v53 "Total Swarm"

![Platform](https://img.shields.io/badge/Platform-Windows-blue?style=for-the-badge)
![Language](https://img.shields.io/badge/Language-Python_3.12-yellow?style=for-the-badge)
![GUI](https://img.shields.io/badge/GUI-CustomTkinter-green?style=for-the-badge)
![Architecture](https://img.shields.io/badge/Architecture-Serverless%20Swarm-purple?style=for-the-badge)

**Die nächste Generation der Baustellendokumentation für Kanalsanierungs-Flotten.**

Der **DiTom Site Manager** ist kein einfaches Dateiverwaltungsprogramm. Es ist ein hochspezialisiertes Operating-System für Sanierungsroboter-Teams. Es eliminiert manuellen Schreibaufwand, verhindert Dateikonflikte zwischen Anlagen und synchronisiert den Projektfortschritt in Echtzeit über eine intelligente, serverlose Cloud-Struktur.

---

## 🏗️ Der Operationelle Workflow

### 1. Das Performance Cockpit (Dashboard)
Dein Start in den Tag. Das System visualisiert live deine Erfolge (sanierte Stutzen & gefahrene Projekte). 

![Dashboard Übersicht](images/DiTom_Site_Manager_v51_Beta_UI7hMrFWoa.png)

* **Zentraler Einstieg:** Projektnummer und Ort eingeben – das System erledigt den Rest (Ordneranlage, Sync-Prüfung).
* **Archiv-Zugriff:** Blitzschnelle Suche in tausenden lokalen Projekten durch optimierte Dateisystem-Scans.

### 2. Deep-Work Modus (Dokumentation vor Ort)
Hier passiert die eigentliche Arbeit. Das Interface ist für die harten Bedingungen im Regiewagen optimiert: Große Buttons, klare Kontraste und minimaler Input-Aufwand.

![Arbeitsbereich](images/DiTom_Site_Manager_v51_Beta_gaw4V9hqPj.png)

* **Smart Folders:** Erstelle Schadensordner (Stutzen, Liner, Riss) mit automatischer Metrierung und Zeitstempel.
* **Intelligente Video-Logik:** Das System prüft lokal und in der Cloud, welche Video-Nummer als Nächstes dran ist (z.B. `1 nach san.mp4`). Keine überschriebenen Dateien mehr!
* **OBS Studio Sync:** Live-Daten (Straße, Haltung, DN) werden direkt als Textquelle für dein Video-Overlay bereitgestellt.

### 3. Cloud Swarm (Dezentrale Intelligenz)
Mehrere Roboter arbeiten im selben Projekt? Kein Problem. Der Swarm-Sync hält alle auf demselben Stand.

![Cloud Sync Status](images/DiTom_Site_Manager_v51_Beta_pqTEorOpVP.png)

* **Ghost Data:** Übernimm Haltungsstrukturen von Kollegen per Doppelklick, ohne deren Gigabytes an Videodaten herunterladen zu müssen.
* **Serverless Architecture:** Nutzt die GitHub API als sicheres, kostenloses Backend. Volle Datenhoheit und 0€ Hosting-Kosten.

---

## 🛠️ Technische Highlights

| Feature | Beschreibung |
| :--- | :--- |
| **Smart Aufmaß** | Erkennt bestehende Excel-Tabellen und führt diese logisch fort (Teil 1 -> Teil 2). |
| **Theme Engine** | 10 spezialisierte Designs (z.B. *Bio-Neural* für Nachtschichten) zur Schonung der Augen. |
| **Hybrid-Speicher** | "Local-First" Ansatz: Videos bleiben lokal, Metadaten gehen in den Schwarm. |
| **Auto-Reporting** | Generiert sofort druckfähige HTML-Tagesberichte für Bauleiter und Kunden. |

---

## 📦 Installation & Build

### Voraussetzungen
* **Windows 10/11**
* **Python 3.12+** (für die Entwicklung)

### EXE Erstellung
Für den stabilen Einsatz im Wagen nutzen wir ein modulares Build-Verfahren (PyInstaller), um Pfadprobleme mit Tcl/Tk zu vermeiden.

```powershell
python build_exe.py
