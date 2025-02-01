//
// Created by tim.janick.july on 06.08.2024.
//
#include <iomanip>
#include "game.h"
#include <regex>
#include <algorithm>
#include "move.h"
#include <string>
#include <cctype>
#include "Chess_Piece.h"
#include <cassert>
#include <list>
#include "BoardHashMap.h"



// Game State handling


Game::Game() {
    last_move_status  = "---";

    game_state = "running";
    num_moves_played = 0;
    active_player = 1;

    white_king_pos = std::make_tuple(0, 4);
    black_king_pos = std::make_tuple(7, 4);
    
    is_active_player_in_check = false;
    is_passive_player_in_check = false;

    masked_coords = std::make_shared<std::tuple<int,int>>(-1,-1);
    en_passant_coords= std::make_shared<std::tuple<int,int>>(-1,-1);
    en_passant_option = false;
    en_passant_counter = -1;


    has_black_king_moved = false;
    has_white_king_moved = false;
    has_white_a_rook_moved = false;
    has_white_h_rook_moved = false;
    has_black_a_rook_moved = false;
    has_black_h_rook_moved = false;

    for (int i = 0; i <= 7; i++) {
        for (int j = 0; j <= 7; j++) {
            if (board_state[i][j] != EE) { // Annahme: EE steht für ein leeres Feld
                auto piece = create_piece(board_state[i][j], i, j);

                if (board_state[i][j] > 0) {
                    white_pieces.push_back(piece);
                } else {
                    black_pieces.push_back(piece);
                }
            }
        }
    }

    active_pieces = std::make_shared<std::vector<std::shared_ptr<Chess_Piece>>>(white_pieces);
    passive_pieces = std::make_shared<std::vector<std::shared_ptr<Chess_Piece>>>(black_pieces);
}


int Game::handle_turn(const std::string &str_player_move) {
    std::shared_ptr<Move> move = std::make_shared<Move>(Move::process_move_syntax(str_player_move));
    if (!move->is_legal_move) {
        return 1;
    }
    if (!consider_move(move)){ // tests if move is legal: if true: move was executed, if false: move was rejected
        return -1;
    }
    std::cout << "move successfully considered" << "\n";

    game_history_str.push_back(move->get_algebraic_chess_notation()); // log the move in game history

    std::cout << "in is player in check" << "\n";

    if(is_passive_player_in_check) {
        if (active_player > 0) {
            last_move_status = "Black has been put under check\n";
        }else {
            last_move_status = "White has been put under check\n";
        }
        std::cout << "in is checkmate" << "\n";
        if(is_checkmate()) {
            last_move_status = "Checkmate Detected\n";
            move->is_mate = true;
            if(active_player > 0) {
                game_state = "white wins";
            }
            else {
                game_state = "black wins";
            }
            return 0;
        }
    }
    else {
        std::cout << "in is stalemate" << "\n";
        if(is_stalemate()){
            last_move_status = "Stalemate Detected\n";
            game_state = "stalemate";
            return 0;
        }
        // to test if the same boardstate has occured for the 3rd time, each boardstate is stored in a hashmap with an ocurrence counter
        if(!game_history_hash_map.memorize_board_state(board_state)) {
            last_move_status = "Draw by repetition detected\n";
            game_state = "draw";
            return 0;
        }
    }
    std::cout << "after all checks" << "\n";
    clean_up_after_turn();
    switchPlayer();
    num_moves_played += 1;
    return 2;
}


void Game::switchPlayer() {
    active_player *= -1;
    std::swap(active_pieces, passive_pieces);
}
void Game::clean_up_after_turn() {
    static int cleanup_call_count = 0;
    cleanup_call_count++;

    masked_coords = std::make_shared<std::tuple<int,int>>(-1, -1);

    if (en_passant_option) {
        if (num_moves_played > en_passant_activation_move) {
            en_passant_coords = std::make_shared<std::tuple<int,int>>(-1, -1);
            en_passant_option = false;
            en_passant_counter = -1;
        }
    } else {
        en_passant_counter = -1;
        en_passant_coords = std::make_shared<std::tuple<int,int>>(-1, -1);
    }

    if (board_state[std::get<0>(white_king_pos)][std::get<1>(white_king_pos)] != 10) {
        for (const auto& piece : white_pieces) {
            if (piece->getPieceType() == 'K') {
                white_king_pos = std::make_tuple(piece->get_row(), piece->get_col());
            }
        }
    }
    if (board_state[std::get<0>(black_king_pos)][std::get<1>(black_king_pos)] != -10) {
        for (const auto& piece : black_pieces) {
            if (piece->getPieceType() == 'K') {
                black_king_pos = std::make_tuple(piece->get_row(), piece->get_col());
            }
        }
    }

    active_pieces = (active_player > 0)
                      ? std::make_shared<std::vector<std::shared_ptr<Chess_Piece>>>(white_pieces)
                      : std::make_shared<std::vector<std::shared_ptr<Chess_Piece>>>(black_pieces);
    passive_pieces = (active_player > 0)
                      ? std::make_shared<std::vector<std::shared_ptr<Chess_Piece>>>(black_pieces)
                      : std::make_shared<std::vector<std::shared_ptr<Chess_Piece>>>(white_pieces);
}



