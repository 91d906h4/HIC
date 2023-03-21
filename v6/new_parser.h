#include <stdexcept>
#include <iostream>
#include <vector>
#include <string>
#include <stack>
#include <map>

#include "operators.h"
#include "random.h"

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
    void getInput (std::vector<std::vector<std::string>> i) { tokens = i; tokensLength = i.size(); }
    std::stack<std::string> parse () {
        statement();
        while (!generatorStack.empty()) {
            std::cout << generatorStack.top() << std::endl;
            generatorStack.pop();
        }
        return generatorStack;
    }

private:
    std::vector<std::vector<std::string>> tokens;
    std::stack<std::string> generatorStack;
    TokenType token;

    int tokensLength, pointer = -1;

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
            throw std::runtime_error("Character '" + match + "' <-> '" + token.current.name + "' did not match.\nDid you miss " + match + "?");

        return token;
    }

    void statement () {
        token = getToken();
        std::string tcn = token.current.name, tcc = token.current.chr, tnn = token.next.name;
        pointer--;
        expression();
        token = getToken();
        std::cout << token.current.chr << std::endl;
    }

    void listParse () {
        generatorStack.push("OPEN LIST");
        if (token.next.name == "CLOSE BRACK") getToken(); // If this is a empty list
        else {
            do {
                expression();
                generatorStack.push("COMMA");

                if (token.next.name == "CLOSE BRACK") break;
                token = getToken();

            } while (token.current.name == "COMMA");
        }
        generatorStack.push("CLOSE LIST");
    }

    void dictParse () {
        generatorStack.push("OPEN DICT");
        if (token.next.name == "CLOSE BRACE") getToken(); // If this is a empty dict
        else {
            do {
                expression();
                generatorStack.push("COLON");
                expression();
                generatorStack.push("COMMA");

                if (token.next.name == "CLOSE BRACE") break;
                token = getToken();

            } while (token.current.name == "COMMA");
        }
        generatorStack.push("CLOSE DICT");
    }

    void factor () {
        token = getToken();
        std::string tcn = token.current.name, tcc = token.current.chr, tnn = token.next.name, tnc = token.next.chr, functionName;
        int params;

        if (tcn == "SYMBOL" && tnn == "OPEN PAREN") {
            functionName = tcc, params = 0;
            getToken("OPEN PAREN");
            if (token.next.name != "CLOSE PAREN") { // Check if call with no params.
                do {
                    expression();
                    generatorStack.push("COMMA");
                    params++;

                    if (token.next.name == "CLOSE PAREN") break;
                    token = getToken();

                } while (token.current.name == "COMMA");
            }
            token = getToken("CLOSE PAREN");
            
            generatorStack.push("CALL " + functionName + " " + std::to_string(params));
        }
        else if (tcn == "SYMBOL" && tnn == "OPEN BRACK") {
            functionName = tcc, params = 0;
            getToken("OPEN BRACK");
            if (token.next.name != "CLOSE BRACK") { // Check if call with no params.
                do {
                    expression();
                    generatorStack.push("COMMA");
                    params++;

                    if (token.next.name == "CLOSE BRACK") break;
                    token = getToken();

                } while (token.current.name == "COMMA");
            }
            token = getToken("CLOSE BRACK");
            
            generatorStack.push("LDAA " + functionName + " " + std::to_string(params));
        }
        else generatorStack.push("LDA " + tcc);
    }

    void expression () {
        std::stack<std::string> operatorStack;
        std::string tcn, tcc, tnn, tnc;

        while (true) {
            token = getToken();
            tcn = token.current.name, tcc = token.current.chr, tnn = token.next.name, tnc = token.next.chr;

            if (tcn == "OPEN PAREN") expression();
            else if (tcn == "OPEN BRACK") listParse();
            else if (tcn == "OPEN BRACE") dictParse();
            else if (tcn == "INTEGER" || tcn == "FLOAT" || tcn == "STRING" || tcn == "TRUE" || tcn == "FALSE" || tcn == "NULL" || tcn == "SYMBOL") { pointer--; factor(); }
            else if (isOperator(tcc)) {
                if (operatorStack.empty()) operatorStack.push(tcc);
                else if (operatorWeight(operatorStack.top()) <= operatorWeight(tcc)) {
                    while (!operatorStack.empty() && operatorWeight(operatorStack.top()) <= operatorWeight(tcc)) {
                        generatorStack.push(operatorToName.at(operatorStack.top()) + " _ _");
                        operatorStack.pop();
                    }
                    operatorStack.push(tcc);
                }
                else operatorStack.push(tcc);
            }

            if (tnn == "CLOSE PAREN" || tnn == "CLOSE BRACK" || tnn == "CLOSE BRACE" || tnn == "ASSIGN" || tnn == "SEMICOLON" || tnn == "COLON" || tnn == "COMMA" || tnn == "EOF") {
                while (!operatorStack.empty()) {
                    if (operatorStack.top() != ";") generatorStack.push(operatorToName.at(operatorStack.top()) + " _ _");
                    operatorStack.pop();
                }
                break;
            }
        }
    }
};