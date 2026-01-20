# 🤖 DiTom Site Manager v53 "Total Swarm"

![Platform](https://img.shields.io/badge/Platform-Windows-blue?style=for-the-badge)
![Language](https://img.shields.io/badge/Language-Python_3.12-yellow?style=for-the-badge)
![GUI](https://img.shields.io/badge/GUI-CustomTkinter-green?style=for-the-badge)
![Architecture](https://img.shields.io/badge/Architecture-Serverless%20Swarm-purple?style=for-the-badge)

**Das ultimative Betriebssystem für Kanalsanierungs-Teams. Dezentral. Automatisiert. Baustellentauglich.**

Der **DiTom Site Manager v53** wurde entwickelt, um das Chaos auf Sanierungs-Baustellen zu beenden. Er verbindet lokale Hochleistungs-Dokumentation mit globaler Schwarm-Intelligenz – ohne Serverkosten und ohne komplizierte IT.

---

## 🛠️ Erstnutzung: Was du beachten musst

Wenn du die App zum ersten Mal startest, sind zwei Schritte entscheidend, damit der "Motor" läuft:

1.  **Basis-Pfad festlegen:** Gehe in die `⚙️ Config`. Hier musst du den Ordner wählen, auf dem deine Baustellendaten liegen (z.B. deine externe Baustellen-Festplatte). Das System scannt diesen Pfad automatisch und baut dein Archiv in Millisekunden auf.
2.  **GitHub Token & Repo:** Für den Schwarm-Sync benötigt die App einen GitHub-Token. Sobald dieser hinterlegt ist, verbindet sich dein Roboter mit der Flotte.
3.  **System-Name:** Gib deinem Roboter einen Namen (z.B. "Anlage 1"). Dieser Name erscheint bei allen Kollegen im Cloud-Sync.

---

## 🏗️ Funktions-Deep-Dive

### 1. Das Dashboard (Performance & Überwachung)
Das Dashboard ist mehr als nur eine Übersicht. Es ist dein Cockpit.

![Dashboard Übersicht](images/DiTom_Site_Manager_v51_Beta_UI7hMrFWoa.png)

* **Live-Gauges:** Die digitalen Anzeigen für sanierten Stutzen und Baustellen reagieren sofort auf deine Filter (z.B. "Dieses Jahr" oder "Gesamt").
* **Projekt-Schnellstart:** Gib einfach Nr. und Stadt ein. Das System prüft sofort, ob das Projekt neu ist oder ob du daran schon einmal gearbeitet hast, und erstellt die Tagesstruktur.

### 2. Die Baum-Ansicht (Treeview) & Context-Menü
Die linke Spalte ist dein Gedächtnis. Hier steckt mächtige Logik hinter dem **Rechtsklick**:

* **🚀 HIER ARBEITEN:** Öffnet sofort das Projekt im Arbeitsmodus, egal in welchem Jahr es liegt.
* **📂 Im Explorer öffnen:** Springt direkt in den Windows-Ordner – kein langes Suchen mehr.
* **✏️ Umbenennen:** Benenne Ordner oder Projekte direkt in der App um. Das System aktualisiert die Pfade im Hintergrund.
* **🗑️ Löschen:** Entfernt Daten sicher von der Festplatte (mit Sicherheitsabfrage).

### 3. Der Arbeitsmodus (Operationelle Ebene)
Hier dokumentierst du deine Sanierung in Echtzeit.

![Arbeitsbereich](images/DiTom_Site_Manager_v51_Beta_gaw4V9hqPj.png)

* **Smart Automation:** Wenn du auf `[+] ORDNER` klickst, wird nicht nur ein Ordner erstellt. Das System formatiert den Namen nach deinen Meter-Angaben (z.B. `14,20m Stutzen`).
* **Historie & Ghost-Mode:** In der rechten Spalte siehst du blaue Einträge. Das sind Arbeiten von Kollegen. Klicke darauf, um deren Struktur sofort zu "erben" – so bleibt die Benennung über alle Anlagen hinweg identisch.

---

## ⚙️ Technische Raffinessen

### Die Neustart-Funktion (Hybrid-Prozess)
Ein Highlight der Version 53 ist der intelligente Neustart nach Einstellungsänderungen. Wir nutzen eine Hybrid-Lösung:
* **Im Skript-Modus:** Nutzt `os.execl()`, um den Python-Prozess direkt zu ersetzen.
* **Im EXE-Modus:** Nutzt `subprocess.Popen()`, um eine frische Instanz zu starten und die alte sauber zu beenden. Dies verhindert den berüchtigten `init.tcl`-Fehler in kompilierten Anwendungen.

### Build-Struktur (`_internal`)
Wir bauen die App im `--onedir` Modus. Das bedeutet für dich:
* Die EXE ist extrem schnell beim Start.
* Alle Ressourcen liegen im Ordner `_internal`. **Wichtig:** Dieser Ordner muss immer zusammen mit der EXE verschickt werden. Er enthält das "Gehirn" der App (DLLs, CustomTkinter-Assets).

---

## 🩹 Bisherige Bugfixes (Changelog v53)

* ✅ **Init.tcl Fix:** Das Problem, dass die EXE beim Neustart die Tcl-Bibliotheken verliert, wurde durch den Wechsel auf `onedir` und optimierte Prozess-Vererbung gelöst.
* ✅ **Gauge-Color Fix:** Die Hintergrundringe der Tachos passen sich nun dynamisch jedem Theme an (keine Hardcoded-Farben mehr).
* ✅ **History Sync:** Ein Fehler wurde behoben, bei dem Cloud-Einträge doppelt in der Historie angezeigt wurden.
* ✅ **Window Geometry:** Das Fenster merkt sich nun exakt seine Position und Größe, außer es war beim Schließen maximiert.

---

## 📂 Dateistruktur des Repos

```text
/
├── images/            # Alle Screenshots für diese Dokumentation
├── main.py            # Die Steuerzentrale (GUI-Logik)
├── file_manager.py    # Das Dateisystem-Genie
├── backend_swarm.py   # Die dezentrale Cloud-Schnittstelle
├── config.py          # Theme-Verwaltung und Einstellungen
├── build_exe.py       # Das automatisierte Build-System
└── version_info.txt   # Metadaten für die Windows-EXE (Version 53)
