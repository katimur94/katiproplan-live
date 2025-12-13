# katiproplan-live

---

# 🏗️ Präsentation: DiTom Site Manager v30.0
**Untertitel:** Digitalisierung & Automatisierung der Kanalsanierungs-Dokumentation

---

## 📌 Folie 1: Die Ausgangslage (Das Problem)
*   **Chaos im Dateisystem:** Manuelle Ordnerstruktur führt zu Fehlern (z.B. "Hauptstr." vs. "Hauptstraße").
*   **Zeitverlust:** Tägliches manuelles Umbenennen von Videos ("Teil 1", "Teil 2") kostet wertvolle Arbeitszeit.
*   **Mangelnde Übersicht:** Keiner weiß, was der andere Roboter gerade macht oder wo er letzte Woche war.
*   **Daten-Silo:** Tagesberichte liegen lokal auf dem Laptop. Das Büro hat keinen sofortigen Zugriff.

---

## 🚀 Folie 2: Die Lösung – DiTom Site Manager
Eine maßgeschneiderte Software-Lösung, die als zentrale Steuereinheit auf jedem Fahrzeug-Laptop läuft.

*   **Standardisierung:** Erzwingt eine einheitliche Ordnerstruktur nach DIN/Firmenvorgabe.
*   **Automatisierung:** Erkennt alte Dateien und nummeriert neue Videos/Berichte automatisch fortlaufend.
*   **Synchronisation:** Verbindet alle Fahrzeuge über eine Cloud-Schnittstelle mit dem Büro (Live-Dashboard).

---

## 🛠️ Folie 3: Kern-Funktionen (Was kann es?)

### 1. Der "Sherlock Holmes" Scanner 🔍
Das Programm weiß alles. Wenn man heute an einer Haltung arbeitet, scannt es das gesamte Laufwerk nach **vergangenen Arbeiten** an dieser Stelle.
*   *Beispiel:* Letzte Woche wurde "Video Teil 1" gemacht. Das Programm benennt das heutige Video automatisch in "Video Teil 2" um.

### 2. Intelligentes Dashboard 🌳
Ein Explorer-Baum, der nicht nur Ordner anzeigt, sondern logisch sortiert:
*   Projekt -> Datum -> Straße -> Haltung -> Schaden.
*   **Neu in v30:** Tiefe Einsicht bis zur einzelnen Datei, direktes Umbenennen und Löschen per Rechtsklick.

### 3. Büro-Automatik 📄
*   **Excel:** Kopiert die Firmen-Vorlage und benennt sie korrekt nach der Haltung.
*   **Tagesbericht:** Erstellt auf Knopfdruck eine HTML-Übersicht für Bauleiter/Kunden.

---

## ☁️ Folie 4: Das Multi-User Cloud System (Highlight)
Das Herzstück der Version 30.0.

*   **Jeder Roboter ist ein Profil:** In den Einstellungen wird der Name (z.B. "Roboter 1") und ein Passwort vergeben.
*   **Intelligenter Merge:** Wenn Roboter 1 seine Daten hochlädt, **überschreibt** er nicht die Daten von Roboter 2. Das System lädt die aktuelle Datenbank, fügt seine Daten hinzu und speichert alles ab.
*   **Web-Ansicht:** Eine passwortgeschützte Webseite zeigt dem Büro **alle** Projekte **aller** Fahrzeuge in Echtzeit.

---

## ⭐ Folie 5: Was ist neu in Version 30.0?
Das "Usability Update":

1.  **Deep Search & Auto-Expand:** Suchst du nach "S100", öffnet sich der Baum automatisch an genau der richtigen Stelle.
2.  **Full Control:** Ordner und Projekte können direkt im Dashboard umbenannt oder gelöscht werden.
3.  **Sicherheitsnetz:** "Soft Delete" (Ausblenden) vs. "Hard Delete" (Löschen) verhindert Datenverlust.
4.  **Performance:** Der Scanner läuft im Hintergrund (Threading), damit das Programm auch bei 100.000 Dateien nicht einfriert.

---

