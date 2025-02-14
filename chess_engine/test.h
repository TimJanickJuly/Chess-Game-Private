#ifndef TEST_H
#define TEST_H

#include <iostream>
#include <vector>
#include "src/game.h"

// Definition der struct Test_Data
struct Test_Data {
    std::vector<std::string> test_game;
    std::string test_solution;
    std::string test_name;

    Test_Data(const std::string& name, const std::vector<std::string>& game, const std::string& solution)
        : test_game(game), test_solution(solution), test_name(name) {}
};

// Definition der Klasse test
class Test {
private:
    std::vector<Test_Data> test_data_vector;
public:
    // Konstruktor
    Test();

    // Getter-Methode für den test_data_vector
    const std::vector<Test_Data>& getTestDataVector() const;

    // Alternativ könnte auch ein Setter hinzugefügt werden, falls nötig
};

#endif // TEST_H
