from subprocess import Popen, PIPE, STDOUT
from os.path import join as pathJoin
from tempfile import TemporaryDirectory
from pathlib import Path
from typing import List
from os import mkdir, system, devnull
from glob import glob
from os.path import basename
from json import dumps as json_dumps

from .errors import InvalidPackageFormat
from .formats import OutFormat

class ConanPkg:

    def __init__(self, package_name : str):

        try:
            part_1, part_2 = package_name.split("@")
        except ValueError:
            part_1 = package_name
            part_2 = "_/_"

        self._name, self._version = part_1.split("/")
        self._postfix1, self._postfix2 = part_2.split("/")

        if self._version == None:
            raise InvalidPackageFormat()
        
    def get_pkg_full_name(self) -> str:
        return "{}/{}@{}/{}".format(
            self._name,
            self._version,
            self._postfix1,
            self._postfix2
        )
    
    def is_present_in_cache(self) -> bool:
        cmd = ["conan","list",self.get_pkg_full_name()]
        proc = Popen(cmd, stderr=PIPE, stdout=PIPE)
        proc.wait()
        out = proc.stdout.readlines()
        return not ("  ERROR: Recipe " in str(out[1]))

class ConanPkgAnalyzer:

    def __init__(self, out) -> None:
        self._pkgs = []
        self._out = out
    
    def add_conan_package(self, name : str) -> bool:
        self._pkgs.append(ConanPkg(name))
        is_in_cache = self._pkgs[-1].is_present_in_cache()
        if is_in_cache:
            self._out.warning("package {} not present in cache - determination takes time .... ".format(self._pkgs[-1].get_pkg_full_name()))
        else:
            self._out.writeln("package {} present in cache".format(self._pkgs[-1].get_pkg_full_name()))

    def get_all_conan_packages(self) -> List[str]:
        pkgs = []
        for pkg in self._pkgs:
            pkgs.append(pkg.get_pkg_full_name())
        return pkgs

    def determine_cmake_targets(self) -> List[str]:
        with TemporaryDirectory() as tmpDir:
            conanfilePath = pathJoin(tmpDir,"conanfile.py")
            conanfile = open(conanfilePath,"w")
            conanfileTemplate = pathJoin(
                Path(__file__).parent,
                "templates",
                "conanfile.py"
            )
        
            conanfileContent = []
            with open(conanfileTemplate,"r") as conantem:
                conanfileContent = conantem.readlines()
                req = "\",\"".join(self.get_all_conan_packages()) 
                conanfileContent[22] = "    requires = [\"{}\"]".format(req)
                conanfile.writelines(conanfileContent)
                conanfile.flush()
            
            conanfile.close()

            buildDir = pathJoin(tmpDir,"build")
            mkdir(buildDir)
            cmd = ["conan",
                   "install", 
                    conanfilePath
            ]
            with open(devnull, 'wb') as devnullvar:
                Popen(cmd, stdout=devnullvar, stderr=STDOUT).wait()
                search_pattern = pathJoin(
                    buildDir,
                    "Release", 
                    "generators",
                    "*-Target-release.cmake"
                )
                cmakeFiles = glob(search_pattern)
                find_package = []
                for cmakefile in cmakeFiles:
                    cmakefile_name = basename(cmakefile)
                    cmakefile_name = cmakefile_name.replace("-Target-release.cmake","")
                    find_package.append(cmakefile_name)
        
                cmake_find_pakage_file = pathJoin(tmpDir,"CMakeLists.txt")
                with open(cmake_find_pakage_file,"w") as cmakefind_package_file_fd:
                    cmakefind_package_file_fd.write("cmake_minimum_required(VERSION 3.10)\n")
                    for idx in find_package:
                        cmakefind_package_file_fd.write("find_package({})\n".format(idx))

                cmd = [
                    "conan",
                    "build",
                    conanfilePath
                ]

                proc = Popen(cmd, stderr=PIPE, stdout=PIPE, cwd=buildDir)
                proc.wait()
                out = proc.stdout.readlines()
                err = proc.stderr.readlines()
                out = out if len(out) != 0 else err

                components = []
                for idx in out:
                    idx = str(idx)
                    if ("-- Conan: Target declared" in idx):
                        components.append(
                            idx.replace("-- Conan: Target declared ","")
                            .replace("\\n","")
                            .replace("'","")
                        )
                    if ("-- Conan: Component target declared " in idx):
                        components.append(
                            idx.replace("-- Conan: Component target declared ","")
                            .replace("\\n","")
                            .replace("'","")
                        )

                for idx in range(0,len(components)):
                    components[idx] = components[idx][2:-1]
                
                return components

    def append_cmake_targets_to_output(self, targets, format, output ):
        if (format == OutFormat.TXT):
            output.append("Found targets in conan packages {}:\n".format(self.get_all_conan_packages()))
            for idx in targets:
                output.append("    - {}".format(idx))
            output.append("")
        elif (format == OutFormat.JSON):
            json = output
            json['dot-utils.analyze.conan.packages'] = self.get_all_conan_packages()
            json['dot-utils.analyze.conan.cmake-targets'] = targets
                    
