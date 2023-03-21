#include <vector>
#include <string>

#include "tokenType.h"

using namespace std;

vector<string> tokenCleaner(vector<string> input) {
    vector<string> result;

    bool inSingleLineComment = false, inMultiLineComment = false;

    for (string text: input) {
        if (text == "//") inSingleLineComment = true;
        if (text == "/*") inMultiLineComment = true;

        // Ignore texts in comment and line breaks.
        if (!inSingleLineComment && ! inMultiLineComment && text != "\\n") result.push_back(text);
        

        if (text == "*/") inMultiLineComment = false;
        if (text == "\\n") inSingleLineComment = false;
    }

    return result;
}