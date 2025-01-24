#include "Chess_Piece.h"

#include <iostream>
#include <vector>

bool Chess_Piece::is_move_possible(const int board[8][8], int target_coord_row, int target_coord_col, bool is_capture, bool is_defense) const {
    int piece_color = (color == "white") ? 1 : -1;

    if (target_coord_row < 0 || target_coord_row >= 8 || target_coord_col < 0 || target_coord_col >= 8) {
        return false;
    }

    if (!is_defense && board[target_coord_row][target_coord_col] * piece_color > 0) { // a piece cannot move to a square on which a friedly
        return false;                                                                  //piece is, but it can defend a the friendly piece there
    }

    switch (type) {
        case 'P':
            return is_pawn_move_possible(board, target_coord_row, target_coord_col, is_capture, is_defense);
        case 'N':
            return is_knight_move_possible(board, target_coord_row, target_coord_col, is_capture);
        case 'R':
            return is_rook_move_possible(board, target_coord_row, target_coord_col, is_capture, is_defense);
        case 'Q':
            return is_queen_move_possible(board, target_coord_row, target_coord_col, is_capture, is_defense);
        case 'K':
            return is_king_move_possible(board, target_coord_row, target_coord_col, is_capture);
        case 'B':
            return is_bishop_move_possible(board, target_coord_row, target_coord_col, is_capture, is_defense);
        default:
            return false;
    }
}

bool Chess_Piece::is_pawn_move_possible(const int board[8][8], int target_coord_row, int target_coord_col, bool is_capture, bool is_defense) const {
    int row_start = get_row();
    int col_start = get_col();
    std::string color = getColor();
    int direction = (color == "white") ? 1 : -1;

    if (!is_capture) {
        if (target_coord_row == row_start + direction && target_coord_col == col_start) {
            if (board[target_coord_row][target_coord_col] == 0) {
                return true;
            }
        }
        if (target_coord_row == row_start + 2 * direction && target_coord_col == col_start) {
            if ((color == "white" && row_start == 1) || (color == "black" && row_start == 6)) {
                if (board[target_coord_row][target_coord_col] == 0 && board[row_start + direction][col_start] == 0) {
                    return true;
                }
            }
        }
    }
    if (is_capture) {
        if ((target_coord_row == row_start + direction && target_coord_col == col_start + 1) ||
            (target_coord_row == row_start + direction && target_coord_col == col_start - 1)) {
            if (board[target_coord_row][target_coord_col] != 0 || is_defense) {
                return true;
            }
        }
    }
    return false;
}

bool Chess_Piece::is_king_move_possible(const int board[8][8], int target_coord_row, int target_coord_col, bool is_capture) const {
    int row_start = get_row();
    int col_start = get_col();
    std::string color = getColor();
    int piece_color = (color == "white") ? 1 : -1;

    int row_diff = std::abs(target_coord_row - row_start);
    int col_diff = std::abs(target_coord_col - col_start);





    if (row_diff == 0 && col_diff == 0) {
        return false;
    }

    if (row_diff <= 1 && col_diff <= 1) {
        return true;
    }
    return false;
}


bool Chess_Piece::is_knight_move_possible(const int board[8][8], int target_coord_row, int target_coord_col, bool is_capture) const {
    int row_start = get_row();
    int col_start = get_col();
    std::string color = getColor();
    int piece_color = (color == "white") ? 1 : -1;

    int row_diff = std::abs(target_coord_row - row_start);
    int col_diff = std::abs(target_coord_col - col_start);

    if ((row_diff == 2 && col_diff == 1) || (row_diff == 1 && col_diff == 2)) {
        return true;
    }
    return false;
}

bool Chess_Piece::is_path_clear(const int board[8][8], int start_row, int start_col, int end_row, int end_col) const {
    int row_step = (end_row > start_row) ? 1 : (end_row < start_row) ? -1 : 0;
    int col_step = (end_col > start_col) ? 1 : (end_col < start_col) ? -1 : 0;

    int row = start_row + row_step;
    int col = start_col + col_step;

    while (row != end_row || col != end_col) {
        if (board[row][col] != 0) {
            return false;
        }
        row += row_step;
        col += col_step;
    }

    return true;
}

bool Chess_Piece::is_target_valid(const int board[8][8], int target_row, int target_col, int piece_color, bool is_capture, bool is_defense) const {
    if (target_row < 0 || target_row >= 8 || target_col < 0 || target_col >= 8) {
        return false;
    }
    if (!is_defense && board[target_row][target_col] * piece_color > 0) {
        return false;
    }
    if (!is_capture && board[target_row][target_col] * piece_color < 0) {
        return false;
    }
    return true;
}


bool Chess_Piece::is_rook_move_possible(const int board[8][8], int target_coord_row, int target_coord_col, bool is_capture, bool is_defense) const {
    int row_start = get_row();
    int col_start = get_col();
    int piece_color = (getColor() == "white") ? 1 : -1;

    if (!is_target_valid(board, target_coord_row, target_coord_col, piece_color, is_capture, is_defense)) {
        return false;
    }

    if (row_start != target_coord_row && col_start != target_coord_col) {
        return false;
    }

    return is_path_clear(board, row_start, col_start, target_coord_row, target_coord_col);
}

