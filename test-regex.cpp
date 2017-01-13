#include <iostream>
#include <regex>


int main(int argc, const char *argv[]) {
    std::smatch match;
    std::string message = "Hello nickname.";
    std::string matcher = "\\bnickname\\b";

    std::regex expression = std::regex(matcher, std::regex_constants::ECMAScript | std::regex_constants::icase);
    std::regex_search(message, match, expression);

    if (match.empty()) {
        return 1;
    }

    return 0;
}
