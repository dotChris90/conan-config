from conan.tools.files import copy
import os


def deploy(graph, output_folder):
    for name, dep in graph.root.conanfile.dependencies.items():
        copy(graph.root.conanfile, "*", os.path.join(dep.folders.package_folder,"include"), os.path.join(output_folder, "include"))
