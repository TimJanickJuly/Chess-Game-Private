
#!/bin/bash

# System-Updates und Abhängigkeiten installieren
sudo yum install git -y
sudo yum groupinstall "Development Tools" -y
sudo yum install gcc-c++ -y
sudo yum install cmake -y
sudo yum install python3-devel -y
sudo yum install tmux -y

# Git-Repository klonen
rm -rf Chess-Game-Private  # Falls das Projekt schon existiert, löschen
git clone https://github.com/TimJanickJuly/Chess-Game-Private.git

# Virtuelle Umgebung einrichten
cd Chess-Game-Private
python3 -m venv venv
source venv/bin/activate

# Python-Abhängigkeiten installieren
pip install --upgrade pip
pip install fastapi uvicorn pydantic websockets fastapi[all] pybind11

# C++-Code kompilieren (Pybind11 + Chess Engine)
cd chess_engine
mkdir -p build
cd build
cmake -Dpybind11_DIR="/home/ec2-user/Chess-Game-Private/venv/lib64/python3.9/site-packages/pybind11/share/cmake/pybind11" ..
cmake --build . --config Release

# Kompiliertes Python-Modul verschieben
cp chess_engine.so /home/ec2-user/Chess-Game-Private/venv/lib/python3.9/site-packages/chess_engine.so

# Backend in tmux starten
cd ../../backend
tmux new -d -s backend "source venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

# Frontend in tmux starten (falls es statisch gehostet wird)
cd ../frontend
tmux new -d -s frontend "python3 -m http.server 3000 --bind 0.0.0.0"

# Abschlussmeldung
echo "✅ Projekt wurde erfolgreich installiert und gestartet!"
echo "📌 Backend läuft auf: http://$(curl -s ifconfig.me):8000"
echo "📌 Frontend läuft auf: http://$(curl -s ifconfig.me):3000"
echo "🔄 Backend erneut aufrufen mit: tmux attach -t backend"
echo "🔄 Frontend erneut aufrufen mit: tmux attach -t frontend"

