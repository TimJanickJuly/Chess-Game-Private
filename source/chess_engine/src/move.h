#ifndef MOVE_H
#define MOVE_H

#include <iostream>
#include <unordered_map>

class Move {
public:
    // Konstruktor mit neuen Feldern
    Move(bool is_legal_move = false, int row_start = -1, int col_start = -1,
         int row_target = 0, int col_target = 0,
         std::string is_castling_move = "None", bool is_capture = false, bool is_difficult = false,
         char piece_to_move = 'X', bool is_check = false, bool is_mate = false, bool en_passant = false, bool promotion = false, char promotion_t = 'X')
        : is_legal_move(is_legal_move), row_start(row_start), col_start(col_start),
          row_target(row_target), col_target(col_target),
          is_castling_move(is_castling_move), is_capture(is_capture), is_difficult(is_difficult),
          piece_to_move(piece_to_move), is_check(is_check), is_mate(is_mate), en_passant(en_passant), is_promotion(promotion), promotion_type(promotion_t) {}


    // Getter-Methoden
    bool getIsLegalMove() const;
    int get_row_CoordStart() const;
    int get_col_CoordStart() const;
    int get_row_CoordTarget() const;
    int get_col_CoordTarget() const;
    std::string getIsCastlingMove() const;
    bool getIsCapturingMove() const;
    bool getIsDifficultMove() const;
    char getPieceToMove() const;
    bool getIsCheck() const;
    bool getIsMate() const;

    // Setter-Methoden
    void setIsLegalMove(bool legal);
    void set_row_CoordStart(int x_start);
    void set_col_CoordStart(int y_start);
    void set_row_CoordTarget(int x_target);
    void set_col_CoordTarget(int y_target);
    void setIsCastlingMove(std::string castling);
    void setIsCapturingMove(bool capturing);
    void setIsDifficultMove(bool difficult);
    void setPieceToMove(char piece);
    void setIsCheck(bool check);
    void setIsMate(bool mate);
    void printMove() const;

    static std::unordered_map<char, int> dict_col_char_to_coord;
    static std::unordered_map<char, int> dict_row_char_to_coord;

    static std::unordered_map<int, char> dict_col_coord_to_char;
    static std::unordered_map<int, char> dict_row_coord_to_char;

    std::string get_algebraic_chess_notation() const;


    static Move process_move_syntax(const std::string &str_player_move);
    //private:
    static bool is_difficult_move(const std::string& input);
    static bool is_capturing_move(const std::string& move);
    static bool is_legal_syntax_move(const std::string& input);
    static bool is_piece_move(const std::string& player_move);
    static bool is_en_passant(const std::string& move);
    static bool is_promotion_syntax(const std::string& input);
public:
    bool is_legal_move;
    int row_start;
    int col_start;
    int row_target;
    int col_target;
    std::string is_castling_move;
    bool is_capture;
    bool is_difficult;
    char piece_to_move;
    bool is_check;
    bool is_mate;
    bool en_passant;
    bool is_promotion;
    char promotion_type;

};

#endif // MOVE_H