bool Game::consider_move(std::shared_ptr<Move> move) {
    // std::cout << "[DEBUG] consider_move() called with move: " << move->get_algebraic_chess_notation() << "\n";

    if (!move->is_legal_move) {
        // std::cout << "[DEBUG] Move syntax invalid.\n";
        last_move_status = "Invalid Move Syntax\n";
        return false;
    }
    
    int promotion_row = (active_player > 0) ? 7 : 0;
    if (move->is_promotion && (move->row_target != promotion_row || move->getPieceToMove() != 'P')) {
        // std::cout << "[DEBUG] Promotion move invalid: row_target (" << move->row_target << ") != promotion row (" << promotion_row << ") or piece != 'P'.\n";
        return false;
    }
    if (!move->is_promotion && move->row_target == promotion_row && move->getPieceToMove() == 'P') {
        // std::cout << "[DEBUG] Pawn reached promotion row without promotion flag.\n";
        return false;
    }

    // Handle Castling Moves
    if (move->is_castling_move == "short" || move->is_castling_move == "long") {
        // std::cout << "[DEBUG] Castling move detected: " << move->is_castling_move << "\n";
        if (move->is_castling_move == "short") {
            if (check_castle('s')) {
                // std::cout << "[DEBUG] Short castling allowed. Executing short castle.\n";
                execute_castle('s');
                return true;
            } else {
                // std::cout << "[DEBUG] Short castling not allowed.\n";
            }
        }
        if (move->is_castling_move == "long") {
            if (check_castle('l')) {
                // std::cout << "[DEBUG] Long castling allowed. Executing long castle.\n";
                execute_castle('l');
                return true;
            } else {
                // std::cout << "[DEBUG] Long castling not allowed.\n";
            }
        }
    }

    // Handle non-Castling Moves
    // std::cout << "[DEBUG] Handling non-castling move.\n";
    std::vector<std::shared_ptr<Chess_Piece>> possible_movers;
    for (const auto& piece : *active_pieces) {
        // std::cout << "[DEBUG] Checking active piece: " << piece->getPieceToMove() 
        //           << " at (" << piece->get_row() << "," << piece->get_col() << ")\n";
        if (piece->getPieceType() == move->piece_to_move) {
            bool move_possible = piece->is_move_possible(board_state, move->row_target, move->col_target, move->is_capture, false);
            // std::cout << "[DEBUG] is_move_possible for piece " << piece->getPieceToMove() << ": " 
            //           << (move_possible ? "true" : "false") << "\n";
            if (move_possible) {
                bool king_safe = !is_own_king_in_check_after_move(piece, move, board_state);
                // std::cout << "[DEBUG] is_own_king_in_check_after_move result: " << (king_safe ? "safe" : "in check") << "\n";
                if (king_safe) {
                    possible_movers.push_back(piece);
                    // std::cout << "[DEBUG] Piece added as possible mover.\n";
                }
            }
            else {
                // En passant check for Pawn
                if (piece->getPieceType() == 'P' &&
                    move->row_target == std::get<0>(*en_passant_coords) &&
                    move->col_target == std::get<1>(*en_passant_coords)) {
                    bool en_passant_possible = piece->is_en_passant_possible(board_state, move->row_target, move->col_target, move->is_capture, false);
                    // std::cout << "[DEBUG] is_en_passant_possible: " << (en_passant_possible ? "true" : "false") << "\n";
                    if (en_passant_possible && !is_own_king_in_check_after_move(piece, move, board_state)) {
                        possible_movers.push_back(piece);
                        // std::cout << "[DEBUG] Pawn en passant move accepted.\n";
                    }
                }
            }
        }
    }

    if (possible_movers.empty()) {
        // std::cout << "[DEBUG] No possible mover found. Move rejected.\n";
        return false;
    }

    bool row_unique = true;
    bool col_unique = true;
    // If more than one piece can perform the move, try to filter by the specified starting coordinates.
    if (possible_movers.size() > 1) {
        // std::cout << "[DEBUG] Multiple possible movers found (" << possible_movers.size() << "). Attempting to filter using start coordinates.\n";
        move->is_difficult = true;  
        if (possible_movers.at(0)->get_row() == possible_movers.at(1)->get_row()) {
            row_unique = false;
            // std::cout << "[DEBUG] Row not unique among possible movers.\n";
        }
        if (possible_movers.at(0)->get_col() == possible_movers.at(1)->get_col()) {
            col_unique = false;
            // std::cout << "[DEBUG] Column not unique among possible movers.\n";
        }

        for (auto it = possible_movers.begin(); it != possible_movers.end();) {
            const auto& piece = *it;
            int piece_row = piece->get_row();
            int piece_col = piece->get_col();
            // std::cout << "[DEBUG] Checking piece at (" << piece_row << ", " << piece_col << ").\n";

            bool rowMismatch = (move->get_row_CoordStart() != -1 && piece_row != move->get_row_CoordStart());
            bool colMismatch = (move->get_col_CoordStart() != -1 && piece_col != move->get_col_CoordStart());

            // std::cout << "row start " << move->get_row_CoordStart() << "  col start " << move->get_col_CoordStart() << "\n";

            if (rowMismatch || colMismatch) {
                // std::cout << "[DEBUG] Removing piece at (" << piece_row << ", " << piece_col << ") due to ";
                // if (rowMismatch) {
                //     std::cout << "row mismatch (expected " << move->get_row_CoordStart() << ", got " << piece_row << ")";
                // }
                // if (rowMismatch && colMismatch) {
                //     std::cout << " and ";
                // }
                // if (colMismatch) {
                //     std::cout << "column mismatch (expected " << move->get_col_CoordStart() << ", got " << piece_col << ")";
                // }
                // std::cout << ".\n";
                it = possible_movers.erase(it);
            } else {
                // std::cout << "[DEBUG] Keeping piece at (" << piece_row << ", " << piece_col << ").\n";
                ++it;
            }
        }
    }
    else if (possible_movers.size() == 1) {
        move->is_difficult = false;
    }

    if (possible_movers.size() != 1) {
        // std::cout << "[DEBUG] Ambiguous mover selection: " << possible_movers.size() << " candidates remain. Move rejected.\n";
        return false;
    }

    std::shared_ptr<Chess_Piece> piece_to_move_ptr = possible_movers.at(0);
    // std::cout << "[DEBUG] Selected mover: " << piece_to_move_ptr->getPieceToMove() 
    //           << " at (" << piece_to_move_ptr->get_row() << "," << piece_to_move_ptr->get_col() << ")\n";

    // For clean move notation in game history, update starting coordinates if needed.
    if (move->is_difficult) {
        if (!row_unique) {
            move->row_start = piece_to_move_ptr->get_row();
            // std::cout << "[DEBUG] Updating move row_start to " << move->row_start << "\n";
        }
        if (!col_unique) {
            move->col_start = piece_to_move_ptr->get_col();
            // std::cout << "[DEBUG] Updating move col_start to " << move->col_start << "\n";
        }
    }

    // Handle en passant option for Pawn double-step moves.
    if (move->getPieceToMove() == 'P' && abs(piece_to_move_ptr->get_row() - move->row_target) == 2) {
        en_passant_option = true;
        en_passant_counter = 0;
        en_passant_activation_move = num_moves_played;
        int en_passant_row = (active_player > 0) ? 2 : 5;
        en_passant_coords = std::make_shared<std::tuple<int,int>>(std::make_tuple(en_passant_row, move->col_target));
    }

    // std::cout << "[DEBUG] Executing move.\n";
    execute_move(piece_to_move_ptr, move);

    if (move->is_promotion) {
        // std::cout << "[DEBUG] Move is a promotion. Promoting pawn to " << move->promotion_type << ".\n";
        promote_pawn(piece_to_move_ptr, move->promotion_type);
    }

    std::tuple<int,int> passive_king_pos = (active_player > 0) ? black_king_pos : white_king_pos;
    // std::cout << "[DEBUG] Passive king position: (" << std::get<0>(passive_king_pos) << "," << std::get<1>(passive_king_pos) << ")\n";
    is_active_player_in_check = false;
    is_passive_player_in_check = is_square_attacked(passive_king_pos, active_pieces, board_state, false);
    // std::cout << "[DEBUG] is_passive_player_in_check: " << (is_passive_player_in_check ? "true" : "false") << "\n";
    if (is_passive_player_in_check) {
        move->is_check = true;
        // std::cout << "[DEBUG] Move results in check.\n";
    }
    // std::cout << "[DEBUG] consider_move() returning true.\n";
    return true;
}



