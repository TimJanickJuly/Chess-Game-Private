#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/complex.h>
#include <pybind11/functional.h>
#include <pybind11/chrono.h>
#include <pybind11/iostream.h>
#include <pybind11/stl_bind.h>
#include <memory>
#include "../src/game.h"

namespace py = pybind11;

PYBIND11_MODULE(chess_engine, m) {
    py::class_<Game, std::shared_ptr<Game>>(m, "Game")
        .def(py::init<>())
        .def_readwrite("active_player", &Game::active_player)
        .def_readwrite("game_history_str", &Game::game_history_str)
        .def_readwrite("game_state", &Game::game_state)
        .def_readwrite("num_moves_played", &Game::num_moves_played)
        .def("handle_turn", &Game::handle_turn)
        .def("switchPlayer", &Game::switchPlayer)
        .def("is_stalemate", &Game::is_stalemate)
        .def("is_checkmate", &Game::is_checkmate)
        .def("print_history", &Game::print_history)
        .def("print_board_state", &Game::print_board_state);
}