bool Chess_Piece::is_queen_move_possible(const int board[8][8], int target_coord_row, int target_coord_col, bool is_capture, bool is_defense) const {
    int row_start = get_row();
    int col_start = get_col();
    int piece_color = (getColor() == "white") ? 1 : -1;

    if (!is_target_valid(board, target_coord_row, target_coord_col, piece_color, is_capture, is_defense)) {
        return false;
    }

    if (row_start == target_coord_row || col_start == target_coord_col ||
        std::abs(row_start - target_coord_row) == std::abs(col_start - target_coord_col)) {
        return is_path_clear(board, row_start, col_start, target_coord_row, target_coord_col);
        }

    return false;
}
bool Chess_Piece::is_bishop_move_possible(const int board[8][8], int target_coord_row, int target_coord_col, bool is_capture, bool is_defense) const {
    int row_start = get_row();
    int col_start = get_col();
    int piece_color = (getColor() == "white") ? 1 : -1;

    if (!is_target_valid(board, target_coord_row, target_coord_col, piece_color, is_capture, is_defense)) {
        return false;
    }

    int row_diff = std::abs(target_coord_row - row_start);
    int col_diff = std::abs(target_coord_col - col_start);

    if (row_diff != col_diff) {
        return false;
    }

    return is_path_clear(board, row_start, col_start, target_coord_row, target_coord_col);
}

