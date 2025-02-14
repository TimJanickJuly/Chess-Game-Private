#include <iostream>
#include <memory>
#include <vector>
#include "src/game.h"
#include "test.h"
#include <iomanip>
#include <set>

int main(int argc, char* argv[]) {
    if (argc == 1) {
        auto board = std::make_shared<Game>();
        std::string user_input;
        int valid_move;
        while (true) {
            std::cout << "\n\n";
            board->print_history();
            std::cout << "\n";
            std::cout << "Commands: a legal chess move, 'show' to see the board, 'moves' to get a list of all legal moves\n\n";
            if (board->active_player == 1) {
                std::cout << "White's Turn: \n";
            } else {
                std::cout << "Blacks's Turn: \n";
            }
            if (board->is_passive_player_in_check) {
                std::cout << "Your King is in check!\n";
            }
            std::getline(std::cin, user_input);
            if(user_input == "show") {
                board->print_board_state();
            }
            else if(user_input == "moves") {
                auto list_of_available_moves = board->get_all_available_moves();
                for (const auto& vector : list_of_available_moves) {
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
                            (*it)->is_difficult = false;
                            std::cout << (*it)->get_algebraic_chess_notation();
                            if (std::next(it) != vector.end()) {
                                std::cout << ", ";
                            }
                        }
                        std::cout << "}\n";
                    }
                }
            }
            else {
                valid_move = board->handle_turn(user_input);
                if (valid_move == 2) {
                    std::cout << "\n";
                }
                if (valid_move == 1) {
                    std::cout << "Invalid Synatx\n";
                }
                if (valid_move == -1) {
                    std::cout << "Illegal move\n";
                }
                if (valid_move == 0) {
                    std::cout << "Check and Mate\n";
                    std::cout << "\n\n";
                    board->print_history();
                    std::cout << "\n";
                    board->print_board_state();
                    break;
                }
            }
        }
        std::cout << "\nPress Enter to end\n";
        std::string end_buffer;
        std::getline(std::cin, end_buffer);
        return 0;
    }
    else if (argc == 3 && std::string(argv[1]) == "--test") {
        std::string which_test = argv[2];
        std::vector<std::tuple<std::string, bool>> test_results;
        Test testInstance;
        std::vector<Test_Data> test_data_vector = testInstance.getTestDataVector();
        std::set<int> tests_to_execute;
        if (which_test != "ALL") {
            int number = std::stoi(which_test);
            tests_to_execute.insert(number);
        }
        int valid_move;
        int test_count = 0;
        for (const Test_Data& test_data : test_data_vector) {
            test_count += 1;
            if (which_test == "ALL" || tests_to_execute.find(test_count) != tests_to_execute.end()){
                std::cout << "\n\nTest Nr. " << test_count << "\n";
                auto board = std::make_shared<Game>();
                bool moves_ok = true;
                for (size_t i = 0; i < test_data.test_game.size(); i++) {
                    std::string move_input = test_data.test_game[i];
                    std::cout << "\n\n";
                    board->print_history();
                    std::cout << "\n";
                    if (board->active_player == 1) {
                        std::cout << "White's Turn, Move: " << move_input << "\n";
                    } else {
                        std::cout << "Black's Turn, Move: " << move_input << "\n";
                    }
                    if (board->is_passive_player_in_check) {
                        std::cout << "Your King is in check!\n";
                    }
                    valid_move = board->handle_turn(move_input);
                    board->print_board_state();
                    if (i != test_data.test_game.size() - 1 && valid_move != 2) {
                        std::cout << "Error: Move " << (i + 1) << " returned " << valid_move << ", expected 2." << std::endl;
                        moves_ok = false;
                        break;
                    }
                    if (valid_move == 2) {
                        std::cout << "\n";
                    } else if (valid_move == 1) {
                        std::cout << "Invalid Syntax\n";
                        moves_ok = false;
                        break;
                    } else if (valid_move == -1) {
                        std::cout << "Illegal move\n";
                        moves_ok = false;
                        break;
                    }
                    if (valid_move == 0) {
                        std::cout << board->last_move_status << "\n";
                        break;
                    }
                    std::cout << "\n";
                    board->print_board_state();
                }
                std::cout << "\n";
                std::cout << "\nRemaining moves for active player:" << std::endl;
                auto active_moves = board->get_player_moves(board->active_player);
                for (const auto &move_tuple : active_moves) {
                    char piece;
                    std::tuple<int, int> pos;
                    std::vector<std::tuple<int, int>> targets;
                    std::tie(piece, pos, targets) = move_tuple;
                    std::cout << piece << " at (" 
                              << std::get<0>(pos) << ", " << std::get<1>(pos) << "): { ";
                    for (const auto &target : targets) {
                        std::cout << "(" 
                                  << std::get<0>(target) << ", " << std::get<1>(target) << ") ";
                    }
                    std::cout << "}" << std::endl;
                }
                std::cout << board->game_state << "\n";
                if ((board->game_state == test_data.test_solution) && ((valid_move == 2 || valid_move == 0) && moves_ok)) {
                    test_results.push_back(std::make_tuple(test_data.test_name, true));
                }
                else {
                    test_results.push_back(std::make_tuple(test_data.test_name, false));
                }
            }
        }
        std::cout << "\n\nEvaluation of all Tests\n\n";
        int result_count = 0;
        const int width_name = 25;
        const int width_result = 8;
        for (auto test_result : test_results) {
            result_count += 1;
            std::string str_result = (std::get<1>(test_result)) ? "passed" : "failed";
            std::cout << " Test Nr. " << std::setw(2) << result_count
                      << " : " << std::setw(width_name) << std::left << std::get<0>(test_result)
                      << " " << std::setw(width_result) << std::right << str_result
                      << "\n";
        }
        std::string end_buffer;
        std::getline(std::cin, end_buffer);
        return 0;
    }
}
