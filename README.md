# ChessEngine Python Module

Dieses Projekt erstellt ein Python-Modul (`chess_engine`) aus einer C++-Codebasis mithilfe von `pybind11`.

## Voraussetzungen

- Python 3.7 oder neuer
- `pybind11` installiert (z. B. via `pip install pybind11`)
- C++17-kompatibler Compiler
- CMake 3.12 oder neuer

## Installation

1. **Clone das Repository** und navigiere in das Verzeichnis des Projekts:
   ```bash
   git clone <repository-url>
   cd ChessGame/source/chess_engine
   ```

2. **Erstelle ein Build-Verzeichnis**:
   ```bash
   mkdir build
   cd build
   ```
(cmake -Dpybind11_DIR="C:/Users/tim.janick.july/Documents/Ch
essGame/venv/Lib/site-packages/pybind11/share/cmake/pybind11" ..)

3. **Führe CMake aus**, um das Projekt zu konfigurieren. Achte darauf, den richtigen `pybind11`-Pfad anzugeben:
   ```bash
   cmake -Dpybind11_DIR=$(python -m pybind11 --cmakedir) ..
   ```

4. **Baue das Modul**:
   ```bash
   cmake --build . --config Release
   ```

   Nach dem Build sollte die Datei `chess_engine.pyd` (unter Windows) oder `chess_engine.so` (unter Unix) im Ordner `Release` generiert werden:
   ```plaintext
   build/Release/chess_engine.pyd
   ```

## Nutzung

1. **Füge das Build-Verzeichnis zu `PYTHONPATH` hinzu**, damit das Modul importiert werden kann:
   ```bash
   export PYTHONPATH=$(pwd)/Release:$PYTHONPATH
   ```
   Unter Windows:
   ```cmd
   set PYTHONPATH=%cd%\Release;%PYTHONPATH%
   ```

2. **Teste das Modul**:
   Navigiere zum Testverzeichnis und führe ein Python-Skript aus, das das Modul nutzt:
   ```bash
   cd ../../../tests
   python test_chess_engine.py
   ```

   Beispielausgabe:
   ```plaintext
   Aktiver Spieler: 1
   8  BR  BN  BB  BQ  BK  BB  BN  BR
   7  BP  BP  BP  BP  BP  BP  BP  BP
   6  ..  ..  ..  ..  ..  ..  ..  ..
   ...
   ```

## Hinweise

- **Fehlerbehebung**:
  Falls `ModuleNotFoundError: No module named 'chess_engine'` auftritt, stellen Sie sicher, dass der `PYTHONPATH` korrekt gesetzt ist.
- **Systemübergreifende Pfade**:
  Ersetze die Pfade entsprechend deinem Betriebssystem und deiner Verzeichnisstruktur.
- **Compiler-Warnungen**:
  Diese können während des Builds auftreten, beeinträchtigen jedoch die Funktionalität nicht.

Viel Spaß beim Programmieren!
