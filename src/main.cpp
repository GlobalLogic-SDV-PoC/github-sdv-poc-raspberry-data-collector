#include <fstream>

#include "dcol/app.hpp"

int main()
{
    constexpr const char* kConfigPath = "/var/config/main_config.json";

    dcol::App app(nlohmann::json::parse(std::ifstream(kConfigPath)));
    app.initDefaultLogger("logs/logs.txt", 10'485'760, 3, std::chrono::seconds(5));
    app.init();
    app.start();
}
