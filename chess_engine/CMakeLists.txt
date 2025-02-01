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

# -------------------------------
# Python-Modul (chess_engine) bauen
# -------------------------------
set(MODULE_SOURCE_FILES
    bindings/bindings.cpp
    src/game.cpp
    src/Chess_Piece.cpp
    src/Move.cpp
    src/BoardHashMap.cpp
)

pybind11_add_module(chess_engine ${MODULE_SOURCE_FILES})

if(WIN32)
    # Für Windows: .pyd-Datei
    set_target_properties(chess_engine PROPERTIES
        PREFIX ""
        SUFFIX ".pyd"                           # Python-kompatible Modul-Endung
        OUTPUT_NAME "chess_engine"              # Name beibehalten
    )
elseif(UNIX)
    # Für Unix/Linux: .so-Datei
    set_target_properties(chess_engine PROPERTIES
        PREFIX ""
        SUFFIX ".so"                            # Python-kompatible Modul-Endung
        OUTPUT_NAME "chess_engine"              # Name beibehalten
    )
else()
    message(FATAL_ERROR "Unbekannte Plattform. Modul-Endung nicht festgelegt.")
endif()

target_include_directories(chess_engine PRIVATE ${CMAKE_SOURCE_DIR}/src)

if(MSVC)
    target_compile_options(chess_engine PRIVATE /W4)
else()
    target_compile_options(chess_engine PRIVATE -Wall -Wextra -pedantic)
endif()

message(STATUS "CMake project configured for Python module 'chess_engine'")

# ------------------------------------
# Executable (main.exe) zum Testen bauen
# ------------------------------------
# Setze den Ausgabepfad für Executables (z. B. im Ordner "bin")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/bin)

set(EXECUTABLE_SOURCES
    main.cpp
    src/game.cpp
    src/game.h
    src/move.h
    src/Move.cpp
    src/Chess_Piece.cpp
    src/Chess_Piece.h
    test.h
    test.cpp
    src/BoardHashMap.cpp
    src/BoardHashMap.h
)

add_executable(main ${EXECUTABLE_SOURCES})

target_include_directories(main PRIVATE ${CMAKE_SOURCE_DIR}/src)

if(MSVC)
    target_compile_options(main PRIVATE /W4)
else()
    target_compile_options(main PRIVATE -Wall -Wextra -pedantic)
endif()

message(STATUS "CMake project configured for executable 'main'")