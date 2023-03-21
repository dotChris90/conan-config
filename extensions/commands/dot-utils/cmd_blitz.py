from conan.api.conan_api import ConanAPI
from conan.api.output import ConanOutput, Color
from conan.cli.command import OnceArgument, conan_command
from conans.client.userio import UserInput

from os.path import join as pathJoin
from os import getcwd, mkdir
from shutil import move, rmtree
from os import mkdir, system, devnull
from glob import glob
from subprocess import check_call, STDOUT, Popen, PIPE
from pathlib import Path
from time import sleep
from json import dumps as json_dumps
from re import compile, VERBOSE

recipe_color = Color.BRIGHT_BLUE
removed_color = Color.BRIGHT_YELLOW

ansi_escape = compile(r'''
    \x1B  # ESC
    (?:   # 7-bit C1 Fe (except CSI)
        [@-Z\\-_]
    |     # or [ for CSI, followed by a control sequence
        \[
        [0-?]*  # Parameter bytes
        [ -/]*  # Intermediate bytes
        [@-~]   # Final byte
    )
''', VERBOSE)


@conan_command(group="dotChris90 utils")
def blitz(conan_api: ConanAPI, parser, *args):
    """
    Do everything at once (clean, install, cppcheck, build, doc )
    """

    parser.add_argument('--conanfile',action=OnceArgument,
                        help="path to conanfile.py")
    parser.add_argument('--profile',action=OnceArgument,
                        help="profile for target")
    
    args = parser.parse_args(*args)

    conan_root_folder = Path(args.conanfile).parent.absolute()
    buildDir = pathJoin(conan_root_folder,"build")    

    if Path(buildDir).exists():
        rmtree(buildDir)

    cmd = [
        "conan",
        "install",
        "--profile:build=default",
        "--profile:host={}".format(args.profile),
        args.conanfile,
        "--build=missing",
        "--output-folder={}".format(conan_root_folder)
    ]

    code = Popen(cmd).wait()

    cmd = [
        "conan",
        "install", 
        "--requires",
        "cppcheck/2.10",
         "--deploy=bin",
         "--output-folder={}".format(buildDir)
    ]

    code = Popen(cmd).wait()

    cmake_user_presets = pathJoin(conan_root_folder,"CMakeUserPresets.json")
    cmake_user_presets_2 = pathJoin(buildDir,"CMakeUserPresets.json")

    try:
        if Path(cmake_user_presets).exists():
            move(cmake_user_presets,cmake_user_presets_2)
        else:
            sleep(1)
    except FileNotFoundError:
        pass

    cppcheck_bin = pathJoin(buildDir,"bin","cppcheck")
    cppcheck_out = pathJoin(buildDir,"cppcheck.txt")
    cppcheck_in  = pathJoin(conan_root_folder,"src")

    counter = 0
    while(not Path(cppcheck_bin).exists()):
        sleep(1)
        counter = counter+1
        if (counter == 10):
            raise Exception("cppcheck is not installed ....")

    cmd = [
        cppcheck_bin,
        "--enable=all",
        "--cppcheck-build-dir={}".format(buildDir),
        "--output-file={}".format(cppcheck_out),
        "{}".format(cppcheck_in)
    ]

    Popen(cmd).wait()

    error_pattern = ": error: "

    with open(cppcheck_out,"r",encoding="utf-8") as out:
        result_lines = out.readlines()
        contains_error = False
        for result_line in result_lines:
            result_line = ansi_escape.sub("", result_line)
            if error_pattern in result_line:
                contains_error = True
                break
        if contains_error:
            raise Exception("cppcheck detects errors")

    cmd = [
        "conan",
        "build",
        args.conanfile
    ]

    Popen(cmd).wait()
    
    a = 1
    