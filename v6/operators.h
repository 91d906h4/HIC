#include <map>
#include <string>

const std::map<std::string, int> operatorWeightList = {
    {"@", 1},
    {"@@", 1},
    {"**", 2},
    {"++", 2},
    {"--", 2},
    {">>", 3},
    {"<<", 3},
    {"*", 4},
    {"/", 4},
    {"%", 4},
    {"&", 5},
    {"|", 5},
    {"^", 5},
    {"+", 6},
    {"-", 6},
    {"==", 7},
    {"!=", 7},
    {">=", 7},
    {"<=", 7},
    {">", 7},
    {"<", 7},
    {"not", 8},
    {"and", 9},
    {"or", 10},
    {",", 99},
    {";", 100}
};

const std::map<std::string, std::string> operatorToName= {
    {"@", "GTA"}, // Get address
    {"@@", "GTV"}, // Get value (by address)
    {"**", "EXP"},
    {">>", "BRS"},
    {"<<", "BLS"},
    {"*", "MUL"},
    {"/", "DIV"},
    {"%", "REM"},
    {"&", "BAND"},
    {"|", "BOR"},
    {"^", "BXOR"},
    {"+", "ADD"},
    {"-", "SUB"},
    {"==", "EQU"},
    {"!=", "NEQ"},
    {">=", "EOGT"}, // Equal or greater than
    {"<=", "EOLT"}, // Equal or less than
    {">", "GRT"}, // Greater than
    {"<", "LST"}, // Less than
    {"not", "NOT"},
    {"and", "AND"},
    {"or", "OR"},
};

bool isOperator (std::string token) {
    return operatorWeightList.count(token) != 0;
}

int operatorWeight (std::string op) {
    if (isOperator(op)) return operatorWeightList.at(op);
    else return -1;
}