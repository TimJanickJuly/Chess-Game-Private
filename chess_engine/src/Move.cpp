#include "move.h"
#include <regex>
#include <set>


// Getter-Methoden
bool Move::getIsLegalMove() const { return is_legal_move; }
int Move::get_row_CoordStart() const { return row_start; }
int Move::get_col_CoordStart() const { return col_start; }
int Move::get_row_CoordTarget() const { return row_target; }
int Move::get_col_CoordTarget() const { return col_target; }
std::string Move::getIsCastlingMove() const { return is_castling_move; }
bool Move::getIsCapturingMove() const { return is_capture; }
bool Move::getIsDifficultMove() const { return is_difficult; }
char Move::getPieceToMove() const { return piece_to_move; }
bool Move::getIsCheck() const { return is_check; }
bool Move::getIsMate() const { return is_mate; }

// Setter-Methoden
void Move::setIsLegalMove(bool legal) { is_legal_move = legal; }
void Move::set_row_CoordStart(int x_start) { row_start = x_start; }
void Move::set_col_CoordStart(int y_start) { col_start = y_start; }
void Move::set_row_CoordTarget(int x_target) { row_target = x_target; }
void Move::set_col_CoordTarget(int y_target) { col_target = y_target; }
void Move::setIsCastlingMove(std::string castling) { is_castling_move = castling; }
void Move::setIsCapturingMove(bool capturing) { is_capture = capturing; }
void Move::setIsDifficultMove(bool difficult) { is_difficult = difficult; }
void Move::setPieceToMove(char piece) { piece_to_move = piece; }
void Move::setIsCheck(bool check) { is_check = check; }
void Move::setIsMate(bool mate) { is_mate = mate; }

// Print-Funktion (optional)
void Move::printMove() const {
    std::cout << "Legal Move: " << std::boolalpha << is_legal_move << "\n"
              << "Start Position: (" << col_start << ", " << row_start << ")\n"
              << "Target Position: (" << row_target << ", " << col_target << ")\n"
              << "Castling Move: " << is_castling_move << "\n"
              << "Capturing Move: " << is_capture << "\n"
              << "Difficult Move: " << is_difficult << "\n"
              << "Piece to Move: " << piece_to_move << "\n"
              << "Check: " << is_check << "\n"
              << "Mate: " << is_mate << "\n"
    << "promotion: " << is_promotion << "\n"
    << "e.p.: " << en_passant << "\n";
}
std::string Move::get_algebraic_chess_notation() const {

    if (!is_legal_move) {
        return "Tryed to print invalid Move";
    }

    if (getIsCastlingMove() == "short") {
        return "o-o";
    }
    if (getIsCastlingMove() == "long") {
        return "o-o-o";
    }

    std::string result;

    char char_to_write;
    bool write_switch;

    if (getPieceToMove() != 'P') {
        result += getPieceToMove();
    }

    if(is_difficult) {
        if(get_col_CoordStart() != -1) {
            result += dict_col_coord_to_char.at(get_col_CoordStart());
        }

        if(get_row_CoordStart() != -1) {
            result += dict_row_coord_to_char.at(get_row_CoordStart());
        }
    }

    if(getIsCapturingMove()) {
        result += 'x';
    }

    char target_col = dict_col_coord_to_char.at(col_target);
    char target_row = dict_row_coord_to_char.at(row_target);

    result += target_col;
    result += target_row;

    if(is_promotion) {
        result += '=';
        result += promotion_type;
    }

    if (is_mate) {
        result += '#';
    }
    else if (is_check) {
        result += '+';
    }


    return result;
}


std::unordered_map<char, int> Move::dict_col_char_to_coord = {
    {'a', 0}, {'b', 1}, {'c', 2}, {'d', 3}, {'e', 4},
    {'f', 5}, {'g', 6}, {'h', 7}
};
std::unordered_map<char, int> Move::dict_row_char_to_coord = {
    {'1', 0}, {'2', 1}, {'3', 2}, {'4', 3}, {'5', 4},
    {'6', 5}, {'7', 6}, {'8', 7}
};

std::unordered_map<int, char> Move::dict_col_coord_to_char = {
    {0, 'a'}, {1, 'b'}, {2, 'c'}, {3, 'd'}, {4, 'e'},
    {5, 'f'}, {6, 'g'}, {7, 'h'}
};
std::unordered_map<int, char> Move::dict_row_coord_to_char  = {
    {0, '1'}, {1, '2'}, {2, '3'}, {3, '4'}, {4, '5'},
    {5, '6'}, {6, '7'}, {7, '8'}
};


void remove_x(std::string& str) {
    std::string result;
    for (char ch : str) {
        if (ch != 'x') {
            result += ch;
        }
    }
    str = result;
}

bool Move::is_difficult_move(const std::string& move) {
    int digit_count = 0;
    int letter_count = 0;

    for(char c : move) {
        if (isdigit(c)) {
            digit_count++;
        } else if (c >= 'a' && c <= 'h') {
            letter_count++;
        }

        if (digit_count >= 2 || letter_count >= 2) {
            return true;
        }
    }

    return false;
}

