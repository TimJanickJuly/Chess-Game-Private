#include <iostream>
#include <memory>
#include <string>
#include "game.h"

int main() {
    auto board = std::make_shared<Game>();
    std::string move;

    std::cout << "Initial Board State:\n";
    board->print_board_state();

    // Liste von Zügen, die simuliert werden
    std::vector<std::string> moves = {"e4", "e5", "Nf3", "Nf6", "Bc4", "Bc5", "o-o", "o-o", "a3"};
    for (const auto& move : moves) {
        std::cout << "\nPlaying move: " << move << "\n";
        int status = board->handle_turn(move);

        if (status == -1) {
            std::cout << "Illegal move: " << move << "\n";
            continue;
        }

        if (status == 1) {
            std::cout << "Invalid move syntax: " << move << "\n";
            continue;
        }

        if (status == 0) {
            std::cout << "Game Over: " << board->last_move_status << "\n";
            board->print_board_state();
            break;
        }

        std::cout << "Board after move:\n";
        board->print_board_state();

        std::cout << "\nAvailable moves for active player:\n";
        auto available_moves = board->get_all_available_moves();
        for (const auto& vector : available_moves) {
            if (!vector.empty()) {
                int col_start = vector.at(0)->col_start;
                int row_start = vector.at(0)->row_start;

                auto col_it = Move::dict_col_coord_to_char.find(col_start);
                auto row_it = Move::dict_row_coord_to_char.find(row_start);

                if (col_it != Move::dict_col_coord_to_char.end() && row_it != Move::dict_row_coord_to_char.end()) {
                    std::cout << vector.at(0)->getPieceToMove() << " on "
                              << col_it->second << row_it->second << ":\n";
                }

                std::cout << "{";
                for (auto it = vector.begin(); it != vector.end(); ++it) {
                    std::cout << (*it)->get_algebraic_chess_notation();
                    if (std::next(it) != vector.end()) {
                        std::cout << ", ";
                    }
                }
                std::cout << "}\n";
            }
        }
    }

    return 0;
}
