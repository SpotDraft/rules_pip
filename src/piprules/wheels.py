import contextlib
import glob
import os
import pkg_resources

from pip._internal import main as pip_main
from wheel import wheelfile

from piprules import util
from piprules import namespace_pkgs


class Error(Exception):

    """Base exception for the wheels module"""


def download(dest_directory, requirements_file_path, *extra_args):
    with _add_pip_import_paths_to_pythonpath():
        pip_main(
            args=[
                "wheel",
                "-w", dest_directory,
                "-r", requirements_file_path,
            ] + list(extra_args)
        )


@contextlib.contextmanager
def _add_pip_import_paths_to_pythonpath():
    import pip
    import setuptools
    import wheel

    import_paths = [util.get_import_path_of_module(m) for m in [pip, setuptools, wheel]]
    with util.prepend_to_pythonpath(import_paths):
        yield


def find_all(directory):
    for matching_path in glob.glob("{}/*.whl".format(directory)):
        yield matching_path

def setup_namespace_pkg_compatibility(extracted_whl_directory):
    """
    Namespace packages can be created in one of three ways. They are detailed here:
    https://packaging.python.org/guides/packaging-namespace-packages/#creating-a-namespace-package
    'pkgutil-style namespace packages' (2) works in Bazel, but 'native namespace packages' (1) and
    'pkg_resources-style namespace packages' (3) do not.
    We ensure compatibility with Bazel of methods 1 and 3 by converting them into method 2.
    """
    namespace_pkg_dirs = namespace_pkgs.pkg_resources_style_namespace_packages(
        extracted_whl_directory
    )
    if not namespace_pkg_dirs and namespace_pkgs.native_namespace_packages_supported():
        namespace_pkg_dirs = namespace_pkgs.implicit_namespace_packages(
            extracted_whl_directory,
            ignored_dirnames=[f"{extracted_whl_directory}/bin",],
        )

    for ns_pkg_dir in namespace_pkg_dirs:
        try:
            namespace_pkgs.add_pkgutil_style_namespace_pkg_init(ns_pkg_dir)
        except ValueError as e:
            pass


def unpack(wheel_path, dest_directory):
    # TODO(): don't use unsupported wheel library
    with wheelfile.WheelFile(wheel_path) as wheel_file:
        distribution_name = wheel_file.parsed_filename.group("name")
        library_name = util.normalize_distribution_name(distribution_name)
        package_directory = os.path.join(dest_directory, library_name)
        wheel_file.extractall(package_directory)
        setup_namespace_pkg_compatibility(package_directory)

    try:
        return next(pkg_resources.find_distributions(package_directory))
    except StopIteration:
        raise DistributionNotFoundError(package_directory)


class DistributionNotFoundError(Error):
    def __init__(self, package_directory):
        super(DistributionNotFoundError, self).__init__()
        self.package_directory = package_directory

    def __str__(self):
        return "Could not find in Python distribution in directory {}".format(
            self.package_directory
        )
