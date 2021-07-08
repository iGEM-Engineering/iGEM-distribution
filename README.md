# iGEM Distribution Design

This repository is for collective design of an iGEM DNA distribution. The processes used in this repository are intended to support:

- Design, review, and discussion by many contributors
- Keeping stable records of decisions
- Checking for errors and issues

## Organization: Packages & Views

Each directory contains one "package" of parts, where a "package" is a coherent collection of basic or composite parts and devices. 
Packages should be large enough to contain a full "tool kit", but small enough to be readily understood, reviewed, and discussed.
Some examples of reasonable packages:

- a collection of small molecule sensors
- a system of recombinases and recombinase targets, plus some ready-to-use recombinase-based devices made with them
- A collection of terminators
- A set of transcriptional insulators and insulated parts and devices

It's OK for a part to appear in multiple packages. Multiple usages will be detected and only one copy will appear in the actual distribution.

### Package Directories

The directory for a package should contain the following:

1. A package spreadsheet, following the format of `package template.xlsx`. This is the central file of the package and defines all of its contents. The format must not be altered, or else it cannot be processed correctly.
2. Files defining basic parts in SBOL3, SBOL2, GenBank, or FASTA format. These are optional and can referred to by the package spreadsheet.  Any given part must appear in only one of such files.
3. A `views` subdirectory, which contains exported versions of package data. These files should not be edited by hand. Views to expect are:
  - CSV exports from the package spreadsheet, to simplify review of differences in pull requests.
  - A compilation of all parts and libraries in the package encoded in SBOL.
  - GenBank and FASTA versions of the package. These are lossy "flat" exports, since these formats can capture only individual sequence design, not part relationships or package and library structure.


## Using the Package Spreadsheet

The package spreadsheet allows a large collection of related parts to be specified compactly.

The `Basic Parts` tab is where to make a list of all of the designs that are to be used, along with notes about them as needed.

Sequence information can be specified in three ways:
 - Reference to the iGEM repository
 - Reference to an ID in one of the directory files
 - Direct specification in the sheet

The `Libraries and Composite Parts` tab 

Do not modify the other tabs; they are used for configuring spreadsheet's automation.

### Automation to implement:

Automatic import of basic parts from directory files and iGEM repo

## Editing and Review

explain the gitflow process

- main branch vs. develop
- release tags
- development on branches and forks
- pull requests

## Referring to Packages and Parts

HEAD:

- repository / package / part
- repository / package / collection

Explain branch, release, commit:

- repository / {branch, release, commit} / package / part