bool Game::is_own_king_in_check_after_move(
    const std::shared_ptr<Chess_Piece> piece_to_move,
    std::shared_ptr<Move> move,
    int board_state[8][8]
) {
    // Determine the opponent's pieces based on the active player.
    std::shared_ptr<std::vector<std::shared_ptr<Chess_Piece>>> attacking_pieces =
        (active_player > 0)
            ? std::make_shared<std::vector<std::shared_ptr<Chess_Piece>>>(black_pieces)
            : std::make_shared<std::vector<std::shared_ptr<Chess_Piece>>>(white_pieces);

    // Save original values at the start and target squares.
    int start_row = piece_to_move->get_row();
    int start_col = piece_to_move->get_col();
    int target_row = move->get_row_CoordTarget();
    int target_col = move->get_col_CoordTarget();
    int original_start = board_state[start_row][start_col];
    int original_target = board_state[target_row][target_col];

    // Determine the numeric value of the piece to move.
    int piece_value;
    switch (std::abs(piece_to_move->getPieceType())) {
        case 'P': piece_value = 1; break;
        case 'N': piece_value = 3; break;
        case 'B': piece_value = 4; break;
        case 'R': piece_value = 5; break;
        case 'Q': piece_value = 9; break;
        case 'K': piece_value = 10; break;
        default: throw std::invalid_argument("Invalid Piece Type");
    }
    if (piece_to_move->getColor() == "black") {
        piece_value *= -1;
    }

    // If the move is a capture, set the masked coordinates to the target square.
    // This will cause is_square_attacked to skip any piece located at (target_row, target_col).
    if (original_target != 0) {
        masked_coords = std::make_shared<std::tuple<int, int>>(target_row, target_col);
    } else {
        masked_coords = std::make_shared<std::tuple<int, int>>(-1, -1);
    }

    // Simulate the move in-place:
    // 1. Remove the piece from its start square.
    board_state[start_row][start_col] = 0;
    // 2. Place the piece on the target square.
    board_state[target_row][target_col] = piece_value;

    // Determine the defending king's position.
    // If the king is moving, use the target square; otherwise, use the stored king position.
    std::tuple<int, int> defending_king_pos;
    if (move->getPieceToMove() == 'K') {
        defending_king_pos = std::make_tuple(target_row, target_col);
    } else {
        defending_king_pos = (active_player > 0) ? white_king_pos : black_king_pos;
    }

    // Check if the defending king's square is attacked in the updated board state.
    bool in_check = is_square_attacked(defending_king_pos, attacking_pieces, board_state, false);

    // Undo the move: restore the original board state.
    board_state[start_row][start_col] = original_start;
    board_state[target_row][target_col] = original_target;

    // Clear the mask.
    masked_coords = std::make_shared<std::tuple<int, int>>(-1, -1);

    return in_check;
}



// necessary to determine checkmate
bool Game::is_opponents_king_move_legal(
    const std::shared_ptr<Chess_Piece> defending_king_ptr,
    const int board_state[8][8], int new_row_king, int new_col_king
) {
    auto attacking_pieces = active_pieces;
    auto defending_king_pos = (active_player > 0)? black_king_pos : white_king_pos;

    masked_coords = std::make_shared<std::tuple<int,int>>(std::make_tuple(new_row_king, new_col_king));
    bool result = !is_square_attacked(std::make_tuple(new_row_king, new_col_king), attacking_pieces, board_state, true);
    masked_coords = std::make_shared<std::tuple<int,int>>(std::make_tuple(-1, -1));

    return result;
    }

// necessary to determine a stalemate by no more available move + no check
bool Game::is_opponents_move_legal(
    const std::shared_ptr<Chess_Piece> piece_to_move_ptr,
    const int board_state[8][8],
    int new_row,
    int new_col
) {

    if (piece_to_move_ptr->getPieceType() == 'P' && board_state[new_row][new_col] == 0)
    {
        if (!(new_row == std::get<0>(*en_passant_coords) &&
                    new_col == std::get<1>(*en_passant_coords))  ){
            return false;
        } 
    }

    auto attacking_pieces = active_pieces;
    auto defending_king_pos = (active_player > 0)? black_king_pos : white_king_pos;


    int board_state_copy[8][8];
    memcpy(board_state_copy, board_state, sizeof(board_state_copy));

    int start_row = piece_to_move_ptr->get_row();
    int start_col = piece_to_move_ptr->get_col();

    int piece_value;
    switch (abs(piece_to_move_ptr->getPieceType())) {
        case 'P': piece_value = 1; break;
        case 'N': piece_value = 3; break;
        case 'B': piece_value = 4; break;
        case 'R': piece_value = 5; break;
        case 'Q': piece_value = 9; break;
        case 'K': piece_value = 10; break;
        default: throw std::invalid_argument("Invalid Piece Type");
    }
    if (piece_to_move_ptr->getColor() == "black"){piece_value *= -1;}

    board_state_copy[start_row][start_col] = 0;
    board_state_copy[new_row][new_col] = piece_value;

    masked_coords = std::make_shared<std::tuple<int,int>>(std::make_tuple(new_row, new_col));
    bool result = !is_square_attacked(std::make_tuple(std::get<0>(defending_king_pos), std::get<1>(defending_king_pos)), attacking_pieces, board_state_copy, true);
    masked_coords = std::make_shared<std::tuple<int,int>>(std::make_tuple(-1, -1));

    return result;
}

// logic to determine if a king is in check
bool Game::is_square_attacked(const std::tuple<int, int> &square,
                              std::shared_ptr<std::vector<std::shared_ptr<Chess_Piece>>> attacking_pieces,
                              const int board_state[8][8], bool is_defense) const{

    int row = std::get<0>(square);
    int col = std::get<1>(square);
    for (const auto &piece: *attacking_pieces) {
        if (!(piece->get_row() == std::get<0>(*masked_coords) && piece->get_col() == std::get<1>(*masked_coords))) {
            if (piece->is_move_possible(board_state, row, col, true, is_defense)) {
                return true;
            }
        }
    }
    return false;
}

