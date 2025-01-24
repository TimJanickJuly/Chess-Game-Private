//
// Created by tim.janick.july on 21.08.2024.
//

#include "BoardHashMap.h"

#include <iostream>


std::size_t BoardHashMap::BoardHasher::operator()(const int board[8][8]) const {
    std::size_t hash = 0;
    for (int i = 0; i < 8; ++i) {
        for (int j = 0; j < 8; ++j) {
            hash ^= std::hash<int>()(board[i][j]) + 0x9e3779b9 + (hash << 6) + (hash >> 2);
        }
    }
    return hash;
}

bool BoardHashMap::memorize_board_state(const int board[8][8]) {
    int board_hash = boardHasher(board);
    auto it = boardFrequency.find(board_hash);
    if (it != boardFrequency.end()) {
        if (it->second < 2) {
            it->second += 1;
            return true;
        }
        return false;
    }
    boardFrequency[board_hash] = 1;
    return true;
    }


void BoardHashMap::clear_hashmap_history() {
    boardFrequency.clear();
}