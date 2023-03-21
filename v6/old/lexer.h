#ifndef LEXER_H
#define LEXER_H

#include <fstream>
#include <string>
#include <vector>
#include <regex>

using namespace std;

vector<string> lexer() {
    ifstream input("test.hy");
    vector<string> result;
    string token = "", currentChar = "", nextChar = "", program = "";
    smatch m;

    bool inString = false, escapeChar = false;
    char chr; // Current char.
    int i = 0; // Pointer.

    while (input >> noskipws >> chr) {
        currentChar = chr;
        program += currentChar;
    }

    while (i < program.length()) {
        // Get current char.
        currentChar = program[i];
        nextChar = currentChar + program[i + 1];

        // Check if the next char is escape char.
        if (currentChar == "\\" && inString) {
            escapeChar = true;
            token += "\\";
            i++; continue;
        }
        // Check if in string.
        else if (currentChar == "\"" && !escapeChar) inString = !inString;

        // Match the following patterns: **, //, /*, */, ==, >=, <=, !=, ++, ->
        if (regex_match(nextChar, m, regex(R"(\*\*|\/\/|\/\*|\*\/|==|>=|<=|!=|\+\+|->)")) && !inString) {
            if (token != "") result.push_back(token);
            if (nextChar != " ") result.push_back(nextChar);
            token = "";
            i++;
        }
        // Match the following patterns: ' ', ;, ',', [, ], (, ), {, }, <, >, +, -, *, /, %, &, |, ^, \n
        else if (regex_match(currentChar, m, regex(R"( |=|;|,|\[|\]|\(|\)|\{|\}|<|>\+|\-|\*|\/|\%|\&|\||\^|\n)")) && !inString) {
            // Check if a line break.
            if (currentChar == "\n") currentChar = "\\n";
            if (token != "") result.push_back(token);
            if (currentChar != " ") result.push_back(currentChar);
            token = "";
        }
        else token += currentChar;

        // Escape char is the char behind the reverse slash.
        // If the previous char is escape char, then set the flag (escapeChar) to false.
        if (escapeChar) escapeChar = false;

        // Update pointer.
        i++;
    }

    // Push the last token.
    if (token != "") result.push_back(token);

    return result;
}

#endif