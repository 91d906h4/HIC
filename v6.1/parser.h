#include <stdexcept>
#include <iostream>
#include <vector>
#include <string>
#include <stack>
#include <map>

/*
    Struct TokenType:
        1. token.current.name
        2. token.current.chr (character)
        3. token.next.name (the name of next token)
        4. token.next.chr
*/
struct XToken {
    std::string name;
    std::string chr;
};

struct TokenType {
    XToken current;
    XToken next;
};

class Parser {
public:
    void input (std::vector<std::vector<std::string>> inputToken) { tokens = inputToken; tokensLength = tokens.size(); }
    void parse () {
        statement();
    }

private:
    std::vector<std::vector<std::string>> tokens;
    std::stack<std::string> generatorStack;
    TokenType token;

    int tokensLength = 0, pointer = -1;

    /*
        Function getToken():
            Return a vector including current token and the next token.
            If there is no next token, then return "EOF".
    */
    TokenType getToken (std::string match = "") {
        // Check if length is out of range.
        if (pointer + 2 >= tokensLength) {
            token.current = {tokens[pointer + 1][0], tokens[pointer + 1][1]};
            token.next = {"EOF", "EOF"};
            return token;
        }

        pointer++; // Update pointer.

        // Ignore all comments.
        int n = 1;
        while (tokens[pointer][0] == "COMMENT") pointer++;
        while (tokens[pointer + n][0] == "COMMENT") n++;

        token.current = {tokens[pointer][0], tokens[pointer][1]};
        token.next = {tokens[pointer + n][0], tokens[pointer + n][1]};

        if (match != "" && match != token.current.name) // Check if given character match.
            throw std::runtime_error("Character '" + match + "' <-> '" + token.current.name + "' did not match.\nDid you miss '" + match + "'?");

        return token;
    }

    void statement () {}

    void expression () {}
};