// puts moving piece on new positon and removes captured pices + handles edgecases en passant and pawn promotion
void Game::execute_move(std::shared_ptr<Chess_Piece> piece, std::shared_ptr<Move> move) {

    int piece_value;

    switch (piece->getPieceType()) {
        case 'P': piece_value = 1; break; // Pawn
        case 'N': piece_value = 3; break; // Knight
        case 'B': piece_value = 4; break; // Bishop
        case 'R': piece_value = 5; break; // Rook
        case 'Q': piece_value = 9; break; // Queen
        case 'K': piece_value = 10; break; // King
        default: throw std::invalid_argument("Unbekannter Figurtyp");
    }

    if (piece->getPieceType() == 'R') {
        int rook_row = (active_player > 0) ? 0 : 7;
        if(!has_black_a_rook_moved && piece->get_row() == rook_row && piece->get_col() == 0) {
            has_black_a_rook_moved = true;
        }
        if(!has_black_h_rook_moved && piece->get_row() == rook_row && piece->get_col() == 7) {
            has_black_h_rook_moved = true;
        }

    }
    if (piece->getPieceType() == 'K') {
        if (active_player > 0) {
            has_white_king_moved = true;
        }else {
            has_black_king_moved = true;
        }
    }

    if (piece->getColor() == "black") {
        piece_value *= -1;
    }

    bool en_passant = false;

    //test for en passant
    if(piece->getPieceType() == 'P' && board_state[move->row_target][move->col_target] == 0 && piece->get_col() != move->col_target) {
        en_passant = true;
    }

    // Setze die Zielposition auf die Figur
    board_state[move->get_row_CoordTarget()][move->get_col_CoordTarget()] = piece_value;

    // Leere die Startposition
    board_state[piece->get_row()][piece->get_col()] = 0;

    // Aktualisiere die Position der Figur
    piece->set_row(move->get_row_CoordTarget());
    piece->set_col(move->get_col_CoordTarget());

    // Aktualisiere die Position der Könige, falls es sich um einen König handelt
    if (piece->getPieceType() == 'K') {
        if (piece->getColor() == "white") {
            white_king_pos = std::make_tuple(move->get_row_CoordTarget(), move->get_col_CoordTarget());
        } else {
            black_king_pos = std::make_tuple(move->get_row_CoordTarget(), move->get_col_CoordTarget());
        }

    }

    // If a piece has to be captured, then remove it for the piece list
    if (board_state[move->row_target][move->col_target] != 0) {
        //game_history_hash_map.clear_hashmap_history();  // hashmap can be cleared because board_state repetion is impossible after a piece has been captured

        std::vector<std::shared_ptr<Chess_Piece>>* opponent_pieces = (active_player > 0) ? &black_pieces : &white_pieces;

        auto it = std::find_if(opponent_pieces->begin(), opponent_pieces->end(), [&](const std::shared_ptr<Chess_Piece>& p) {
            return p->get_row() == move->get_row_CoordTarget() && p->get_col()== move->get_col_CoordTarget();
        });

        if (it != opponent_pieces->end()) {
            opponent_pieces->erase(it);
        }
    }
    if (en_passant) {
        int direction = (active_player > 0)? 1 : -1;
        board_state[piece->get_row() - direction][piece->get_col()] = 0;
        std::vector<std::shared_ptr<Chess_Piece>>* opponent_pieces = (active_player > 0) ? &black_pieces : &white_pieces;

        auto it = std::find_if(opponent_pieces->begin(), opponent_pieces->end(), [&](const std::shared_ptr<Chess_Piece>& p) {
            return p->get_row() == move->get_row_CoordTarget() - direction && p->get_col()== move->get_col_CoordTarget();
        });

        if (it != opponent_pieces->end()) {
            opponent_pieces->erase(it);
        }
    }
}

// returns true if active player is allowed to castle, input: 'l' for long castle, 's' for short castle
bool Game::check_castle(char castle_type) {
    auto active_king_pos = (active_player > 0) ? white_king_pos : black_king_pos;
    bool active_player_has_king_moved = (active_player > 0) ? has_white_king_moved : has_black_king_moved;
    bool active_player_a_rook_moved = (active_player > 0) ? has_white_a_rook_moved : has_black_a_rook_moved;
    bool active_player_h_rook_moved = (active_player > 0) ? has_white_h_rook_moved : has_black_h_rook_moved;
    if (castle_type == 's') { 
        if (active_player_has_king_moved) {
            last_move_status = "Error: King has been moved\n";
            return false;
        }
        if (active_player_h_rook_moved) {
            last_move_status = "Error: h rook has been moved\n";
            return false;
        }
    }
    else if (castle_type == 'l') {
        if (active_player_has_king_moved) {
            last_move_status = "Error: King has been moved\n";
            return false;
        }
        if (active_player_a_rook_moved) {
            last_move_status = "Error: a rook has been moved\n";
            return false;
        }
    }


    int rook_row = (active_player > 0) ? 0 : 7;
    int rook_col = (castle_type == 's') ? 7 : 0;

    if (abs(board_state[rook_row][rook_col]) != 5) {
        last_move_status = "rook is missing\n";
        return false;
    }
    if (abs(board_state[std::get<0>(active_king_pos)][std::get<1>(active_king_pos)]) != 10) {
        last_move_status = "king is missing\n";
        return false;
    }
    if (castle_type == 's') {

        for(int i = 0; i < 3; i++) {
            auto square_to_check = std::make_tuple(std::get<0>(active_king_pos), std::get<1>(active_king_pos) + i);
            if(is_square_attacked(square_to_check, passive_pieces, board_state, false)) {
                last_move_status = "king cant castle over attacked squares\n";
                return false;
            }
            if(i > 0 && board_state[std::get<0>(square_to_check)][std::get<1>(square_to_check)] != 0) { // check if squares are ampty but leave out kings and rooks square
                last_move_status = "castle path is blocked\n";
                return false;
            }
        }


    }
    if (castle_type == 'l') {
        for(int i = 0; i < 4; i++) {
            auto square_to_check = std::make_tuple(std::get<0>(active_king_pos), std::get<1>(active_king_pos) - i);
            if(is_square_attacked(square_to_check, passive_pieces, board_state, false)) {

                return false;
            }
            if(i > 0 && board_state[std::get<0>(square_to_check)][std::get<1>(square_to_check)] != 0) { // check if squares are ampty but leave out kings and rooks square
                return false;
            }
        }
    }
    return true;
}

