#include <iostream>
#include <regex>


int main(int argc, const char *argv[]) {
    std::smatch match;
    std::string message = "Hello nickname.";
    std::string matcher = "\\bnickname\\b";

    try {
        std::regex expression = std::regex(matcher, std::regex_constants::ECMAScript | std::regex_constants::icase);
        std::regex_search(message, match, expression);
    } catch (std::regex_error& error) {
        std::cout << "Your C++ compiler doesn't properly support regex. Please upgrade to GCC 4.9, Clang or newer.\n";
        return 1;
    }

    if (match.empty()) {
        return 1;
    }

    return 0;
}
