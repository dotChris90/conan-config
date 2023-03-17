from conan.api.conan_api import ConanAPI
from conan.api.output import ConanOutput, Color
from conan.cli.command import OnceArgument, conan_command
from conans.client.userio import UserInput

from tempfile import TemporaryDirectory
from os.path import join as pathJoin
from os.path import basename
from os import mkdir, system, devnull
from glob import glob
from subprocess import check_call, STDOUT, Popen, PIPE
from pathlib import Path
from time import sleep
from json import dumps as json_dumps

recipe_color = Color.BRIGHT_BLUE
removed_color = Color.BRIGHT_YELLOW


@conan_command(group="dotChris90 utils")
def cmaketargets(conan_api: ConanAPI, parser, *args):
    """
    list cmake targets of packages
    """

    parser.add_argument('--requires', action='append',
                        help='package to determine targets')
    parser.add_argument('--json',action=OnceArgument,
                        help="json output file")
    
    args = parser.parse_args(*args)

    conan_out = ConanOutput()
    conan_in = UserInput(non_interactive=False)

    pkg_not_in_cache = False

    for idx in args.requires:
        cmd = ["conan","list",idx]
        proc = Popen(cmd, stderr=PIPE, stdout=PIPE)

        out = proc.stdout.readlines()

        if ("  ERROR: Recipe " in str(out[1])):
            pkg_not_in_cache = True
            conan_out.warning("package {} not present in cache - determination takes time .... ".format(idx))
        else:
            conan_out.writeln("package {} present in cache".format(idx))
        sleep(1)
        

    conan_out.writeln("\n")

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
            req = "\",\"".join(args.requires) 
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
            check_call(cmd, stdout=devnullvar, stderr=STDOUT)
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

        if (args.json == None):
            conan_out.writeln("Found target :\n")
            for idx in components:
                conan_out.writeln("    - {}".format(idx))
        else:
            json = {}
            json['targets'] = components
            json_file_path = str(Path(args.json).absolute())
            if not Path(args.json).exists():
                with open(json_file_path,"w") as json_file:
                    json_file.write(json_dumps(json))
            else:
                overwrite = conan_in.request_boolean("Overwrite existing file{}".format(Path(args.json).absolute()))
                if (overwrite):
                    with open(json_file_path,"w") as json_file:
                        json_file.write(json_dumps(json))
                