import tempfile
import os
from shutil import copy

from scripts.scriptutils import EXPORT_DIRECTORY


def copy_to_tmp(package: list[str] = None, exports: list[str] = None, renames: dict[str, str] = None) -> str:
    """Copy test files into a temporary package directory

    :param package: list of files to go into the package directory
    :param exports: list of files to go into the exports subdirectory
    :param renames: dictionary of copy/renaming, mapping local path to local path
    :return: temporary package directory
    """
    # make a temporary package directory and export directory
    if exports is None:
        exports = []
    if package is None:
        package = []
    if renames is None:
        renames = {}
    tmp_dir = tempfile.mkdtemp()
    tmp_sub = os.path.join(tmp_dir, 'test_package')
    tmp_export = os.path.join(tmp_sub, EXPORT_DIRECTORY)
    os.mkdir(tmp_sub)
    os.mkdir(tmp_export)
    # copy all of the relevant files
    test_dir = os.path.dirname(os.path.realpath(__file__))
    for f in package:
        copy(os.path.join(test_dir, 'test_files', f), tmp_sub)
    for f in exports:
        copy(os.path.join(test_dir, 'test_files', EXPORT_DIRECTORY, f), tmp_export)
    for old_f, new_f in renames.items():
        copy(os.path.join(test_dir, 'test_files', old_f), os.path.join(tmp_sub, new_f))
    return tmp_sub
