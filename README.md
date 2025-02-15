# Chess Game – Online Multiplayer Chess

This project is a fully functional online chess game with three main components:

Chess Engine (C++):The engine is implemented in C++ and handles game logic. It is made available in Python using pybind11.

Backend (FastAPI/Python):The backend manages game instances and provides a REST API. It is built with FastAPI and runs on uvicorn.

Frontend (Brython):The frontend is implemented using Brython and runs directly in the browser.

Installation & Execution

Linux / AWS (Bash Script)
'''
#!/bin/bash

sudo yum install git -y
sudo yum groupinstall "Development Tools" -y
sudo yum install gcc-c++ cmake python3-devel tmux -y

rm -rf Chess-Game-Private
git clone https://github.com/TimJanickJuly/Chess-Game-Private.git
cd Chess-Game-Private

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install fastapi uvicorn pydantic websockets fastapi[all] pybind11

cd chess_engine
mkdir -p build && cd build
cmake -Dpybind11_DIR="/home/<USERNAME>/Chess-Game-Private/venv/lib64/python3.9/site-packages/pybind11/share/cmake/pybind11" ..
cmake --build . --config Release

cp chess_engine.so ../venv/lib/python3.9/site-packages/chess_engine.so

cd ../../backend
tmux new -d -s backend "source ../venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

cd ../frontend
tmux new -d -s frontend "python3 -m http.server 3000 --bind 0.0.0.0"

echo "✅ Installation complete."
echo "📌 Backend: http://$(curl -s ifconfig.me):8000"
echo "📌 Frontend: http://$(curl -s ifconfig.me):3000"
'''

Windows (WSL / Git Bash)

'''
rm -rf Chess-Game-Private
git clone https://github.com/TimJanickJuly/Chess-Game-Private.git
cd Chess-Game-Private

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install fastapi uvicorn pydantic websockets fastapi[all] pybind11

cd chess_engine
mkdir build && cd build
cmake -Dpybind11_DIR="$(python3 -m pybind11 --cmakedir)" ..
cmake --build . --config Release

cp chess_engine.so ../venv/lib/python3.9/site-packages/chess_engine.so

cd ../../backend
source ../venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

cd ../frontend
python3 -m http.server 3000 --bind 0.0.0.0
'''


Follow the installation instructions and enjoy the game!
