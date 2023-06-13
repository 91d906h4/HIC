#include <fstream>
#include <string>
#include <vector>
#include <regex>
#include <map>

/*
    DFA-Based Lexer
*/
class Lexer {
public:
    std::vector<std::vector<std::string>> lex (std::string filename) {
        std::ifstream input(filename);
        std::string temp = "";

        while (input >> std::noskipws >> chr) {
            temp = chr;
            program += chr;
        }

        // Append end char.
        program += "\n";

        // Get the length of program.
        length = program.length();

        while (pointer < length) {
            chr = program[pointer];
            
            switch (state) {
                case 0: state0(); break;
                case 1: state1(); break;
                case 2: state2(); break;
                case 3: state3(); break;
                case 4: state4(); break;
                case 5: state5(); break;
                case 6: state6(); break;
                case 7: state7(); break;
                case 8: state8(); break;
                case 9: state9(); break;
                case 10: state10(); break;
                case 11: state11(); break;
                case 12: state12(); break;
                case 13: state13(); break;
                case 14: state14(); break;
                case 15: state15(); break;
                case 16: state16(); break;
                case 17: state17(); break;
                case 18: state18(); break;
            //  case 19: state19(); break;
                case 20: state20(); break;
                case 21: state21(); break;
                case 22: state22(); break;
                case 23: state23(); break;
                case 24: state24(); break;
                case 25: state25(); break;
                case 26: state26(); break;
                case 27: state27(); break;
                case 28: state28(); break;
                case 29: state29(); break;
                case 30: state30(); break;
                case 31: state31(); break;
                default: state0(); break;
            }

            pointer++;
        }

        // Push 2 semicolons to the end of program to prevent empty file inputs.
        result.push_back({"SEMICOLON", ";"});
        result.push_back({"SEMICOLON", ";"});

        return result;
    }

private:
    std::vector<std::vector<std::string>> result;
    std::string token = "", program = "";

    const std::string INTEGER_0_9 = "0123456789";
    const std::string INTEGER_1_9 = "123456789";
    const std::string STRING_a_z_A_Z = "_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
    const std::string STRING_0_9_a_z_A_Z = "_0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";

    char chr;
    int state = 0, pointer = 0, length = 0;

    void makeToken (std::string type) {
        result.push_back({type, token});
        state = 0;
        token = "";
    }

    // Ignore specific char.
    void ignoreToken () { };

    void state0 () {
        if (chr == '\n' || chr == ' ') ignoreToken();
        else token += chr;

        if (chr == '0') state = 1;
        else if (chr == '"') state = 5;
        else if (chr == '-') state = 8;
        else if (chr == '\'') state = 9;
        else if (chr == '+') state = 12;
        else if (chr == '/') state = 13;
        else if (chr == '*') state = 17;
        else if (chr == '>') state = 20;
        else if (chr == '<') state = 22;
        else if (chr == '%') state = 24;
        else if (chr == '|') state = 25;
        else if (chr == '&') state = 26;
        else if (chr == '^') state = 27;
        else if (chr == '=') state = 28;
        else if (chr == '!') state = 29;
        else if (chr == '@') state = 30;

        else if (chr == '(') makeToken("OPEN PAREN");
        else if (chr == ')') makeToken("CLOSE PAREN");
        else if (chr == '[') makeToken("OPEN BRACK");
        else if (chr == ']') makeToken("CLOSE BRACK");
        else if (chr == '{') makeToken("OPEN BRACE");
        else if (chr == '}') makeToken("CLOSE BRACE");
        else if (chr == ';') makeToken("SEMICOLON");
        else if (chr == ':') makeToken("COLON");
        else if (chr == ',') makeToken("COMMA");
        else if (chr == '#') makeToken("SHARP");

        else if (INTEGER_1_9.find(chr) != -1) state = 4;
        else if (STRING_a_z_A_Z.find(chr) != -1) state = 7;

        else ignoreToken(); // Ignore unexpected char.
    }

