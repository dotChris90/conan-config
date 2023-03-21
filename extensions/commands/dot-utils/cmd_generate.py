from conan.api.conan_api import ConanAPI
from conan.api.output import ConanOutput, Color
from conan.cli.command import OnceArgument, conan_command
from conans.client.userio import UserInput

from os.path import join as pathJoin
from os import getcwd
from shutil import copyfile
from os import mkdir, system, devnull
from glob import glob
from subprocess import check_call, STDOUT, Popen, PIPE
from pathlib import Path
from time import sleep
from json import dumps as json_dumps

recipe_color = Color.BRIGHT_BLUE
removed_color = Color.BRIGHT_YELLOW


@conan_command(group="dotChris90 utils")
def generate(conan_api: ConanAPI, parser, *args):
    """
    generate different files
    """

    parser.add_argument('--vscode-settings', default=False, action='store_true',
                        help='Generate settings file for vscode')
    parser.add_argument('--vscode-launch', default=False, action='store_true',
                        help='Generate launch file for vscode')
    parser.add_argument('--doxy', default=False, action='store_true',
                        help='Generate doxygen file')
    parser.add_argument('--clang', default=False, action='store_true',
                        help='Generate .clang-tidy and .clang-format')
    parser.add_argument('--all', default=False, action='store_true',
                        help='Generate all files')
    parser.add_argument('--dst',action=OnceArgument,
                        help="destination folder",default=getcwd())
    
    args = parser.parse_args(*args)

    conan_out = ConanOutput()

    clang_tidy_path = pathJoin(
            Path(__file__).parent,
            "templates",
            ".clang-tidy"
        )
    
    clang_format_path = pathJoin(
            Path(__file__).parent,
            "templates",
            ".clang-format"
        )
    
    doxyfile_path = pathJoin(
            Path(__file__).parent,
            "templates",
            "Doxyfile"
        )
    
    vscode_settings_path = pathJoin(
            Path(__file__).parent,
            "templates",
            ".vscode",
            "settings.json"
        )

    dst = Path(args.dst).absolute()
    
    if args.all:

        file_dst = pathJoin(dst,".clang-tidy")
        copyfile(clang_tidy_path,file_dst)
        conan_out.writeln(".clang-tidy at {}".format(file_dst))

        file_dst = pathJoin(dst,".clang-format")
        copyfile(clang_format_path,file_dst)
        conan_out.writeln(".clang-format at {}".format(file_dst))


        file_dst = pathJoin(dst,"Doxyfile")
        copyfile(doxyfile_path,file_dst)
        conan_out.writeln("Doxyfile at {}".format(file_dst))
    else:
        if args.clang:
            file_dst = pathJoin(dst,".clang-tidy")
            copyfile(clang_tidy_path,file_dst)
            conan_out.writeln(".clang-tidy at {}".format(file_dst))

            file_dst = pathJoin(dst,".clang-format")
            copyfile(clang_format_path,file_dst)
            conan_out.writeln(".clang-format at {}".format(file_dst))
        if args.doxy:
            file_dst = pathJoin(dst,"Doxyfile")
            copyfile(doxyfile_path,file_dst)
            conan_out.writeln("Doxyfile at {}".format(file_dst))
        if args.vscode_settings:
            dst = pathJoin(dst,".vscode")
            if not Path(dst).exists():
                mkdir(dst)                
            file_dst = pathJoin(dst,"settings.json")
            copyfile(vscode_settings_path,file_dst)
            conan_out.writeln("Doxyfile at {}".format(file_dst))

            # conan install . --deploy=include
            cmd = [
                "conan",
                "install",
                
            ]


