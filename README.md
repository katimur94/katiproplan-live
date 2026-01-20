🤖 DiTom Site Manager v53

Intelligente Baustellendokumentation & Schwarm-Synchronisation

Der DiTom Site Manager ist eine spezialisierte Softwarelösung für die Kanalsanierung. Er optimiert den Workflow vor Ort, automatisiert die Berichterstellung und ermöglicht einen nahtlosen Datenaustausch zwischen verschiedenen Sanierungseinheiten via Cloud-Sync – ganz ohne teure Serverinfrastruktur.

🚀 Key Features

Echtzeit-Performance-Cockpit: Visuelle Kontrolle über sanierte Bauteile und Projektfortschritt.

Intelligente Ordnerstruktur: Automatisierte Anlage von Tagesprojekten nach KW/Jahr-Logik.

Schwarm-Intelligenz: Synchronisation von Projektdaten (Metadaten) über das GitHub-Backend.

Smart-Aufmaß: Automatische Generierung und Nummerierung von Excel-Aufmaßblättern.

OBS Integration: Direktes Update von Text-Overlays für die Videoüberwachung.

Modularer Aufbau: Über 10 Themes für optimale Sichtbarkeit unter Baustellenbedingungen.

🛠 Das System im Detail

1. Das Dashboard (Performance & Archiv)

Das Dashboard bietet einen schnellen Überblick über die aktuelle Leistung des Operators. Hier können Projekte gestartet und lokale sowie Cloud-Daten verwaltet werden.

Zentrale Suche: Blitzschneller Zugriff auf das gesamte lokale Archiv.

Cloud-Daten: Einsicht in die Projektfortschritte anderer "Schwarm-Teilnehmer".

2. Der Arbeitsmodus (Operationelle Ebene)

Hier wird die Dokumentation während der Sanierung durchgeführt. Das Interface ist auf Geschwindigkeit und Fehlerminimierung ausgelegt.

Maßnahmen-Management: Erstellung von Schadensordnern (Stutzen, Liner, Risse) mit einem Klick.

Intelligente Video-Benennung: Das System prüft die Historie und vergibt automatisch die korrekte Fortlaufnummer für Videoaufnahmen (z.B. 2 nach san.mp4).

Historie: Schneller Vergleich zwischen lokalem Stand und Cloud-Status der aktuellen Haltung.

3. Smart-Dokumentation & Tools

Automatisierung von zeitfressenden Büroaufgaben direkt im Wagen.

Automatisches Aufmaß: Das Tool erkennt vorhandene Aufmaße und erstellt basierend darauf das nächste Teilaufmaß in Excel.

HTML-Berichte: Generiert sofort druckreife Tagesübersichten für die Bauleitung.

4. Cloud Swarm Synchronisation

Datenaustausch auf Basis einer dezentralen Architektur.

Durch die Anbindung an die GitHub-API fungiert ein Repository als dezentraler Hub. So wissen alle Einheiten im Schwarm, welche Arbeiten bereits durchgeführt wurden, ohne dass Dateien mühsam manuell verschickt werden müssen.

5. Konfiguration & Personalisierung

Anpassung des Systems an die jeweilige Hardware und Vorlieben des Operators.

Flexibler Basis-Pfad: Unterstützung für externe Festplatten und Netzlaufwerke.

Design-Engines: Themes wie "Corporate Dark" oder "Midnight Blue" reduzieren die Blendwirkung bei Nachtarbeiten.

💻 Tech-Stack

Core: Python 3.x

UI-Framework: CustomTkinter (Modern UI Engine)

Backend: Swarm-Logic via GitHub API (Requests)

Mapping: Leaflet.js & Nominatim Integration

Deployment: PyInstaller (Modularized Build)

Entwickelt von Timur Kalayci
Präzision im Schacht, Ordnung im System.
