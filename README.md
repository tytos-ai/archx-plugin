# ArchX für Codex und Claude

Mit diesem Plugin arbeiten Codex und Claude Code mit den Fachwerkzeugen Ihrer installierten ArchX-App: Ausmass aus Plänen
und IFC, Offertvergleich mit Preisspiegel und Vergabeantrag, Kostenvoranschlag und Kostenschätzung nach BKP,
Machbarkeitsstudie, Baueingabe-Nachweis (Bauziffern, SIA 416), Grundrisse und masshaltige 2D-Pläne, 3D-Modell aus Plänen
und die ArchX-Hilfe. Es sind dieselben Werkzeuge und Arbeitsanweisungen wie in einem Gespräch in ArchX.

## Voraussetzungen

- ArchX auf dem Mac oder unter Windows, angemeldet, mit Lizenz oder laufendem Test
  ([architekten.frontierx.ch](https://architekten.frontierx.ch/archx/)).
- Ein Büro in der Schweiz oder in Deutschland (ArchX › Einstellungen › Land).
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
Preisspiegel und Vergabeantrag.»

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

- **«ArchX hat die Verbindung abgelehnt»:** Das Plugin steht Büros in der Schweiz und in Deutschland zur Verfügung. Prüfen
  Sie in ArchX unter Einstellungen das Land des Büros.
- **«Keine installierte ArchX-App gefunden»:** ArchX von [architekten.frontierx.ch](https://architekten.frontierx.ch/archx/)
  installieren und einmal öffnen.
- **«ArchX wurde gestartet, ist aber nicht erreichbar»:** ArchX einmal von Hand öffnen und anmelden.

Das Plugin läuft dort, wo Codex oder Claude auf Ihrem Computer arbeiten (Codex-App und -CLI, Claude Code). In ChatGPT
oder claude.ai im Browser gibt es die ArchX-Werkzeuge nicht.

ArchX ist ein Produkt von FrontierX, TYTOS GmbH, Kriens.