    void state1 () {
        if (chr == '.') {
            token += chr;
            state = 2;
        }
        else {
            makeToken("INTEGER");
            pointer--;
        }
    }

    void state2 () {
        if (INTEGER_0_9.find(chr) != -1) {
            token += chr;
            state = 3;
        }
        else {
            makeToken("ERROR");
            pointer--;
        }
    }

    void state3 () {
        if (INTEGER_0_9.find(chr) != -1) {
            token += chr;
        }
        else {
            makeToken("FLOAT");
            pointer--;
        }
    }

    void state4 () {
        if (INTEGER_0_9.find(chr) != -1) {
            token += chr;
        }
        else if (chr == '.') {
            token += chr;
            state = 2;
        }
        else {
            makeToken("INTEGER");
            pointer--;
        }
    }

    /*
        State 5:
        char == '"': from state 0 -> 5, or from state 5 -> 0.
        char == '/': ignore any char after reverse slash (\).
        else: add to string.
    */
    void state5 () {
        if (chr == '"') {
            token += chr;
            makeToken("STRING");
        }
        else if (chr == '\\') {
            token += chr;
            state = 6;
        }
        else {
            token += chr;
        }
    }

    /*
        State 6:
        ignore any char after reverse slash (\).
    */
    void state6 () {
        token += chr;
        state = 5;
    }

    void state7 () {
        if (STRING_0_9_a_z_A_Z.find(chr) != -1) {
            token += chr;
        }
        else {
            if (token == "if") makeToken("IF");
            else if (token == "elif")       makeToken("ELSE IF");
            else if (token == "else")       makeToken("ELSE");

            else if (token == "int")        makeToken("DEC INT");
            else if (token == "float")      makeToken("DEC FLOAT");
            else if (token == "string")     makeToken("DEC STRING");
            else if (token == "bool")       makeToken("DEC BOOL");
            else if (token == "list")       makeToken("DEC LIST");
            else if (token == "dict")       makeToken("DEC DICT");

            else if (token == "while")      makeToken("WHILE");
            else if (token == "for")        makeToken("FOR");
            else if (token == "break")      makeToken("BREAK");

            else if (token == "and")        makeToken("LAND");
            else if (token == "or")         makeToken("LOR");
            else if (token == "not")        makeToken("LNOT");

            else if (token == "true")       makeToken("TRUE");
            else if (token == "false")      makeToken("FALSE");
            else if (token == "null")       makeToken("NULL");

            else if (token == "function")   makeToken("FUNCTION");
            else if (token == "return")     makeToken("RETURN");
            else if (token == "import")     makeToken("IMPORT");

            else makeToken("SYMBOL");

            pointer--;
        }
    }

    void state8 () {
        if (chr == '-') {
            token += chr;
            makeToken("SUB ONE");
        }
        else if (chr == '=') {
            token += chr;
            makeToken("SELF SUB");
        }
        else if (chr == '0') {
            token += chr;
            state = 1;
        }
        else if (INTEGER_1_9.find(chr) != -1) {
            token += chr;
            state = 4;
        }
        else {
            makeToken("SUB");
            pointer--;
        }
    }

    /*
        State 9:
        char == '\'': from state 0 -> 9, or from state 9 -> 0.
        char == '/': ignore any char after reverse slash (\).
        else: add to string.
    */
    void state9 () {
        if (chr == '\'') {
            makeToken("ERROR");
            pointer--;
        }
        else if (chr == '\\') {
            token += chr;
            state = 10;
        }
        else {
            token += chr;
            state = 11;
        }
    }

    /*
        State 10:
        ignore any char after reverse slash (\).
    */
    void state10 () {
        token += chr;
        state = 11;
    }

    void state11 () {
        if (chr == '\'') {
            token += chr;
            makeToken("CHAR");
        }
        else {
            makeToken("ERROR");
            pointer--;
        }
    }

