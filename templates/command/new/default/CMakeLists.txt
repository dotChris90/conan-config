
cmake_minimum_required(VERSION 3.15)
project({{name}} CXX)

include_directories("src")

find_package(fmt REQUIRED)
find_package(Microsoft.GSL REQUIRED)

add_library(ILog INTERFACE)

add_library(Log       src/conan_imp/Log.cpp
)     
target_link_libraries(Log fmt::fmt)

add_executable(main     src/main.cpp
)
target_link_libraries(main Log)




target_include_directories(Log PUBLIC src)
set_target_properties(Log PROPERTIES PUBLIC_HEADER "src/conan_imp/Log.hpp")

install(TARGETS Log

        DESTINATION "."
        ARCHIVE DESTINATION lib
        LIBRARY DESTINATION lib
        PUBLIC_HEADER DESTINATION include/conan_imp
)

install(FILES src/conan_if/ILog.hpp DESTINATION include/conan_if)
install(FILES src/conan_imp/Log.hpp DESTINATION include/conan_imp)