std::vector<std::tuple<int, int, bool>> Chess_Piece::get_available_coords_to_move_to(
    int active_player, const int board_state[8][8]) {

    std::vector<std::tuple<int, int, bool>> koord_candidates_and_is_capture;
    switch (getPieceType()) {
        case 'P': {
            int starting_row = (active_player > 0) ? 1 : 6;
            int direction = (active_player > 0) ? 1 : -1;
            if (get_row() == starting_row) {
                if (is_move_possible(board_state, get_row() + 2 * direction, get_col(), false, false)) {
                    koord_candidates_and_is_capture.push_back(std::make_tuple(get_row() + 2 * direction, get_col(), false));
                }
            }
            if (is_move_possible(board_state, get_row() + 1 * direction, get_col(), false, false)) {
                koord_candidates_and_is_capture.push_back(std::make_tuple(get_row() + 1 * direction, get_col(), false));
            }


            if (is_move_possible(board_state, get_row() + 1 * direction, get_col() + 1, true, false)) {
                koord_candidates_and_is_capture.push_back(std::make_tuple(get_row() + 1 * direction, get_col() + 1, true));
            }
            if (is_move_possible(board_state, get_row() + 1 * direction, get_col() - 1, true, false)) {
                koord_candidates_and_is_capture.push_back(std::make_tuple(get_row() + 1 * direction, get_col() - 1, true));
            }

            // en passant
            if (is_en_passant_possible(board_state, get_row() + 1 * direction, get_col() + 1, true, false)) {
                koord_candidates_and_is_capture.push_back(std::make_tuple(get_row() + 1 * direction, get_col() + 1, true));
            }
            if (is_en_passant_possible(board_state, get_row() + 1 * direction, get_col() - 1, true, false)) {
                koord_candidates_and_is_capture.push_back(std::make_tuple(get_row() + 1 * direction, get_col() - 1, true));
            }

            break;
        }
        case 'N': {
            std::vector<std::tuple<int, int>> knight_moves = {
                std::make_tuple(-2, -1), std::make_tuple(-1, -2),
                std::make_tuple(1, -2),  std::make_tuple(2, -1),
                std::make_tuple(2, 1),   std::make_tuple(1, 2),
                std::make_tuple(-1, 2),  std::make_tuple(-2, 1)
            };

            int current_row = get_row();
            int current_col = get_col();

            for (const auto& move : knight_moves) {
                int new_row = current_row + std::get<0>(move);
                int new_col = current_col + std::get<1>(move);

                if (new_row >= 0 && new_row < 8 && new_col >= 0 && new_col < 8) {
                    if (is_move_possible(board_state, new_row, new_col, true, false)) {
                        koord_candidates_and_is_capture.push_back(std::make_tuple(new_row, new_col, (board_state[new_row][new_col] != 0)));
                    }
                }
            }
            break;
        }
        case 'R': {
            int directions[4][2] = {{-1, 0}, {1, 0}, {0, -1}, {0, 1}}; // Up, Down, Left, Right
            int current_row = get_row();
            int current_col = get_col();

            for (const auto& dir : directions) {
                int row_offset = dir[0];
                int col_offset = dir[1];

                int new_row = current_row + row_offset;
                int new_col = current_col + col_offset;

                while (new_row >= 0 && new_row < 8 && new_col >= 0 && new_col < 8) {
                    if (is_move_possible(board_state, new_row, new_col, true, false)) {
                        koord_candidates_and_is_capture.push_back(std::make_tuple(new_row, new_col, (board_state[new_row][new_col] != 0)));
                        if (board_state[new_row][new_col] != 0) {
                            break; // Stop if there is a piece on the square
                        }
                    } else {
                        break; // Stop if the move is not possible
                    }

                    new_row += row_offset;
                    new_col += col_offset;
                }
            }
            break;
        }
        case 'B': {
            int directions[4][2] = {{-1, -1}, {-1, 1}, {1, -1}, {1, 1}}; // Diagonals: Up-Left, Up-Right, Down-Left, Down-Right
            int current_row = get_row();
            int current_col = get_col();

            for (const auto& dir : directions) {
                int row_offset = dir[0];
                int col_offset = dir[1];

                int new_row = current_row + row_offset;
                int new_col = current_col + col_offset;

                while (new_row >= 0 && new_row < 8 && new_col >= 0 && new_col < 8) {
                    if (is_move_possible(board_state, new_row, new_col, true, false)) {
                        koord_candidates_and_is_capture.push_back(std::make_tuple(new_row, new_col, (board_state[new_row][new_col] != 0)));
                        if (board_state[new_row][new_col] != 0) {
                            break; // Stop if there is a piece on the square
                        }
                    } else {
                        break; // Stop if the move is not possible
                    }

                    new_row += row_offset;
                    new_col += col_offset;
                }
            }
            break;
        }
        case 'Q': {
            // Rook-like moves (horizontal and vertical)
            int rook_directions[4][2] = {{-1, 0}, {1, 0}, {0, -1}, {0, 1}};
            int current_row = get_row();
            int current_col = get_col();

            for (const auto& dir : rook_directions) {
                int row_offset = dir[0];
                int col_offset = dir[1];

                int new_row = current_row + row_offset;
                int new_col = current_col + col_offset;

                while (new_row >= 0 && new_row < 8 && new_col >= 0 && new_col < 8) {
                    if (is_move_possible(board_state, new_row, new_col, false, false)) {
                        koord_candidates_and_is_capture.push_back(std::make_tuple(new_row, new_col, (board_state[new_row][new_col] != 0)));
                        if (board_state[new_row][new_col] != 0) {
                            break; // Stop if there is a piece on the square
                        }
                    } else {
                        break; // Stop if the move is not possible
                    }

                    new_row += row_offset;
                    new_col += col_offset;
                }
            }

            // Bishop-like moves (diagonals)
            int bishop_directions[4][2] = {{-1, -1}, {-1, 1}, {1, -1}, {1, 1}};

            for (const auto& dir : bishop_directions) {
                int row_offset = dir[0];
                int col_offset = dir[1];

                int new_row = current_row + row_offset;
                int new_col = current_col + col_offset;

                while (new_row >= 0 && new_row < 8 && new_col >= 0 && new_col < 8) {
                    if (is_move_possible(board_state, new_row, new_col, true, false)) {
                        koord_candidates_and_is_capture.push_back(std::make_tuple(new_row, new_col, (board_state[new_row][new_col] != 0)));
                        if (board_state[new_row][new_col] != 0) {
                            break; // Stop if there is a piece on the square
                        }
                    } else {
                        break; // Stop if the move is not possible
                    }

                    new_row += row_offset;
                    new_col += col_offset;
                }
            }
            break;
        }
        case 'K': { // King logic
            std::vector<std::tuple<int, int>> king_moves = {
                std::make_tuple(-1, -1), std::make_tuple(-1, 0), std::make_tuple(-1, 1),
                std::make_tuple(0, -1),  std::make_tuple(0, 1),
                std::make_tuple(1, -1),  std::make_tuple(1, 0), std::make_tuple(1, 1)
            };

            int current_row = get_row();
            int current_col = get_col();

            for (const auto& move : king_moves) {
                int new_row = current_row + std::get<0>(move);
                int new_col = current_col + std::get<1>(move);

                if (new_row >= 0 && new_row < 8 && new_col >= 0 && new_col < 8) {
                    if (is_move_possible(board_state, new_row, new_col, true, false)) {
                        koord_candidates_and_is_capture.push_back(std::make_tuple(new_row, new_col, (board_state[new_row][new_col] != 0)));
                    }
                }
            }

            break;
        }
    }
    return koord_candidates_and_is_capture;
}


bool Chess_Piece::is_en_passant_possible(const int board[8][8], int target_coord_row, int target_coord_col, bool is_capture, bool is_defense) const {
    if(getPieceType() != 'P') {
        return false;
    }
    if(color == "white") {
        if(get_row() == 4) {

            if (target_coord_col == get_col() + 1 && abs(board[get_row()][get_col()+1]) == 1) {
                return true;
            }
            if (target_coord_col == get_col() - 1 && abs(board[get_row()][get_col()-1]) == 1) {
                return true;
            }
        }
    }
    else {
        if(get_row() == 3) {
            if (target_coord_col == get_col() + 1 && abs(board[get_row()][get_col()+1]) == 1) {
                return true;
            }
            if (target_coord_col == get_col() - 1 && abs(board[get_row()][get_col()-1]) == 1) {
                return true;
            }
        }
    }
    return false;
}