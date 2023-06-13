#include <iostream>
#include <stack>

#include "parser.h"
#include "lexer.h"

int main () {
    std::vector<std::vector<std::string>> tokens;
    std::stack<std::string> generateStack;

    Lexer lexer = Lexer();
    Parser parser = Parser();

    tokens = lexer.lex("test.hy");
    parser.input(tokens);
    parser.parse();

    // for (std::vector<std::string> t: tokens) std::cout << t[0] << "    \t|\t" << t[1] << std::endl;

    return 0;
}