#ifndef D1EFE530_EE10_4996_8685_70E14521738C
#define D1EFE530_EE10_4996_8685_70E14521738C

#include "conan_if/ILog.hpp"

namespace conan_imp {
class Log : public conan_if::ILog {
 private:
  /* data */
 public:
  Log(/* args */);
  ~Log() override;
  auto LogMsg(const std::string& msg) -> void override;
  auto LogErr(const std::string& msg) -> void override;
};

}  // namespace conan_imp

#endif /* D1EFE530_EE10_4996_8685_70E14521738C */