## 🔮 Folie 6: Ausblick (Roadmap)
Was könnte man in Zukunft noch einbauen?

*   **KI-Schadenserkennung:** Automatische Analyse der Fotos (Riss, Scherbe) durch KI.
*   **Karten-Integration:** Anzeige der Haltungen auf einer Google Maps Karte.
*   **PDF-Engine:** Generierung von fertigen PDF-Berichten direkt aus der Software (statt HTML).
*   **Material-Erfassung:** Eingabe von verbrauchtem Harz/Liner direkt im Tool für die Abrechnung.

---

# 📘 Technische Dokumentation (Code-Erklärung)

Hier erkläre ich dir die wichtigsten Bausteine des Codes, damit du Fragen dazu beantworten kannst.

### 1. Architektur & Bibliotheken
*   **`customtkinter`:** Sorgt für das moderne, dunkle Design (sieht nicht aus wie Windows 95).
*   **`os` & `shutil`:** Die "Hände" des Programms. Sie erstellen Ordner, verschieben Dateien und benennen um.
*   **`threading`:** Das "Gehirn-Management". Es sorgt dafür, dass schwere Aufgaben (Laufwerk scannen, Upload) im Hintergrund laufen, während die Oberfläche bedienbar bleibt.
*   **`requests` & `base64`:** Die "Telefonleitung" zu GitHub.

### 2. Der "Intelligente Scanner" (`generate_export_json`)
Dies ist der komplexeste Teil.
*   **Funktion:** Er nutzt `os.walk`, um jeden Winkel der Festplatte zu durchsuchen.
*   **Der Filter:** Er schaut sich den Pfad an: `Basis / Jahr / KW / Datum / ...`.
*   **Der Trick:** Er prüft mit `datetime.strptime`, ob der Ordnername wirklich ein Datum (YYYY-MM-DD) ist. Wenn nicht (z.B. ein Systemordner wie `.git` oder `bin`), ignoriert er den ganzen Ast sofort. Das macht ihn extrem schnell und präzise.

### 3. Die GitHub-Bridge (`run_github_logic`)
Hier passiert die Magie der Synchronisation ohne Datenbank-Server.
1.  **Download:** Lädt die aktuelle `index.html` von GitHub herunter.
2.  **Extraktion:** Sucht im HTML-Code nach den Markern `/*JSON_START*/` und `/*JSON_END*/`. Alles dazwischen ist die aktuelle Datenbank aller Roboter.
3.  **Merge:** Nimmt die extrahierte Datenbank und aktualisiert **nur** den Eintrag für den eigenen Roboter (z.B. "Roboter 2"). Roboter 1 bleibt unberührt.
4.  **Injection:** Schreibt das neue JSON wieder zwischen die Marker in die lokale `template.html`.
5.  **Upload:** Sendet die neue HTML-Datei zurück an GitHub. Netlify erkennt die Änderung und aktualisiert die Webseite sofort.

### 4. Das Dashboard (`filter_tree`)
*   Baut den Baum (`Treeview`) dynamisch auf.
*   Nutzt Rekursion, um Projekt -> Datum -> Straße -> Haltung -> Datei darzustellen.
*   Die **Suchfunktion** filtert diesen Baum in Echtzeit und setzt das `open=True` Flag, damit gefundene Elemente sofort sichtbar aufgeklappt werden.

### 5. Datensicherheit (`save_config`)
*   Das Programm prüft mit `sys.frozen`, ob es als `.exe` läuft.
*   Es speichert die `ditom_config.json` immer direkt neben der `.exe`. So gehen Einstellungen auch bei einem Update oder PC-Wechsel nicht verloren, solange man den Ordner kopiert.

---

### Zusammenfassung für den Chef:
> *"Wir haben hier nicht nur ein Datei-Tool gebaut, sondern eine **dezentrale Cloud-Plattform**. Wir nutzen die Sicherheit und Infrastruktur von GitHub (Microsoft), ohne eigene Server betreiben zu müssen. Das spart uns monatliche Hosting-Kosten und Wartungsaufwand, während wir gleichzeitig eine professionelle Dokumentation sicherstellen."*
