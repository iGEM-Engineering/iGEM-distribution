import scriptutils

# find the root and packages
root = scriptutils.distribution_dir()
scriptutils.check_synthesizability(root)