class CMakeFileAnalyzer:

    def __init__(self, cmakefile):
        if not Path(cmakefile).exists():
            raise FileNotFoundError("{} is missing".format(cmakefile))
        if not cmakefile.endswith("CMakeLists.txt"):
            raise Exception("cmakefile must be a CMakeLists.txt file")
        self._cmakefile = str(Path(cmakefile).absolute())
        self._cmake_dir = Path(self._cmakefile).parent.absolute()
        self._build_dir = pathJoin(self._cmake_dir,"build")

    def determine_cmakelists_targets(self):

        out_lines = []
        with TemporaryDirectory() as tmpDir:
            dot_file = pathJoin(tmpDir,"graph.dot")
            cmd = [
                "cmake",
                "-B",
                self._build_dir,
                "-S",
                self._cmake_dir,
                "--graphviz={}".format(dot_file)
            ]
            with open(devnull, "w") as null_dev:
                Popen(cmd,stdout=null_dev, stderr=null_dev ).wait()

            with open(dot_file,"r") as file:
                out_lines = file.readlines()

        libs = []
        exes = []

        for out_line in out_lines:
            out_line = out_line.replace("b'... ","").replace("\\n","").replace("'","")
            if '"node' in out_line:
                if "shape = octagon" in out_line:
                    start = out_line.find('label = "')
                    end   = out_line.find('", shape =')
                    label = out_line[start+9:end]
                    libs.append(label)
                elif "shape = egg" in out_line:
                    start = out_line.find('label = "')
                    end   = out_line.find('", shape =')
                    label = out_line[start+9:end]
                    exes.append(label)
                else:
                    pass

        for idx in range(0,len(libs)):
            if "(" in libs[idx] and ")" in libs[idx]:
                start = libs[idx].find("(")
                end   = libs[idx].find(")")
                libs[idx] = libs[idx][start+1:end]
        
        for idx in range(0,len(exes)):
            if "(" in exes[idx] and ")" in exes[idx]:
                start = exes[idx].find("(")
                end   = exes[idx].find(")")
                exes[idx] = exes[idx][start+1:end]
                    
        return (libs,exes)

    def append_targets_to_output(self, exes, libs, format, output):
        if format == OutFormat.TXT:
            output.append("found libs in {} : \n".format(self._cmakefile))
            for lib in libs:
                output.append("- {}".format(lib))
            output.append("\nfound exes in {} : \n".format(self._cmakefile))
            for exe in exes:
                output.append("- {}".format(exe))
        elif format == OutFormat.JSON:
        
            json = output
            json["dot-utils.analyze.cmake-targets.cmakefile"] = self._cmakefile
            json["dot-utils.analyze.cmake-targets.exes"] = exes
            json["dot-utils.analyze.cmake-targets.libs"] = libs
            content = json_dumps(json)
