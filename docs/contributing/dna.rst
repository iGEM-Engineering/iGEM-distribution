Contributing packages and DNA parts to the distribution
=========================================

Package structure
-----------------

A package containing DNA parts exists as a subdirectory in the iGEM Distrubution directory.

Package spreadsheet structure
-----------------------------

To document the package spreadsheet structure, and maybe discuss and refer to displayids and stuff for the two basic sheets, basic and composite parts/libraries
Also explain columns and highlight *ideal* minimal requirements for part documentation in the several columns (e.g. part design, etc.)
Also explain databases and literal TRUE or FALSE for people to understand when to look for DNA seqs or draw them from dbs

Adding a new package directory
--------------------------

Recommended use: Github Desktop or Github.dev -> Link to existing documentation for this

1. Collect all desired parts in SBOL (if possible, but difficult to exist already), Genbank (preferable to FASTA, allows annotations) or FASTA -- also check for TypeIIS compatibility or find them in supported databases
2. use lastest spreadsheet template from here (DNA distro link for excel_template.xlsx) --> name it according to package name for clarity
3. Add part information in the basic part sheet, add flanking seqs, sourceIDs and thelike
4. Fill the composite/libraries sheet, to specify the final circular plasmids for synthesis
5. Create a directory with desired package name, that contains the package spreadsheet and all downloaded DNA files (SBOL, Genbank or FASTA). Make sure there are no subdirectories
6. Review spreadsheet and DNA files. FASTA name to Part Name, GenBank LOCUS name to part name etc.
7. Move the package directory in the iGEM distribution directory
8. Commit and push changes to remote, let the gitflow buil the new package along with everything else. 
9. Fetch locally if needed for everything to proceed smoothly
10. Once build is complete, ensure package structure is correct, according to (igem distro readme link)

Add DNA parts to an existing package directory
----------------------------------------------


