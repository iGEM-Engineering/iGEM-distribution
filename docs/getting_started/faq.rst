(In)Frequently Asked Questions
==============================

When working on an issue is it better to create a Branch then Merge changes into the Develop branch or is it better to create a Fork of the repository and then initiate a Pull Request?
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Either method is acceptable. 

In general, the Branch method is more suitable for contributors who are already familiar with the Git environment. The Fork method is more appropriate for those who have less Git experience.

How do I run the tests locally? 
-------------------------------

The tests can be run using Pytest. The script that GitHub actions uses for tests like this can be found `here <https://github.com/iGEM-Engineering/iGEM-distribution/blob/develop/.github/workflows/python-test.yml>`__

I want to update the designation of existing packages in .xslx, noting, for example, whether they are synthetic or not.  I can update the .xls file, but can’t figure out how to update the .csv files in views that the README uses to generate itself. How can the scripts be rerun ? 
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

The required steps are detailed in the “Scripts” README file: 

1. See what actions are being run automatically by GitHub to build the distribution each time a push is made `here <https://github.com/iGEM-Engineering/iGEM-distribution/blob/develop/.github/workflows/synchronize.yml>`__

2. In 'directories_and_excel', there is a section that executes run: ``python3 scripts/export_csvs.py``. Within the code for that script locate ``scriptutils.export_csvs(p)`` that function can be found in ``package_specification.py``.  This is the code that converts the .xlsx file into a .csv format that can be exported.

To run the entire process and build the distribution from the .xlsx files, run the python scripts in the scripts README sequentially. 
The output takes the form of locally-accessible .md summary files. 
It is necessary to follow all the steps specified.

Highlighted below are the specific steps within the process that are most directly relevant to the question:

1. It looks like the .mds are made in the job ``build_packages`` when the python script ``generate_markdown`` is run here.

2. This runs the script ``generate_package_summary`` in ``generate_markdown.py``

**tl;dr**:

1. Setup a python *venv* with requirements from ``requirements.txt``

2. Run the scripts in the order that they are there in the scripts ``README.md``

Note:  

- It is advisable to setup a Python virtual environment and install the requirements from ``requirements.txt``.

- The scripts run faster when run on a single directory.  To accomplish this, set up a testing script that can run the workflow.

- The process and related scripts can be run in a fork on GitHub provided the Actions are enabled

