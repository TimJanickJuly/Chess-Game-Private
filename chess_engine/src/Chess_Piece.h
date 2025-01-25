#ifndef CHESS_PIECE_H
#define CHESS_PIECE_H

#include <cstdint>
#include <string>
#include <cmath>
#include <algorithm>
#include <vector>

class Chess_Piece {
public:
    Chess_Piece(int x_coord, int y_coord, const std::string& color, char type)
        : x_coord(x_coord), y_coord(y_coord), color(color), type(type) {}

    int get_row() const { return x_coord; }
    int get_col() const { return y_coord; }
    std::string getColor() const { return color; }
    char getPieceType() const { return type; }

    void set_row(int x) { x_coord = x; }
    void set_col(int y) { y_coord = y; }
    void setColor(const std::string& c) { color = c; }
    void setPieceType(char t) { type = t; }

    bool is_move_possible(const int board[8][8], int target_coord_row, int target_coord_col, bool is_capture, bool is_defense) const;
    bool is_pawn_move_possible(const int board[8][8], int target_coord_row, int target_coord_col, bool is_capture, bool is_defense) const;
    bool is_knight_move_possible(const int board[8][8], int target_coord_row, int target_coord_col, bool is_capture) const;
    bool is_bishop_move_possible(const int board[8][8], int target_coord_row, int target_coord_col, bool is_capture, bool is_defense) const;
    bool is_rook_move_possible(const int board[8][8], int target_coord_row, int target_coord_col, bool is_capture, bool is_defense) const;
    bool is_queen_move_possible(const int board[8][8], int target_coord_row, int target_coord_col, bool is_capture, bool is_defense) const;
    bool is_king_move_possible(const int board[8][8], int target_coord_row, int target_coord_col, bool is_capture) const;
    bool is_target_valid(const int board[8][8], int target_row, int target_col, int piece_color, bool is_capture, bool is_defense) const;
    bool is_path_clear(const int board[8][8], int start_row, int start_col, int end_row, int end_col) const ;
    bool is_en_passant_possible(const int board[8][8], int target_coord_row, int target_coord_col, bool is_capture, bool is_defense) const;

    std::vector<std::tuple<int, int, bool>> get_available_coords_to_move_to(
    int active_player, const int board_state[8][8]);
private:
    int x_coord;
    int y_coord;
    std::string color;
    char type;
};

#endif // CHESS_PIECE_H
