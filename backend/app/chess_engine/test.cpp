#include "test.h"

const std::vector<Test_Data>& Test::getTestDataVector() const {
    return test_data_vector;
}

Test::Test() {

    test_data_vector.emplace_back(
        "fools_mate_white",
        std::vector<std::string>{"e4", "e5", "Qf3", "c6", "Bc4", "a6", "Qxf7#"},
        "white wins"
    );

    test_data_vector.emplace_back(
        "fools_mate_black",
        std::vector<std::string>{"a3", "e5", "a4", "Qf6", "a5", "Bc5", "a6", "Qxf2#"},
        "black wins"
    );

    test_data_vector.emplace_back(
        "unblockable check",
        std::vector<std::string>{"e4", "f5", "a3", "g5", "Qh5#"},
        "white wins"
    );

    test_data_vector.emplace_back(
        "blockable check",
        std::vector<std::string>{"e4", "f6", "Nc3", "Nc6", "d3", "g5", "Be3", "Ne5", "Qh5+", "Nf7", "O-O-O"},
        "running"
    );

    test_data_vector.emplace_back(
        "castling short",
        std::vector<std::string>{"e4", "e5", "Nf3", "Nf6", "Bc4", "Bc5", "o-o", "o-o", "a3"},
        "running"
    );

    test_data_vector.emplace_back(
        "stalemate",
        std::vector<std::string>{
            "e4", "e5", "f4", "Nf6", "fxe5", "d5", "exd5", "Nxd5", "Bc4", "Bh3", 
            "Bxd5", "Qxd5", "gxh3", "Qxh1", "Qf3", "Nc6", "Nc3", "Bc5", "Qxh1", "f6", 
            "exf6", "a5", "b4", "a4", "a3", "b5", "Qxc6+", "Kf7", "Qe6+", "Kxe6", 
            "Nf3", "gxf6", "Bb2", "Kf5", "h4", "c6", "h5", "Rhe8+", "Kf1", "Re1+", 
            "Kxe1", "Re8+", "Kf1", "Re1+", "Kxe1", "h6", "Ng1", "Bd4", "Kf1", "Be5", 
            "Kg2", "Bf4", "Rf1", "c5", "Kf3", "c4", "d4", "Bd6", "d5", "Bf4", "Nge2", 
            "Bd6", "Ng1", "Bf4", "Nh3", "Bd6", "Ke2+", "Bf4", "Kd1", "Kg4", "Ke2", 
            "Kf5", "Kf2", "Bd6", "Ne2", "Bc7", "Bc3", "Bd6", "Bd4", "Bf4", "Nc3", 
            "Bd6", "Kf3", "Bf4", "Kf2", "Bg5", "Kg3+", "Bf4+", "Kh4"
            },
        "stalemate"
    );

    test_data_vector.emplace_back(
        "king walk",
        std::vector<std::string>{"e4", "e5", "Ke2", "Ke7", "Kd3", "Kd6", "Kc4", "Kc6", "h3", "Kb6",
                                 "Kd5", "c5", "Kxe5", "c4", "Kf5", "Kb5", "Qh5", "Kb4", "a3+", "Ka4",
                                 "Kf4", "h6", "Nc3#"},
        "white wins"
    );

    test_data_vector.emplace_back(
        "capturable_check",
        std::vector<std::string>{"e4", "f6", "Bb5", "g5", "Nc3", "h5", "Qxh5+", "Rxh5"},
        "running"
    );

    test_data_vector.emplace_back(
        "stalemate hard",
        std::vector<std::string>{"e4", "e5", "f4", "exf4", "Nf3", "f5", "exf5", "Nc6", "Bb5", "Nf6", "Bxc6", "Bb4", "Bxb7", "Bxd2+", "Bxd2", "d5", "Bxa8", "a5", "a4", "c5", "o-o", "o-o", "Qe2", "Kh8", "Qe6", "g6", "Qxc8", "Ng4", "Qxd8", "Rg8", "h4", "Nf2", "Rxf2", "c4", "h5", "c3", "b3", "d4", "h6", "gxf5", "Nh4", "Rf8", "Ng6+", "Kg8", "Ne7+", "Kh8", "Qd7", "Rg8", "Be1", "d3", "Bd2", "cxd2", "c3", "f3", "g3", "f4", "g4", "Rf8", "Rg8", "Rg7", "Qd4"},
        "stalemate");


    test_data_vector.emplace_back(
        "Promotion Queen",
        std::vector<std::string>{"f4", "g6", "f5", "Bh6", "fxg6", "Bxd2+", "Qxd2", "Nf6", "g7", "Ne4", "gxh8=Q#"},
        "white wins");

    test_data_vector.emplace_back(
        "En Passant",
        std::vector<std::string>{"e4", "g5", "e5", "f5", "exf6 e.p.", "Nc6", "Qh5#"},
        "white wins");

    test_data_vector.emplace_back(
    "e.p. + queening black",
    std::vector<std::string>{ "a3", "h5", "f4", "h4", "g4", "hxg3 e.p.", "a4", "e6", "a5", "gxh2", "a6", "hxg1=Q", "axb7", "Qg3#"},
    "black wins");

    test_data_vector.emplace_back(
"draw by repetition",
std::vector<std::string>{ "Nf3", "Nf6", "Ng1", "Ng8", "Nf3", "Nf6", "Ng1", "Ng8", "Nf3", "Nf6", "Ng1", "Ng8"},
"draw");
}
