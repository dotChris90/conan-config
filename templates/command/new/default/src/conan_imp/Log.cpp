#include "Log.hpp"

#include <iostream>

#include "fmt/format.h"

namespace conan_imp {
Log::Log(/* args */) = default;

Log::~Log() = default;

auto Log::LogMsg(const std::string& msg) -> void {
  fmt::print("Logging normal msg --> {}.", msg);
}

auto Log::LogErr(const std::string& msg) -> void {
  fmt::print("Logging error msg --> {}.", msg);
}
}  // namespace conan_imp