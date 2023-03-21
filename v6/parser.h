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

    int tokensLength;
    int pointer = 0;

    /*
        Function getToken():
            Return a vector including current token and the next token.
            If there is no next token, then return "EOF".
    */
    TokenType getToken (std::string match = "") {
        // Check if length is out of range.
        if (pointer + 1 >= tokensLength) {
            token.current = {tokens[pointer][0], tokens[pointer][1]};
            token.next = {"EOF", "EOF"};
            return token;
        }

        token.current = {tokens[pointer][0], tokens[pointer][1]};
        pointer++; // Update pointer to next index.
        token.next = {tokens[pointer][0], tokens[pointer][1]};

        if (match != "" && match != token.current.name) // Check if given character match.
            throw std::runtime_error("Character '" + match + "' <-> '" + token.current.name + "' did not match.\nDid you miss " + match + "?");

        return token;
    }

    void statement () {
        token = getToken();
        std::string tcn = token.current.name, tcc = token.current.chr, tnn = token.next.name;

        if (tcn == "IF") ifStatement();
        else if (tcn == "OPEN BRACE") { statement(); getToken("CLOSE BRACE"); statement(); }
        else if (tcn == "SEMICOLON") statement();
        else if (tcn == "FOR") forStatement();
        else if (tcn == "WHILE") whileStatement();
        else if (tcn == "FUNCTION") functionStatement();
        else if (tcn == "SYMBOL" && (tnn == "ASSIGN" || tnn.find("SELF ") == 0 || tnn == "ADD ONE" || tnn == "SUB ONE")) { pointer--; assignment();}
        else if (tcn == "DEC INT" || tcn == "DEC FLOAT" || tcn == "DEC STRING" || tcn == "DEC BOOL" || tcn == "DEC LIST" || tcn == "DEC DICT") { pointer--; delcaration(); }
        else if (tcn == "CLOSE BRACE") pointer--;
        else if (tcn == "COMMENT") pointer++;
        else if (tcn == "RETURN") { expression(); pointer++; generatorStack.push("RET"); }
        else { pointer--; expression(); getToken("SEMICOLON"); }
    }

    /*
        Function delcaration():
            If delcaration() is called by for-loop or function, then set
            backToStatement argument to false to prevent return to statement.
    */
    void delcaration (std::string defaulType = "", bool backToStatement = true) {
        std::string variableName, type;
        if (defaulType == ""){
            token = getToken();
            type = token.current.name.erase(0, 4);
        }
        else type = defaulType;
        token = getToken();
        variableName = token.current.chr;

        generatorStack.push(type + " " + variableName);

        if (token.next.name == "ASSIGN") {
            getToken("ASSIGN");
            expression();
            generatorStack.push("STA " + variableName + " _");
        }

        /*
            Check if a one-liner declaration.
            Examepl: int a, b = 1, c;
        */
        token = getToken();
        if (token.current.name == "COMMA") {
            if (token.next.name == "SYMBOL") delcaration(type);
            else delcaration();
        }
        else if (backToStatement) statement();
        else if (!backToStatement) pointer--;
    }

    void functionDeclaration () {
        std::string variableName, type;
        token = getToken();
        type = token.current.name.erase(0, 4);
        token = getToken();
        variableName = token.current.chr;

        generatorStack.push(type + " " + variableName);

        if (token.next.name == "ASSIGN") {
            getToken("ASSIGN");
            expression();
            generatorStack.push("STA " + variableName + " _");
        }

        token = getToken();
        if (token.current.name == "COMMA") functionDeclaration();
    }

    void assignment() {
        std::string tcn, variableName;
        token = getToken("SYMBOL");
        variableName = token.current.chr;
        token = getToken();
        tcn = token.current.name;
        
        /*
            Check special operators ++ and --.
        */
        if (tcn == "ADD ONE") {
            generatorStack.push("LDA " + variableName);
            generatorStack.push("ADD _ 1");
        }
        else if (tcn == "SUB ONE") {
            generatorStack.push("LDA " + variableName);
            generatorStack.push("SUB _ 1");
        }
        else expression();        

        /*
            Check if self operate.
            Example: i += 1; n **= 2;
        */
        if (tcn.find("SELF ") == 0) {
            tcn = tcn.erase(0, 5);
            generatorStack.push("LDA " + variableName);
            generatorStack.push(tcn + " _ _");
        }

        generatorStack.push("STA " + variableName + " _");

        if (token.next.name == "SEMICOLON") statement();
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
        std::string tcn = token.current.name, tcc = token.current.chr, tnn = token.next.name, tnc = token.next.chr, functionName, arrayName;
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
            arrayName = tcc, params = 0;
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
            
            std::string instruction = "LDAA";
            if (token.next.name == "ASSIGN") instruction = "STAA";
            generatorStack.push(instruction + " " + arrayName + " " + std::to_string(params));
        }
        else generatorStack.push("LDA " + tcc);
    }

    void functionStatement () {
        token = getToken("SYMBOL");
        generatorStack.push(":" + token.current.chr);

        token = getToken("OPEN PAREN");
            if (token.next.name != "CLOSE PAREN") {
                functionDeclaration(); // Special declaration using on function statement.
                pointer--; // Pointer back
            }
        getToken("CLOSE PAREN");
        getToken("OPEN BRACE");
            statement();
        getToken();
        statement();
    }

    void forStatement () {
        getToken("OPEN PAREN");
            delcaration("", false); // Called by a for-loop, prevent to return to statement.
        getToken("SEMICOLON");
            expression();
        getToken("SEMICOLON");
            assignment();
        getToken("CLOSE PAREN");
        getToken("OPEN BRACE");
            statement();
        getToken("CLOSE BRACE");
        statement();
    }

    void whileStatement () {
        getToken("OPEN PAREN");
            expression();
        getToken("CLOSE PAREN");
        getToken("OPEN BRACE");
            statement();
        getToken("CLOSE BRACE");
        statement();
    }

    void ifStatement () {
        getToken("OPEN PAREN");
            expression();
        getToken("CLOSE PAREN");
        getToken("OPEN BRACE");
            statement();
        token = getToken("CLOSE BRACE");

        if (token.next.name == "ELSE") elseStatement();
        else if (token.next.name == "ELSE IF") elseIfStatement();
        else statement();
    }

    void elseStatement () {
        getToken("ELSE");
        getToken("OPEN BRACE");
            statement();
        getToken("CLOSE BRACE");
        statement();
    }

    void elseIfStatement () {
        getToken("ELSE IF");
        getToken("OPEN PAREN");
            expression();
        getToken("CLOSE PAREN");
        getToken("OPEN BRACE");
            statement();
        token = getToken("CLOSE BRACE");

        if (token.next.name == "ELSE") elseStatement();
        else if (token.next.name == "ELSE IF") elseIfStatement();
        else statement();
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

            if (tnn == "CLOSE PAREN" || tnn == "CLOSE BRACK" || tnn == "CLOSE BRACE" || tnn == "SEMICOLON" || tnn == "COLON" || tnn == "COMMA" || tnn == "ASSIGN" || tnn == "EOF") {
                while (!operatorStack.empty()) {
                    if (operatorStack.top() != ";") generatorStack.push(operatorToName.at(operatorStack.top()) + " _ _");
                    operatorStack.pop();
                }
                break;
            }
        }
    }
};