void Game::execute_castle(char castle_type) {
    int rook_row = (active_player > 0) ? 0 : 7;
    int rook_col = (castle_type == 's') ? 7 : 0;
    std::shared_ptr<Chess_Piece> king;
    std::shared_ptr<Chess_Piece> rook;
    auto active_king_pos = (active_player > 0) ? white_king_pos : black_king_pos;

    auto it_rook = std::find_if(active_pieces->begin(), active_pieces->end(),
                                [=](const std::shared_ptr<Chess_Piece>& piece) {
                                    return piece->getPieceType() == 'R' &&
                                           piece->get_row() == rook_row &&
                                           piece->get_col()== rook_col;
                                });

    if (it_rook != active_pieces->end()) {
        rook = *it_rook;
    } else {
        std::cerr << "Rook not found for castling!" << std::endl;
        return;
    }

    auto it_king = std::find_if(active_pieces->begin(), active_pieces->end(),
                                [=](const std::shared_ptr<Chess_Piece> piece) {
                                    return piece->getPieceType() == 'K' &&
                                           piece->get_row() == std::get<0>(active_king_pos) &&
                                           piece->get_col()== std::get<1>(active_king_pos);
                                });

    if (it_king != active_pieces->end()) {
        king = *it_king;
    } else {
        std::cerr << "King not found for castling!" << std::endl;
        return;
    }

    if (active_player > 0) {
        has_white_king_moved = true;
        if(castle_type == 's') {
            has_white_h_rook_moved = true;
        }
        if(castle_type == 'l') {
            has_white_a_rook_moved = true;
        }
    }
    else {
        has_black_king_moved = true;
        if(castle_type == 's') {
            has_black_h_rook_moved = true;
        }
        if(castle_type == 'l') {
            has_black_a_rook_moved = true;
        }
    }

        // SWAP KING AND ROOK ON BOARD
    if (castle_type == 's') {
        king->set_col(6);
        rook->set_col(5);
        board_state[rook_row][4] = 0; 
        board_state[rook_row][7] = 0; 
        board_state[rook_row][5] = (active_player > 0) ? 5 : -5;
        board_state[rook_row][6] = (active_player > 0) ? 10 : -10;

        if(active_player > 0) {
            white_king_pos = std::make_tuple(0,6);
        }else {
            black_king_pos = std::make_tuple(7,6);
        }

    } else if (castle_type == 'l') {
        king->set_col(2);
        rook->set_col(3);
        board_state[rook_row][4] = 0;
        board_state[rook_row][0] = 0;
        board_state[rook_row][3] = (active_player > 0) ? 5 : -5;
        board_state[rook_row][2] = (active_player > 0) ? 10 : -10;
        if(active_player > 0) {
            white_king_pos = std::make_tuple(0,2);
        }else {
            black_king_pos = std::make_tuple(7,2);
        }
    }
}


bool Game::is_checkmate()
{
    auto defending_king_pos = (active_player > 0) ? black_king_pos : white_king_pos;
    int king_row = std::get<0>(defending_king_pos);
    int king_col = std::get<1>(defending_king_pos);



    auto attacking_pieces = (active_player > 0 ) ? std::make_shared<std::vector<std::shared_ptr<Chess_Piece>>>(white_pieces) : std::make_shared<std::vector<std::shared_ptr<Chess_Piece>>>(black_pieces);
    auto defending_pieces = (active_player > 0 ) ? std::make_shared<std::vector<std::shared_ptr<Chess_Piece>>>(black_pieces) : std::make_shared<std::vector<std::shared_ptr<Chess_Piece>>>(white_pieces);


    // Find all Pieces that are checking the king: min 1, max 2 (more than double check not possible)
    std::vector<std::shared_ptr<Chess_Piece>> attacking_pieces_that_give_check;
    for (const auto& piece : *attacking_pieces) {
        if (piece->is_move_possible(board_state, king_row, king_col,true, false)) {
        attacking_pieces_that_give_check.push_back(piece);
        }
    }

    //find the pointer to the king object
    std::shared_ptr<Chess_Piece> defending_king_ptr;
    for (const auto& piece : *defending_pieces) {
        if (piece->get_row() == king_row && piece->get_col() == king_col) {
            defending_king_ptr = piece;
        }
    }
    assert(defending_king_ptr != nullptr && "Error in Detcting Checkmate, could not find defending_king_ptr: defending_king_ptr is a nullptr!");

    bool multicheck = (attacking_pieces_that_give_check.size() > 1);

    // Try to move the king to its 8-Neighbourhood
    for (int row = -1; row <= 1; ++row) {
        for (int col = -1; col <= 1; ++col) {
            if (row != 0 || col != 0) {
                int new_row = king_row + row;
                int new_col = king_col + col;
                if (new_row >= 0 && new_row < 8 && new_col >= 0 && new_col < 8) { 
                        if (defending_king_ptr->is_move_possible(board_state, new_row, new_col,true, false)) {
                            if(is_opponents_king_move_legal(defending_king_ptr, board_state, new_row, new_col)) {
                                return false; // King can run to safe square
                                }
                        }
                    }
            }
        }
    }

    if (multicheck) {
        return true; // checkmate, you cannot capture and block two attackes at the same time
    }

    // Try to capture attacker
    std::shared_ptr<Chess_Piece> piece_that_gives_check = attacking_pieces_that_give_check[0];

    for (const auto& piece : *defending_pieces) {
        if (piece->getPieceType() != 'K' && piece->is_move_possible(board_state, piece_that_gives_check->get_row(), piece_that_gives_check->get_col(), true, false)) {
            if(is_opponents_move_legal(piece, board_state, piece_that_gives_check->get_row(), piece_that_gives_check->get_col())) {
                return false; // A defending piece can capture the king attacking piece
                }
        }
    }
    // Try to Body-Block Check
    if (piece_that_gives_check->getPieceType() == 'N' || piece_that_gives_check->getPieceType() == 'P') {
        return true; // Checkmate, you cannot block checks by Knight or Pawn
    }

    int row_diff = std::abs(std::get<0>(defending_king_pos) - piece_that_gives_check->get_row());
    int col_diff = std::abs(std::get<1>(defending_king_pos) - piece_that_gives_check->get_col());


    if (row_diff <= 1 && col_diff <= 1) {
        return true; // Checkmate, you cannot block an attacker that close to the king
    }

    std::vector<std::tuple<int, int>> possible_squares_for_blockers;

    if (row_diff == col_diff) {
        possible_squares_for_blockers= compute_block_squares_diag(defending_king_pos, piece_that_gives_check->get_row(), piece_that_gives_check->get_col());
    } else if (col_diff == 0) {
        possible_squares_for_blockers = compute_block_squares_vertical(defending_king_pos, piece_that_gives_check->get_row(), piece_that_gives_check->get_col());
    } else if (row_diff == 0) {
        possible_squares_for_blockers = compute_block_squares_horizontal(defending_king_pos, piece_that_gives_check->get_row(), piece_that_gives_check->get_col());
    }

    for (const auto& square : possible_squares_for_blockers) {
        int row, col;
        std::tie(row, col) = square;
    }

    for (const auto& square : possible_squares_for_blockers) {
        for (const auto& piece : *defending_pieces) {
            if (piece->getPieceType() != 'K' && piece->is_move_possible(board_state, std::get<0>(square), std::get<1>(square),false, true)) {
                if(is_opponents_move_legal(piece, board_state,std::get<0>(square), std::get<1>(square))){
                    return false;
                }
            }
        }

    }

    return true; // Schachmatt
}


