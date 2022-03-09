
from json import tool
from conans import ConanFile
from conans import tools
from conan.tools.cmake import CMakeToolchain, CMake, CMakeDeps
from conan.tools.layout import cmake_layout


class {{package_name}}Conan(ConanFile):

    name = "{{ name }}"
    version = "{{ version }}"

    # Optional metadata
    license = "<Put the package license here>"
    author = "<Put your name here> <And your email here>"
    url = "<Package recipe repository url here, for issues about the package>"
    description = "<Description of {{ name }} here>"
    topics = ("<Put some tag here>", "<here>", "<and here>")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    # Sources are located in the same place as this recipe, copy them to the recipe
    exports_sources = [
        "CMakeLists.txt",
        "src/*"
    ]

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def requirements(self):
        self.requires("fmt/8.1.1")
        self.requires("ms-gsl/4.0.0")

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        cmake = CMakeDeps(self)
        cmake.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.components["Log"].libs = ["Log"]
        self.cpp_info.components["Log"].requires = ["fmt::fmt"]
        self.cpp_info.components["Log"].libdirs = ["lib"]
        self.cpp_info.components["Log"].includedirs = ["include"]
        self.cpp_info.components["ILog"].libdirs = ["lib"]
        self.cpp_info.components["ILog"].includedirs = ["include"]
