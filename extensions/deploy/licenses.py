from conan.tools.files import copy
import os


def deploy(graph, output_folder):
    for name, dep in graph.root.conanfile.dependencies.items():
        src_folder = os.path.join(dep.folders.package_folder,"licenses")
        dst_folder = os.path.join(output_folder, "licenses", name.ref.name, str(name.ref.version))
        copy(graph.root.conanfile, "*", src_folder , dst_folder )