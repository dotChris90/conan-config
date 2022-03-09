#include "conan_imp/Log.hpp"

auto main() -> int {
  conan_imp::Log log;
  log.LogMsg("Hello World!");
  return 0;
}
