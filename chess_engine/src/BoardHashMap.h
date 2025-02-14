#ifndef BOARD_HASHMAP_H
#define BOARD_HASHMAP_H

#include <cstdint>
#include <unordered_map>

class BoardHashMap {
public:
    bool memorize_board_state(const int board[8][8]);
    void clear_hashmap_history();
private:
    struct BoardHasher {
        std::size_t operator()(const int board[8][8]) const;
    };

    struct BoardEqual {
        bool operator()(const int lhs[8][8], const int rhs[8][8]) const;
    };

    std::unordered_map<std::size_t, int> boardFrequency;
    BoardHasher boardHasher;
};

#endif // BOARD_HASHMAP_H
