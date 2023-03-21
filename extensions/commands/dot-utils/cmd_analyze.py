from conan.api.conan_api import ConanAPI
from conan.api.output import ConanOutput, Color
from conan.cli.command import OnceArgument, conan_command
from conans.client.userio import UserInput

from tempfile import TemporaryDirectory
from os.path import join as pathJoin
from os import getcwd
from shutil import copyfile
from os import mkdir, system, devnull
from glob import glob
from subprocess import check_call, STDOUT, Popen, PIPE
from pathlib import Path
from time import sleep
from json import dumps as json_dumps

from .analyzer import ConanPkgAnalyzer, CMakeFileAnalyzer
from .formats import OutFormat

recipe_color = Color.BRIGHT_BLUE
removed_color = Color.BRIGHT_YELLOW


@conan_command(group="dotChris90 utils")
def analyze(conan_api: ConanAPI, parser, *args):
    """
    analyze files e.g. cmake or conan packages
    """

    parser.add_argument('--conan-package', action='append',
                        help='package to determine targets')
    parser.add_argument('--cmakefile',action=OnceArgument,
                        help="path to cmakefile.txt")
    parser.add_argument('--out-format',action=OnceArgument,
                        help="currently supports json")
    parser.add_argument('--out-file',action=OnceArgument,
                        help="name of destination file")
    
    conan_out = ConanOutput()
    conan_in = UserInput(non_interactive=False)

    args = parser.parse_args(*args)

    if args.out_format == "json":
        out_format = OutFormat.JSON
    else: 
        out_format = OutFormat.TXT
    if args.out_file == None:
        out_format = OutFormat.TXT

    out_object = None
    if out_format == OutFormat.TXT:
        out_object = []
    elif out_format == OutFormat.JSON:
        out_object = {}
    else:
        pass

    conan_pkg_analyzer = ConanPkgAnalyzer(conan_out) if args.conan_package else None
    if conan_pkg_analyzer:
        for idx in args.conan_package:
            conan_pkg_analyzer.add_conan_package(idx)
            sleep(1)
        conan_out.writeln("\n")
        components = conan_pkg_analyzer.determine_cmake_targets()
        conan_pkg_analyzer.append_cmake_targets_to_output(components,out_format,out_object)
    
    cmake_analyzer = CMakeFileAnalyzer(args.cmakefile) if args.cmakefile else None
    if cmake_analyzer:
        libs, exes = cmake_analyzer.determine_cmakelists_targets()
        cmake_analyzer.append_targets_to_output(exes,libs,out_format,out_object)
        
    if args.out_file != None and args.out_format == None:
        raise Exception("invalide combination - use --format in combination with --out-file")

    if out_format == OutFormat.JSON:
        content = json_dumps(out_object)

    if args.out_file:
        if not Path(args.out_file).exists():
                with open(args.out_file,"w") as file:
                    file.write(content)
        else:
            overwrite = conan_in.request_boolean("Overwrite existing file{}".format(Path(args.json).absolute()))
            if (overwrite):
                with open(args.out_file,"w") as file:
                    file.write(content)
    else:
        for idx in out_object:
            conan_out.writeln(idx)