    void state12 () {
        if (chr == '+') {
            token += chr;
            makeToken("ADD ONE");
        }
        else if (chr == '=') {
            token += chr;
            makeToken("SELF ADD");
        }
        else {
            makeToken("ADD");
            pointer--;
        }
    }

    void state13 () {
        if (chr == '/') {
            token += chr;
            state = 14;
        }
        else if (chr == '*') {
            token += chr;
            state = 15;
        }
        else if (chr == '=') {
            token += chr;
            makeToken("SELF DIV");
        }
        else {
            makeToken("DIV");
            pointer--;
        }
    }

    void state14 () {
        if (chr == '\n') {
            makeToken("COMMENT");
            pointer--;
        }
        else {
            token += chr;
        }
    }

    void state15 () {
        if (chr == '*') {
            token += chr;
            state = 16;
        }
        else if (chr == '\n') ignoreToken();
        else {
            token += chr;
        }
    }

    void state16 () {
        if (chr == '/') {
            token += chr;
            makeToken("COMMENT");
        }
        else if (chr == '\n') ignoreToken();
        else {
            token += chr;
            state = 15;
        }
    }

    void state17 () {
        if (chr == '*') {
            token += chr;
            state = 18;
        }
        else if (chr == '=') {
            token += chr;
            makeToken("SELF MUL");
        }
        else {
            makeToken("MUL");
            pointer--;
        }
    }

    void state18 () {
        if (chr == '=') {
            token += chr;
            makeToken("SELF EXP");
        }
        else {
            makeToken("EXP");
            pointer--;
        }
    }

    void state20 () {
        if (chr == '>') {
            token += chr;
            state = 21;
        }
        else if (chr == '=') {
            token += chr;
            makeToken("EOGT"); // Equal Or Greater Than
        }
        else {
            makeToken("GREATER THAN");
            pointer--;
        }
    }

    void state21 () {
        if (chr == '=') {
            token += chr;
            makeToken("SELF BRS");
        }
        else {
            makeToken("BRS"); // Bit Right Shift
            pointer--;
        }
    }

    void state22 () {
        if (chr == '<') {
            token += chr;
            state = 23;
        }
        else if (chr == '=') {
            token += chr;
            makeToken("EOLT"); // Equal Or Less Than
        }
        else {
            makeToken("LESS THAN");
            pointer--;
        }
    }

    void state23 () {
        if (chr == '=') {
            token += chr;
            makeToken("SELF BLS");
        }
        else {
            makeToken("BLS"); // Bit Left Shift
            pointer--;
        }
    }

    void state24 () {
        if (chr == '=') {
            token += chr;
            makeToken("SELF REM");
        }
        else {
            makeToken("REM");
            pointer--;
        }
    }

    void state25 () {
        if (chr == '=') {
            token += chr;
            makeToken("SELF BOR");
        }
        else {
            makeToken("BOR"); // Bit OR
            pointer--;
        }
    }

    void state26 () {
        if (chr == '=') {
            token += chr;
            makeToken("SELF BAND");
        }
        else {
            makeToken("BAND"); // Bit AND
            pointer--;
        }
    }

    void state27 () {
        if (chr == '=') {
            token += chr;
            makeToken("SELF BXOR");
        }
        else {
            makeToken("BXOR"); // Bit XOR
            pointer--;
        }
    }

    void state28 () {
        if (chr == '=') {
            token += chr;
            makeToken("EQUAL");
        }
        else {
            makeToken("ASSIGN");
            pointer--;
        }
    }

    void state29 () {
        if (chr == '=') {
            token += chr;
            makeToken("NOT EQUAL");
        }
        else {
            makeToken("LNOT"); // Logical NOT
            pointer--;
        }
    }

    void state30 () {
        if (chr == '@') {
            token += chr;
            state = 31;
        }
        else {
            makeToken("AT MARK"); // Bit Left Shift
            pointer--;
        }
    }

    void state31 () {
        makeToken("DUBLE AT MARK");
        pointer--;
    }
};