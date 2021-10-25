import os

import sequences_to_features

fp_package = os.path.join(os.getcwd(), 'Fluorescent Reporter Proteins')

target_files = [os.path.join(fp_package, f) for f in os.listdir(fp_package)
			    if os.path.isfile(os.path.join(fp_package, f)) and f.endswith('.gb')]

output_files = [f.replace('.gb', '.curated.xml') for f in target_files]

args = ['-n', 'http://synbict.org']
args = args + ['-t'] + target_files
args = args + ['-o'] + output_files
args = args + ['-m', '0']
args = args + ['-M', '30']
args = args + ['-U', 'https://synbiohub.org']
args = args + ['-F', 'https://synbiohub.org/public/igem/cds_reporter/1']
args = args + ['-ni', '-cm', '-a']

sequences_to_features.main(args)