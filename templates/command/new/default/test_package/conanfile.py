
import os
from conans import ConanFile, tools
from conan.tools.cmake import CMake, cmake_layout, CMakeToolchain, CMakeDeps


class TestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    apply_env = False
    requires = ["gtest/1.11.0"]

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        cmake = CMakeDeps(self)
        cmake.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def layout(self):
        cmake_layout(self)

    def test(self):
        if not tools.cross_building(self):
            cmd = os.path.join(self.cpp.build.bindirs[0], "pkg_test")
            if self.settings.build_type == "Debug":
                self.output.info("-----------------------------")
                self.output.info("|Skip Test because Debug ...|")
                self.output.info("-----------------------------")
            else:
                self.run(cmd)
        else:
            self.output.info("-----------------------------------")
            self.output.info("|Skip Test because Cross build ...|")
            self.output.info("-----------------------------------")
            self.run(cmd, env="conanrun")
