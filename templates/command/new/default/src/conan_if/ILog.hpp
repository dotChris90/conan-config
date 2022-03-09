#ifndef B0C147B1_8C54_415A_81AC_3D3FBF1035A0
#define B0C147B1_8C54_415A_81AC_3D3FBF1035A0

#include <string>

namespace conan_if {
class ILog {
 private:
  /* data */
 public:
  virtual ~ILog() = default;
  virtual auto LogMsg(const std::string& msg) -> void = 0;
  virtual auto LogErr(const std::string& msg) -> void = 0;
};

}  // namespace conan_if

#endif /* B0C147B1_8C54_415A_81AC_3D3FBF1035A0 */
