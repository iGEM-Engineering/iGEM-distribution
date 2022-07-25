import os
import sys
import git

import scriptutils

# find the repository for automatic git actions, if possible
try:
    repo = git.Repo('.', search_parent_directories=True)
except git.InvalidGitRepositoryError:
    repo = None

error = False
packages = scriptutils.package_dirs()
for p in packages:

    print(f'Converting SBOL2 to SBOL3 files for package {os.path.basename(p)}')
    try:
        # convert files
        mappings = scriptutils.convert_package_sbol2_files(p)
        # if there's a git repo, try to remove the old files
        if repo and len(mappings):
            repo.index.add(mappings.keys())     # add, in case they weren't there before
            repo.index.remove(mappings.keys(), working_tree=True, f=True)  # then remove

    except (OSError, ValueError) as e:
        print(f'Could not convert SBOL2 files for package {os.path.basename(p)}: {e}')
        error = True

# If there was an error, flag on exit in order to notify executing YAML script
if error:
    sys.exit(1)