bool Game::is_stalemate() {
    if(num_moves_played < 20) {
        return false;
    }

    auto defensive_pieces = (active_player > 0)  ? std::make_shared<std::vector<std::shared_ptr<Chess_Piece>>>(black_pieces) : std::make_shared<std::vector<std::shared_ptr<Chess_Piece>>>(white_pieces);

    for (std::shared_ptr<Chess_Piece> piece : *defensive_pieces) {
        if (piece->getPieceType() =='Q') {
            for(int row = -1; row <= 1; row++) {
                for(int col = -1; col <= 1; col++) {
                    int new_queen_row = piece->get_row() + row;
                    int new_queen_col = piece->get_col() + col;
                    if(new_queen_row >= 0 && new_queen_row <8 && new_queen_col >= 0 && new_queen_row < 8) {
                        if(board_state[new_queen_row][new_queen_col] == 0) {
                            return false;
                        }
                    }
                }
            }
        }
    }

    int piece_owner = (active_player > 0) ? -1 : 1;
    std::shared_ptr<Chess_Piece> defending_king_ptr;
    for (const auto& piece : *defensive_pieces) {
        if (piece->getPieceType() == 'K'){
            defending_king_ptr = piece;
        }
    }

    for (const auto& piece : *defensive_pieces) {
        if (has_piece_available_move(piece, piece_owner)){
            return false;
        }
        return true;
    }
    return false;
}


void Game::promote_pawn(std::shared_ptr<Chess_Piece>piece_ptr, char promotion_type) {
    piece_ptr->setPieceType(promotion_type);

    int new_piece_value;
    switch (promotion_type) {
        case 'P': new_piece_value = 1; break; // Pawn
        case 'N': new_piece_value = 3; break; // Knight
        case 'B': new_piece_value = 4; break; // Bishop
        case 'R': new_piece_value = 5; break; // Rook
        case 'Q': new_piece_value = 9; break; // Queen
        case 'K': new_piece_value = 10; break; // King
        default: throw std::invalid_argument("Invalid Promotion Type");
    }
    int color = (active_player > 0) ? 1 : -1;

    board_state[piece_ptr->get_row()][piece_ptr->get_col()] = new_piece_value * color;
}


std::vector<std::tuple<int, int>> Game::compute_block_squares_diag(
    const std::tuple<int, int>& defending_king_pos,
    int attacking_piece_row,
    int attacking_piece_col
) const{
    std::vector<std::tuple<int, int>> blockable_squares_diag;

    int king_row = std::get<0>(defending_king_pos);
    int king_col = std::get<1>(defending_king_pos);

    int diff_row =  king_row - attacking_piece_row;
    int diff_col =  king_col - attacking_piece_col;

    assert(abs(diff_row) == abs(diff_col) && "Error in compute diagonal block squares");

    int row_direction = (diff_row > 0) ? -1 : 1;
    int col_direction = (diff_col > 0) ? -1 : 1;

    int block_row = king_row + row_direction;
    int block_col = king_col + col_direction;

    while (block_row != attacking_piece_row && block_col != attacking_piece_col) {
        blockable_squares_diag.push_back({block_row, block_col});
        block_row += row_direction;
        block_col += col_direction;
    }
    return blockable_squares_diag;
}


std::vector<std::tuple<int, int>> Game::compute_block_squares_horizontal(
    const std::tuple<int, int>& defending_king_pos,
    int attacking_piece_row,
    int attacking_piece_col
) const{
    std::vector<std::tuple<int, int>> blockable_squares_horizontal;

    int king_row = std::get<0>(defending_king_pos);
    int king_col = std::get<1>(defending_king_pos);

    int diff_col =  king_col - attacking_piece_col;
    int col_direction = (diff_col > 0) ? -1 : 1;

    int block_row = king_row;
    int block_col = king_col + col_direction;

    while (block_col != attacking_piece_col) {
        blockable_squares_horizontal.push_back({block_row, block_col});
        block_col += col_direction;
    }
    return blockable_squares_horizontal;
}
std::vector<std::tuple<int, int>> Game::compute_block_squares_vertical(
    const std::tuple<int, int>& defending_king_pos,
    int attacking_piece_row,
    int attacking_piece_col
) const{
    std::vector<std::tuple<int, int>> blockable_squares_vertical;

    int king_row = std::get<0>(defending_king_pos);
    int king_col = std::get<1>(defending_king_pos);

    int diff_row = king_row - attacking_piece_row;
    int row_direction = (diff_row > 0) ? -1 : 1;

    int block_row = king_row + row_direction;
    int block_col = king_col;

    while (block_row != attacking_piece_row) {
        blockable_squares_vertical.push_back({block_row, block_col});
        block_row += row_direction;  
    }
    return blockable_squares_vertical;
}


std::shared_ptr<Chess_Piece> Game::create_piece(int val, int row_coord, int col_coord) {
    std::shared_ptr<Chess_Piece> piece;

    std::string color = (val > 0) ? "white" : "black";

    switch (std::abs(val)) {
        case 1:
            piece = std::make_shared<Chess_Piece>(row_coord, col_coord, color,'P');
        break;
        case 3:
            piece = std::make_shared<Chess_Piece>(row_coord, col_coord, color,'N');
        break;
        case 4:
            piece = std::make_shared<Chess_Piece>(row_coord, col_coord, color, 'B');
        break;
        case 5:
            piece = std::make_shared<Chess_Piece>(row_coord, col_coord, color, 'R');
        break;
        case 9:
            piece = std::make_shared<Chess_Piece>(row_coord, col_coord, color, 'Q');
        break;

        case 10: // King
            piece = std::make_shared<Chess_Piece>(row_coord, col_coord, color, 'K');
        break;
        case 0:
            break;
        default:
            throw std::invalid_argument("Unbekannter Wert für Schachfigur");
    }

    return piece;
}


