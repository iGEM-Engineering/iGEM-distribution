import tempfile
import sbol2
import sbol3
import scriptutils

import sequences_to_features

from os import listdir
from os.path import isfile,join

fp_package = None

for package in scriptutils.package_dirs():
	if 'Fluorescent Reporter Proteins' in package:
		fp_package = package

target_files = [join(fp_package, f) for f in listdir(fp_package)
			    if isfile(join(fp_package, f)) and f.endswith('.gb')]

output_files = [f.replace('.gb', '.curated.xml') for f in target_files]

args = ['-n', 'http://synbict.org']
args = args + ['-t'] + target_files
args = args + ['-o'] + output_files
args = args + ['-m', '0']
args = args + ['-M', '30']
args = args + ['-U', 'https://synbiohub.org']
# args = args + ['-f', 'fp_library.xml']
args = args + ['-F', 'https://synbiohub.org/public/igem/cds_reporter/1']
args = args + ['-ni', '-cm', '-a']

sequences_to_features.main(args)