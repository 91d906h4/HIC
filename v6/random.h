#include <string>
#include <time.h>

std::string virtualAddressGenerator (int length = 16) {
    std::string result = "";

    const char alphabet[26] = { 'A', 'B', 'C', 'D', 'E', 'F', 'G',
                             'H', 'I', 'J', 'K', 'L', 'M', 'N',
                             'O', 'P', 'Q', 'R', 'S', 'T', 'U',
                             'V', 'W', 'X', 'Y', 'Z' };

    for (int i = 0; i < length; i++) result = result + alphabet[rand() % 26];

    return result;
}