# ArchX für Codex und Claude

Mit diesem Plugin arbeiten Codex und Claude Code mit den Fachwerkzeugen Ihrer installierten ArchX-App. Es sind dieselben
Werkzeuge und Arbeitsanweisungen wie in einem Gespräch in ArchX, passend zum Land Ihres Büros:

- **Schweiz:** Ausmass aus Plänen und IFC, Offertvergleich mit Preisspiegel und Vergabeantrag, Kostenvoranschlag und
  Kostenschätzung nach BKP, Machbarkeitsstudie, Baueingabe-Nachweis (Bauziffern, SIA 416), Grundrisse und masshaltige
  2D-Pläne, 3D-Modell aus Plänen und die ArchX-Hilfe.
- **Deutschland:** Aufmaß aus Plänen und IFC, Angebotsprüfung mit Preisspiegel und Vergabevorschlag (VOB/A),
  Leistungsverzeichnisse im GAEB-Format, Kostenschätzung und Kostenberechnung nach DIN 276, GRZ, GFZ und BMZ nach
  BauNVO, maßhaltige 2D-Pläne, 3D-Modell, Fachwissen zu HOAI, Bauantrag und Bauüberwachung und die ArchX-Hilfe.

## Voraussetzungen

- ArchX auf dem Mac oder unter Windows, angemeldet, mit Lizenz oder laufendem Test
  ([architekten.frontierx.ch](https://architekten.frontierx.ch/archx/)).
- Ein Büro in der Schweiz oder in Deutschland (ArchX › Einstellungen › Land). Büros im Vereinigten Königreich und in den
  USA installieren die englische Variante `archx-en` (siehe «ArchX for Codex and Claude» unten).
- Codex (App oder CLI) oder Claude Code auf demselben Computer.

## Installation

Codex-App: bei den Plugins «Add marketplace» wählen, `tytos-ai/archx-plugin` eintragen und das Plugin ArchX installieren.
Oder im Terminal:

```bash
codex plugin marketplace add tytos-ai/archx-plugin
codex plugin add archx@frontierx
```

Claude Code, in einer Sitzung:

```text
/plugin marketplace add tytos-ai/archx-plugin
/plugin install archx@frontierx
```

Danach eine neue Unterhaltung beginnen. Fragen Sie zum Beispiel: «Vergleiche die Offerten in diesem Ordner und erstelle
Preisspiegel und Vergabeantrag.» oder „Prüfe die Angebote in diesem Ordner und erstelle Preisspiegel und Vergabevorschlag.“
Wechselt das Land des Büros in ArchX, beginnen Sie eine neue Unterhaltung: Die Werkzeuge des anderen Landes gelten erst dort.

Updates: `codex plugin marketplace upgrade frontierx` bzw. `/plugin marketplace update frontierx` in Claude Code. Neue
Werkzeuge brauchen kein Plugin-Update: Sie kommen mit jedem ArchX-Update.

## So funktioniert es

- **ArchX liefert, das Plugin verbindet.** ArchX öffnet beim Start einen privaten Anschluss auf Ihrem Computer. Das Plugin
  bringt nur einen Einstieg für Codex und Claude und einen kleinen Starter, der mit der Python aus ArchX läuft. Sonst
  braucht es nichts.
- **ArchX startet von selbst.** Läuft ArchX nicht, startet das Plugin es im Hintergrund. Das Fenster bleibt zu, bis Sie
  ArchX selbst öffnen.
- **Viele Unterhaltungen, keine Wartezeit.** Eine Unterhaltung hält die Verbindung zu ArchX nur, während sie arbeitet, und
  holt sie unbemerkt zurück, sobald sie ArchX wieder braucht. Auch ein Neustart von ArchX unterbricht keine Unterhaltung.
- **Lizenz und Daten bleiben bei ArchX.** ArchX prüft bei jedem Projektwerkzeug die Lizenz; Büro-Katalog und Archiv kommen
  aus den ArchX-Einstellungen. Pläne und Offerten liest ArchX auf Ihrem Computer; an Codex oder Claude gehen nur die
  Ergebnisse der Werkzeuge, wie bei jedem anderen Werkzeug dort.
- **Rückfragen stellt Codex oder Claude.** Beide fragen vor Werkzeugaufrufen nach ihren eigenen Regeln; lesende Werkzeuge
  sind als lesend gekennzeichnet, ändernde als ändernd.

## Wenn etwas nicht geht

- **«ArchX hat die Verbindung abgelehnt»:** ArchX startet noch oder alle Verbindungen sind belegt. Den Auftrag gleich noch
  einmal geben.
- **«Keine installierte ArchX-App gefunden»:** ArchX von [architekten.frontierx.ch](https://architekten.frontierx.ch/archx/)
  installieren und einmal öffnen.
- **«ArchX wurde gestartet, ist aber nicht erreichbar»:** ArchX einmal von Hand öffnen und anmelden.

Das Plugin läuft dort, wo Codex oder Claude auf Ihrem Computer arbeiten (Codex-App und -CLI, Claude Code). In ChatGPT
oder claude.ai im Browser gibt es die ArchX-Werkzeuge nicht.

ArchX ist ein Produkt von FrontierX, TYTOS GmbH, Kriens.

## ArchX for Codex and Claude (United Kingdom and United States)

With the plugin `archx-en`, Codex and Claude Code work with the professional tools of your installed ArchX app, in English.
They are the same tools and instructions as in a conversation in ArchX, matching your office's country:

- **United Kingdom:** permitted development check, householder application and Building Regulations, feasibility study,
  area schedule, cost plan, schedule of works and tender report, contract administration, site photographs, excavation from
  point clouds, reviewing drawings and checking consultants’ drawings, editing a floor plan, dimensioned 2D drawings, 3D
  models and the ArchX help.
- **United States:** code and permit review, zoning feasibility, quantities and cost planning, area schedule and occupant
  load, bid leveling and bid packages, fee proposals, construction administration, phases and specifications, site photos
  and observation reports, reviewing drawings, editing a floor plan, CAD drawings in feet and inches, 3D models on the real
  site, excavation quantities and the ArchX help.

Requirements: ArchX on the Mac or on Windows, signed in, with a license or a running trial; your office's country set to the
United Kingdom or the United States (ArchX › Settings › Country); Codex (app or CLI) or Claude Code on the same computer.

Installation in Codex: add the marketplace `tytos-ai/archx-plugin` and install ArchX (English), or in the terminal:

```bash
codex plugin marketplace add tytos-ai/archx-plugin
codex plugin add archx-en@frontierx
```

Claude Code, in a session:

```text
/plugin marketplace add tytos-ai/archx-plugin
/plugin install archx-en@frontierx
```

Then start a new conversation and ask, for example: “Check whether the rear extension in these drawings falls within
permitted development.” or “Run a code and permit review for this project.” If the office's country changes in ArchX,
start a new conversation: the other country's tools apply only there. New tools need no plugin update; they come with every
ArchX update. Licence and data stay with ArchX: it checks the licence with every project tool and reads your drawings and
tenders on your computer; Codex or Claude only receive the tools' results.
