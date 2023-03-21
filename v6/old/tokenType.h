#include <string>
#include <regex>

using namespace std;

string tokenType(string target) {
    smatch m;

    if (regex_match(target, m, regex(R"(^-?[1-9][0-9]*$|^0$)"))) return "<INTEGER>";
    else if (regex_match(target, m, regex(R"(^-?[0-9]+\.[0-9]+$)"))) return "<FLOAT>";
    else if (regex_match(target, m, regex(R"(^\".*\"$)"))) return "<STRING>";
    else if (regex_match(target, m, regex(R"(true|false|null)"))) return "<BOOLEAN>";
    else if (regex_match(target, m, regex(R"(int|float|string|bool)"))) return "<ID TYPE>";
    else if (regex_match(target, m, regex(R"(^[a-zA-Z_][0-9a-zA-Z_]*$)"))) return "<SYMBOL>";
    else if (target == ";") return "<SEMICOLON>";
    else if (target == ",") return "<COMMA>";
    else if (target == "=") return "<ASSIGNMENT>";
    else if (target == "->") return "<CHILD>";
    else if (target == "==") return "<EQUAL MARK>";
    else if (target == "!=") return "<NOT EQUAL MARK>";
    else if (target == ">") return "<GREATER THAN MARK>";
    else if (target == "<") return "<LESS THAN MARK>";
    else if (target == ">=") return "<GREATER THAN OR EQUAL MARK>";
    else if (target == "<=") return "<LESS THAN OR EQUAL MARK>";
    else if (target == "++") return "<PLUS ONE>";
    else if (target == "+") return "<ADDITION>";
    else if (target == "-") return "<SUBTRACTION>";
    else if (target == "*") return "<MULTIPLICATION>";
    else if (target == "/") return "<DIVISION>";
    else if (target == "**") return "<EXPONENTITATION>";
    else if (target == "%") return "<REMAINDER>";
    else if (target == "<<") return "<BIT LEFT SHIFT>";
    else if (target == ">>") return "<BIT RIGHT SHIFT>";
    else if (target == "&") return "<BIT AND>";
    else if (target == "|") return "<BIT OR>";
    else if (target == "^") return "<BIT XOR>";
    else if (target == "and") return "<LOGICAL AND>";
    else if (target == "or") return "<LOGICAL OR>";
    else if (target == "not") return "<LOGICAL NOT>";
    else if (target == "(") return "<LEFT PARN>";
    else if (target == ")") return "<RIGHT PARN>";
    else if (target == "[") return "<LEFT BRACKET>";
    else if (target == "]") return "<RIGHT BRACKET>";
    else if (target == "{") return "<LEFT BRACE>";
    else if (target == "}") return "<RIGHT BRACE>";
    else if (target == "//") return "<COMMENT>";
    else if (target == "/*") return "<COMMENT>";
    else if (target == "*/") return "<COMMENT>";
    else if (target == "<NEW LINE>") return "<NEW LINE>";

    return "<ERROR>";
}