std::vector<std::shared_ptr<Move>> Game::get_available_moves(std::shared_ptr<Chess_Piece> piece, int piece_owner) {

    std::vector<std::shared_ptr<Move>> available_moves;
    std::vector<std::tuple<int, int, bool>> move_candidates = piece->get_available_coords_to_move_to(piece_owner, board_state);
    for (const auto& move_candidate : move_candidates) {
        
        int row = std::get<0>(move_candidate);
        int col = std::get<1>(move_candidate);
        bool capture = std::get<2>(move_candidate);
        auto move = std::make_shared<Move>(Move(true, piece->get_row(), piece->get_col(), row, col, "", capture, false, piece->getPieceType()));
        if (piece->getPieceType() != 'K' && !is_own_king_in_check_after_move(piece, move, board_state)) {
            available_moves.push_back(move);
        } 
        else if(piece->getPieceType() == 'K' && !is_own_king_in_check_after_move(piece, move, board_state)) {
            available_moves.push_back(move);
        }

    }

    if(piece->getPieceType() == 'K') {
        if (check_castle('s')) {
            auto move = std::make_shared<Move>(Move(true, piece->get_row(), piece->get_col(), -1, -1, "short", false, false,'x'));
            available_moves.push_back(move);
        }
        if (check_castle('l')) {
            auto move = std::make_shared<Move>(Move(true, piece->get_row(), piece->get_col(), -1, -1, "long", false, false,'x'));
            available_moves.push_back(move);
        }
    }

    return available_moves;
}


bool Game::has_piece_available_move(std::shared_ptr<Chess_Piece> piece, int piece_owner) {
    std::vector<std::tuple<int, int, bool>> coord_candidates = piece->get_available_coords_to_move_to(piece_owner, board_state);
    for (const auto& coord : coord_candidates) {
        int row = std::get<0>(coord);
        int col = std::get<1>(coord);
        auto move = std::make_shared<Move>(Move(true, piece->get_row(), piece->get_col(), row, col, "", (board_state[row][col] != 0), true, piece->getPieceType()));
        if (piece->getPieceType() != 'K' && is_opponents_move_legal(piece, board_state, row,col)) {
            return true;
        }
        if(piece->getPieceType() == 'K' && is_opponents_king_move_legal(piece, board_state, row, col)) {
            return true;
        }
    }
return false;
}

std::list<std::vector<std::shared_ptr<Move>>> Game::get_all_available_moves() {
    auto active_pieces = (active_player > 0) ? white_pieces : black_pieces;

    std::list<std::vector<std::shared_ptr<Move>>> available_moves;

    for (auto piece : active_pieces) {
        available_moves.push_back(get_available_moves(piece, active_player));
    }
    return available_moves;
}

// Game state management

std::string Game::save_game_state() const {
    std::ostringstream oss;
    oss << active_player << "," << num_moves_played << "," << game_state << ";";
    oss << std::get<0>(white_king_pos) << "," << std::get<1>(white_king_pos) << ";";
    oss << std::get<0>(black_king_pos) << "," << std::get<1>(black_king_pos) << ";";

    for (int i = 0; i < 8; i++) {
        for (int j = 0; j < 8; j++) {
            oss << board_state[i][j] << ",";
        }
    }
    oss << ";";
    oss << is_active_player_in_check << "," << is_passive_player_in_check << ",";
    oss << has_black_king_moved << "," << has_white_king_moved << ",";
    oss << has_white_a_rook_moved << "," << has_white_h_rook_moved << ",";
    oss << has_black_a_rook_moved << "," << has_black_h_rook_moved << ";";
    oss << std::get<0>(*en_passant_coords) << "," << std::get<1>(*en_passant_coords) << "," << en_passant_option;

    return oss.str();
}

void Game::restore_game_state(const std::string& state_str) {
    std::istringstream iss(state_str);
    std::string part;

    std::getline(iss, part, ';');
    std::istringstream s1(part);
    s1 >> active_player;
    s1.ignore();
    s1 >> num_moves_played;
    s1.ignore();
    std::getline(s1, game_state, ';');

    std::getline(iss, part, ';');
    std::istringstream s2(part);
    int x, y;
    s2 >> x;
    s2.ignore();
    s2 >> y;
    white_king_pos = {x, y};

    std::getline(iss, part, ';');
    std::istringstream s3(part);
    s3 >> x;
    s3.ignore();
    s3 >> y;
    black_king_pos = {x, y};

    std::getline(iss, part, ';');
    std::istringstream s4(part);
    for (int i = 0; i < 8; i++) {
        for (int j = 0; j < 8; j++) {
            s4 >> board_state[i][j];
            s4.ignore();
        }
    }

    std::getline(iss, part, ';');
    std::istringstream s5(part);
    s5 >> is_active_player_in_check;
    s5.ignore();
    s5 >> is_passive_player_in_check;
    s5.ignore();
    s5 >> has_black_king_moved;
    s5.ignore();
    s5 >> has_white_king_moved;
    s5.ignore();
    s5 >> has_white_a_rook_moved;
    s5.ignore();
    s5 >> has_white_h_rook_moved;
    s5.ignore();
    s5 >> has_black_a_rook_moved;
    s5.ignore();
    s5 >> has_black_h_rook_moved;

    std::getline(iss, part, ';');
    std::istringstream s6(part);
    s6 >> x;
    s6.ignore();
    s6 >> y;
    s6.ignore();
    s6 >> en_passant_option;
    en_passant_coords = std::make_shared<std::tuple<int, int>>(x, y);
}




// just some interfaces 



std::vector<std::tuple<char, std::string, int, int>> Game::get_all_positions() {
    std::vector<std::tuple<char, std::string, int, int>> positions;
    for (const auto& piece : white_pieces) {
        positions.emplace_back(piece->getPieceType(), piece->getColor(), piece->get_row(), piece->get_col());
    }
    for (const auto& piece : black_pieces) {
        positions.emplace_back(piece->getPieceType(), piece->getColor(), piece->get_row(), piece->get_col());
    }
    return positions;
}

std::vector<std::tuple<char, std::tuple<int, int>, std::vector<std::tuple<int, int>>>> Game::get_player_moves(int player) {
    std::vector<std::tuple<char, std::tuple<int, int>, std::vector<std::tuple<int, int>>>> moves;

    auto pieces = (player > 0) ? white_pieces : black_pieces;
    bool short_castle = false;
    bool long_castle = false;
    for (const auto& piece : pieces) {
        std::vector<std::tuple<int, int>> piece_moves;
        for (const auto& move : get_available_moves(piece, player)) {
            if (move->getIsCastlingMove() == "")
            {
                piece_moves.emplace_back(move->row_target, move->col_target);
            }
            else{
                if (move->getIsCastlingMove() == "short")
                {
                    short_castle = true;
                }
                if (move->getIsCastlingMove() == "long")
                {
                    long_castle = true;
                }
            }
        }
        moves.emplace_back(piece->getPieceType(),
                           std::make_tuple(piece->get_row(), piece->get_col()),
                           piece_moves);
    }
    if (long_castle)
    {   
        std::tuple<int,int> king_position = (player > 0) ? std::make_tuple(0,4) : std::make_tuple(7,4);
        std::tuple<int,int> castle_coords = (player > 0) ? std::make_tuple(0,2) : std::make_tuple(7,2);
        std::vector<std::tuple<int, int>> target = { castle_coords };
        moves.emplace_back('K',
                           king_position,
                           target);
    }
        if (short_castle)
    {   
        std::tuple<int,int> king_position = (player > 0) ? std::make_tuple(0,4) : std::make_tuple(7,4);
        std::tuple<int,int> castle_coords = (player > 0) ? std::make_tuple(0,6) : std::make_tuple(7,6);
        std::vector<std::tuple<int, int>> target = { castle_coords };
        moves.emplace_back('K',
                           king_position,
                            target);
    }
    return moves;
}