bool Move::is_capturing_move(const std::string& move) {
    return move.find('x') != std::string::npos;
}


bool Move::is_legal_syntax_move(const std::string& input) {
        std::string move_pattern = R"([KQRBNP]?(([a-h]|[1-8])|[a-h][1-8])?[x]?[a-h][1-8][#]?[+]?)";
    std::string castling_pattern = R"((O-O|O-O-O|o-o|o-o-o)$)";
    std::string promotion_pattern = R"((([a-h]|[1-8])|[a-h][1-8])?[x]?[a-h][1-8]=[KQRBN][#]?[+]?)";
    std::regex move_re(move_pattern);
    std::regex castling_re(castling_pattern);
    std::regex promotion_re(promotion_pattern);
    return std::regex_match(input, move_re) || std::regex_match(input, castling_re) || std::regex_match(input,promotion_re);
}

bool Move::is_promotion_syntax(const std::string& input) {
    std::string promotion_pattern = R"((([a-h]|[1-8])|[a-h][1-8])?[x]?[a-h][1-8]=[KQRBN][#]?[+]?)";
    std::regex promotion_re(promotion_pattern);
    return std::regex_match(input,promotion_re);
}

bool Move::is_piece_move(const std::string& player_move) {
    std::string piece_names = "RNBQK";
    return piece_names.find(player_move[0]) != std::string::npos;
}

bool Move::is_en_passant(const std::string& move) {
    if (move.length() < 5) {
        return false;
    }
    std::string lastFourChars = move.substr(move.length() - 5);
    return lastFourChars == " e.p.";
}
//


Move Move::process_move_syntax(const std::string &str_player_move) {
    Move move = Move();

    std::string str_player_move_copy = str_player_move;

    if (is_en_passant(str_player_move_copy)) {
        str_player_move_copy.resize(str_player_move_copy.length() - 5);
        move.en_passant = true;
    }

    if (str_player_move_copy.empty() || str_player_move_copy.length() >= 10) {
        return move;
    }

    if (!is_legal_syntax_move(str_player_move_copy)) {
        return move;
    }

    if (str_player_move_copy == "o-o" || str_player_move_copy == "O-O") {
        move.setIsCastlingMove("short");
        move.setIsLegalMove(true);
        return move;
    }
    if (str_player_move_copy == "o-o-o" || str_player_move_copy == "O-O-O") {
        move.setIsCastlingMove("long");
        move.setIsLegalMove(true);
        return move;
    }

    if (str_player_move_copy.back() == '#' || str_player_move_copy.back() == '+') {
        if (str_player_move_copy.back() == '#') {
            move.setIsMate(true);
        } else {
            move.setIsCheck(true);
        }
        str_player_move_copy.pop_back();
    }

    if(is_promotion_syntax(str_player_move)) {
        move.is_promotion = true;
        move.promotion_type = str_player_move_copy.back();
        str_player_move_copy.pop_back();
        str_player_move_copy.pop_back();
    }

    if (is_difficult_move(str_player_move_copy)) {
        move.setIsDifficultMove(true);
    } else {
        move.setIsDifficultMove(false);
    }

    if (str_player_move_copy.find('x') != std::string::npos) {
        move.setIsCapturingMove(true);
    } else {
        move.setIsCapturingMove(false);
    }

    if (is_piece_move(str_player_move_copy)) {
        move.setPieceToMove(str_player_move_copy[0]);
        str_player_move_copy.erase(0, 1);
    } else {
        move.setPieceToMove('P');
    }

    if (!move.getIsDifficultMove()) {
        if (str_player_move_copy[0] == 'x') {
            str_player_move_copy.erase(0, 1);
        }

        move.set_col_CoordTarget(dict_col_char_to_coord.at(str_player_move_copy[0]));
        move.set_row_CoordTarget(dict_row_char_to_coord.at(str_player_move_copy[1]));
    } else if (move.getIsDifficultMove()) {
        static const std::set<char> valid_chars = {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'};
        static const std::set<char> valid_digits = {'1', '2', '3', '4', '5', '6', '7', '8'};

        if (valid_chars.find(str_player_move_copy[0]) != valid_chars.end()) {
            move.set_col_CoordStart(dict_col_char_to_coord.at(str_player_move_copy[0]));
            str_player_move_copy.erase(0, 1);
        }
        if (valid_digits.find(str_player_move_copy[0]) != valid_digits.end()) {
            move.set_row_CoordStart(dict_row_char_to_coord.at(str_player_move_copy[0]));
            str_player_move_copy.erase(0, 1);
        }
        if (str_player_move_copy[0] == 'x') {
            str_player_move_copy.erase(0, 1);
        }

        move.set_col_CoordTarget(dict_col_char_to_coord.at(str_player_move_copy[0]));
        move.set_row_CoordTarget(dict_row_char_to_coord.at(str_player_move_copy[1]));
    }
    if (move.en_passant && move.getPieceToMove() != 'P') {
        return move;
    }

    move.setIsLegalMove(true);
    return move;
}