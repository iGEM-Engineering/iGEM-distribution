import scriptutils

root = scriptutils.distribution_dir()
packages = scriptutils.package_dirs()
scriptutils.build_distribution(root, packages)
