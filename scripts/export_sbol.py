import os
import scriptutils

if __name__ == '__main__':
    packages = scriptutils.package_dirs()
    for p in packages:
        print(f'Exporting SBOL from Excel for package {os.path.basename(p)}')
        try:
            doc = scriptutils.export_sbol(p)
            print(f'  {len(doc.objects)} designs and collections exported')
        except (OSError,ValueError) as e:
            print(f'Could not export SBOL file for package {os.path.basename(p)}: {e}')
