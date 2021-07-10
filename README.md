# iGEM Distribution Design

This repository is for collective design of an iGEM DNA distribution. The processes used in this repository are intended to support:

- Design, review, and discussion by many contributors
- Keeping stable records of decisions
- Checking for errors and issues

**Table of Contents**

- [Organization: Packages & Views](#organization)  
    - [Package Directories](#directories)
- [Using the Package Spreadsheet](#spreadsheet)
- [Editing and Review](#editing)

## Organization: Packages & Views<a name="organization"></a>

Each directory contains one "package" of parts, where a "package" is a coherent collection of basic or composite parts and devices. 
Packages should be large enough to contain a full "tool kit", but small enough to be readily understood, reviewed, and discussed.
Some examples of reasonable packages:

- a collection of small molecule sensors
- a system of recombinases and recombinase targets, plus some ready-to-use recombinase-based devices made with them
- A collection of terminators
- A set of transcriptional insulators and insulated parts and devices

It's OK for a part to appear in multiple packages. Multiple usages will be detected and only one copy will appear in the actual distribution.

### Package Directories<a name="directories"></a>

The directory for a package should contain the following:

1. A package spreadsheet, following the format of `package template.xlsx`. This is the central file of the package and defines all of its contents. The format must not be altered, or else it cannot be processed correctly.
2. Files defining basic parts in SBOL3, SBOL2, GenBank, or FASTA format. These are optional and can be referred to by the package spreadsheet.  Any given part must appear in only one of such files.
3. A `views` subdirectory, which contains exported versions of package data. These files should not be edited by hand. Views to expect are:
    - CSV exports from the package spreadsheet, to simplify review of differences in pull requests.
    - A compilation of all parts and libraries in the package encoded in SBOL. _Not yet automated._
    - GenBank and FASTA versions of the package. These are lossy "flat" exports, since these formats can capture only individual sequence design, not part relationships or package and library structure. _Not yet automated._

Package directories should not have any other subdirectories.

## Using the Package Spreadsheet<a name="spreadsheet"></a>

The package spreadsheet allows a collection of related parts to be specified compactly.

The `Basic Parts` tab list of all the parts that are to be used, along with notes about them as needed.

Sequence information can be specified in three ways:
 - Reference to the iGEM repository
 - Reference to an ID in one of the directory files
 - Direct listing in the sheet

The `Libraries and Composite Parts` tab is where parts can be grouped together into sub-collections and where the backbones they should be inserted into can be specified.

Do not modify the other tabs; they are used for configuring spreadsheet's automation.

## Editing and Review<a name="editing"></a>

To organize collective editing and review, this repository uses the [GitFlow workflow](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow). The key points for contributors to know are:

- The `main` branch is only for releases, and the `develop` branch only for approved and validated pre-release material. `main` should have very few commits, mostly just release tags.
- All proposed changes should be made on new branches off of `develop`. 
- In order to incorporate a proposed change, make a pull request from the change branch into `develop` and request review from other contributors.
    - Automated validation checks make sure your contribution is well-organized. **Do not merge any pull that is failing validation!**
    - GitHub doesn't visualize Excel diffs well, so a GitHub action creates CSV exports to allow the change to be more easily reviewed and discussed.

_Example: You see some missing constructs in a sensors package and want to add them. First, you make a new `add-missing-sensors` branch off of `develop`. You edit the package Excel file to add the sensors, commit, and push.  GitHub automatically creates CSV exports in the `views` directory for the package.  Satisfied with what you see, you create a pull request and ask a colleague to review and merge._