std::vector<std::vector<int>> Game::get_board_state() {
    std::vector<std::vector<int>> state(8, std::vector<int>(8));
    for (int i = 0; i < 8; ++i) {
        for (int j = 0; j < 8; ++j) {
            state[i][j] = board_state[i][j];
        }
    }
    return state;
}
std::string Game::generate_move_notation(int start_row, int start_col, int target_row, int target_col) {
    if (start_row < 0 || start_row >= 8 || start_col < 0 || start_col >= 8 ||
        target_row < 0 || target_row >= 8 || target_col < 0 || target_col >= 8) {
        return "Invalid move";
    }

    int piece_value = board_state[start_row][start_col];
    if (piece_value == 0) {
        return "Invalid move";
    }

    char piece_type;
    if (piece_encoding.find(std::abs(piece_value)) != piece_encoding.end()) {
        piece_type = piece_encoding[std::abs(piece_value)];
    } else {
        return "Invalid move";
    }

    // Check for castling
    if (piece_type == 'K' && start_col == 4) {
        if ((start_row == 0 || start_row == 7) && target_row == start_row) {
            if (target_col == 2) {
                return "O-O-O"; // Long castle
            } else if (target_col == 6) {
                return "O-O"; // Short castle
            }
        }
    }

    // Determine if the move is a capture
    bool is_capture = (board_state[target_row][target_col] != 0 &&
                       (board_state[target_row][target_col] * piece_value < 0));

    // Create a move object to generate algebraic notation
    Move move;
    move.setIsLegalMove(true);
    move.setPieceToMove(piece_type);
    move.set_row_CoordStart(start_row);
    move.set_col_CoordStart(start_col);
    move.set_row_CoordTarget(target_row);
    move.set_col_CoordTarget(target_col);
    move.setIsCapturingMove(is_capture);

    return move.get_algebraic_chess_notation();
}



std::vector<std::pair<int, std::pair<std::string, std::string>>> Game::get_history_vector() const {
    std::vector<std::pair<int, std::pair<std::string, std::string>>> history_vector;
    int move_number = 1;

    for (size_t i = 0; i < game_history_str.size(); i += 2) {
        std::string first_move = game_history_str[i];
        std::string second_move = (i + 1 < game_history_str.size()) ? game_history_str[i + 1] : "";
        history_vector.emplace_back(move_number++, std::make_pair(first_move, second_move));
    }

    return history_vector;
}





std::unordered_map<int, std::string> Game::valueToPiece = {
    {EE, ".."},
    {BK, "BK"},
    {BQ, "BQ"},
    {BB, "BB"},
    {BN, "BN"},
    {BR, "BR"},
    {BP, "BP"},
    {WK, "WK"},
    {WQ, "WQ"},
    {WB, "WB"},
    {WN, "WN"},
    {WR, "WR"},
    {WP, "WP"}
};

std::unordered_map<std::string, int> Game::pieceToValue = {
    {"EMPTY", EE},
    {"BK", BK},
    {"BQ", BQ},
    {"BB", BB},
    {"BN", BN},
    {"BR", BR},
    {"BP", BP},
    {"WK", WK},
    {"WQ", WQ},
    {"WB", WB},
    {"WN", WN},
    {"WR", WR},
    {"WP", WP}
};

std::unordered_map<int, char> Game::piece_encoding = {
    {1, 'P'},
    {3, 'N'},
    {4, 'B'},
    {5, 'R'},
    {9, 'Q'},
    {10, 'K'}
};





// Debug


void Game::print_board_state() const {
    const int cell_width = 3;

    for (int row = 7; row >= 0; --row) {
        std::cout << row +1<< " "; // Zeilennummer
        for (int col = 0; col < 8; ++col) {
            int piece = board_state[row][col];
            // Verwendung der valueToPiece Map für die Ausgabe
            auto it = valueToPiece.find(piece);
            if (it != valueToPiece.end()) {
                std::cout << std::setw(cell_width) << it->second << " ";
            } else {
                std::cout << std::setw(cell_width) << "??" << " "; // Fehlerfall, wenn der Wert nicht gefunden wird
            }
        }
        std::cout << "\n";
    }

    // Ausgabe der Spaltenbezeichner
    std::cout << "  ";
    for (char col = 'a'; col <= 'h'; ++col) {
        std::cout << std::setw(cell_width) << col << " ";
    }
    std::cout << "\n";
}

void Game::print_pieces_debug() {
    std::cout << "White Pieces:\n";
    for (const auto& piece : white_pieces) {
        std::cout << "Type: " << piece->getPieceType() << ", Color: " << piece->getColor()
                  << ", Position: (" << piece->get_row() << ", " << piece->get_col()<< ")\n";
    }

    // Debug-Ausgabe für schwarze Figuren
    std::cout << "Black Pieces:\n";
    for (const auto& piece : black_pieces) {
        std::cout << "Type: " << piece->getPieceType() << ", Color: " << piece->getColor()
                  << ", Position: (" << piece->get_row() << ", " << piece->get_col()<< ")\n";
    }

    std::cout << "Active Pieces:\n";
    for (const auto& piece : *active_pieces) {
        std::cout << "Type: " << piece->getPieceType() << ", Color: " << piece->getColor()
                  << ", Position: (" << piece->get_row() << ", " << piece->get_col()<< ")\n";
    }

    // Debug-Ausgabe für schwarze Figuren
    std::cout << "Passive Pieces:\n";
    for (const auto& piece : *passive_pieces) {
        std::cout << "Type: " << piece->getPieceType() << ", Color: " << piece->getColor()
                  << ", Position: (" << piece->get_row() << ", " << piece->get_col()<< ")\n";
    }
    std::cout << "\n";
}

void Game::print_history() {
    int move_number = 1;
    std::cout << "Game History: \n";
    for (size_t i = 0; i < game_history_str.size(); i += 2) {
        // Ausgabe der Zugnummer und des ersten Zugs
        std::cout << move_number << ". " << game_history_str[i];

        // Prüfen, ob es einen zweiten Zug für diesen Zug gibt
        if (i + 1 < game_history_str.size()) {
            std::cout << " " << game_history_str[i + 1];
        }

        // Zeilenumbruch nach jedem Zugpaar
        std::cout << std::endl;

        move_number++;
    }
}