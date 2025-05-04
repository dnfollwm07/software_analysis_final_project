#include <string>
#include <map>

std::map<std::string, std::string> store;

int get_config_int(const std::string& key) {
    return std::stoi(store[key]); // [INFER_WARNING] May throw if key not found or not int
}
