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


def all_starts_with_prefix(str_arr, str_pref):
    all_starts_with_pref = True
    str_pref = str(str_pref)
    for idx in str_arr:
        idx = str(idx)
        if idx.startswith('b"'):
            idx = idx[2:-1]
        if not idx.startswith(str_pref):
            all_starts_with_pref=False
            break
    return all_starts_with_pref

@conan_command(group="dotChris90 utils")
def doc(conan_api: ConanAPI, parser, *args):
    """
    generate different documentations
    """

    parser.add_argument('--doxyfile',action=OnceArgument,
                        help="path to Doxyfile")
    
    args = parser.parse_args(*args)

    cmd = [
        "doxygen",
        args.doxyfile
    ]

    cwd = str(Path(args.doxyfile).parent.absolute())

    proc = Popen(cmd, stderr=PIPE)
    err = proc.stderr.readlines()

    if all_starts_with_prefix(err,"warning"):
        pass
    else:
        pass

