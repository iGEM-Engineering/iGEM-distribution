import scriptutils

# find the root and packages
root = scriptutils.distribution_dir()
packages = scriptutils.package_dirs()

# build the distribution
doc = scriptutils.build_distribution(root, packages)

# make the summary Markdown
scriptutils.generate_distribution_summary(root, doc)

# export materials in GenBank and FASTA for independent inspection and synthesis
