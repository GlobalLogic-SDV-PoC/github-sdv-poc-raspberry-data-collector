cmake_minimum_required(VERSION 3.5.2)
project(
    data_collection
    LANGUAGES CXX
    VERSION 1.0.0)

set(CMAKE_CXX_STANDARD 17)

add_subdirectory(dep/internal/data_collector)

set(APP_NAME ${PROJECT_NAME}_app)
set(LIB_NAME ${PROJECT_NAME}_core)

add_executable(${APP_NAME} src/main.cpp)
target_link_libraries(${APP_NAME} PRIVATE ${LIB_NAME})
