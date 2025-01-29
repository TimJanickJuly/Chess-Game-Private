cmake_minimum_required(VERSION 3.12) # Erhöht auf 3.12 für moderne Features
project(chess_engine VERSION 1.0 LANGUAGES CXX)

# C++17 festlegen
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Compiler-spezifische Flags
if(UNIX)
    set(CMAKE_POSITION_INDEPENDENT_CODE ON) # Automatisch -fPIC auf Unix
endif()

# Pybind11 suchen
find_package(pybind11 REQUIRED)

# Quell- und Header-Dateien
set(SOURCE_FILES
    bindings/bindings.cpp
    src/game.cpp
    src/Chess_Piece.cpp
    src/Move.cpp
    src/BoardHashMap.cpp
)

# Pybind11-Modul definieren
pybind11_add_module(chess_engine ${SOURCE_FILES})

# Ziel-Eigenschaften festlegen
if(WIN32)
    # Für Windows: .pyd-Datei
    set_target_properties(chess_engine PROPERTIES
        PREFIX ""
        SUFFIX ".pyd"                           # Python-kompatible Modul-Endung
        OUTPUT_NAME "chess_engine"              # Sicherstellen, dass der Name korrekt bleibt
    )
elseif(UNIX)
    # Für Unix/Linux: .so-Datei
    set_target_properties(chess_engine PROPERTIES
        PREFIX ""
        SUFFIX ".so"                            # Python-kompatible Modul-Endung
        OUTPUT_NAME "chess_engine"              # Sicherstellen, dass der Name korrekt bleibt
    )
else()
    message(FATAL_ERROR "Unbekannte Plattform. Modul-Endung nicht festgelegt.")
endif()

# Include-Verzeichnisse hinzufügen
target_include_directories(chess_engine PRIVATE ${CMAKE_SOURCE_DIR}/src)

# Zusätzliche Compiler-Warnungen aktivieren (optional, für Debugging)
if(MSVC)
    target_compile_options(chess_engine PRIVATE /W4)
else()
    target_compile_options(chess_engine PRIVATE -Wall -Wextra -pedantic)
endif()

# Ausgabe verifizieren
message(STATUS "CMake project configured for Python module 'chess_engine'")