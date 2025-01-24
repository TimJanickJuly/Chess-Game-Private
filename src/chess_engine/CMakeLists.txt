cmake_minimum_required(VERSION 3.28)
project(chess)

set(CMAKE_CXX_STANDARD 17)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/bin)

add_executable(chess main.cpp
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
