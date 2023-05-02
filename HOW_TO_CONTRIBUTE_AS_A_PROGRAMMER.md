# How to contribute as a programmer

Every year teams participating in the main iGEM competition receive the Distribution Kit, a open and global curation of what the synbio community believes is the most important parts to share with all the iGEM Teams. This repository is where all the information to create the DNA samples that will be part of the iGEM distribution are organized.

As seen previously, packages are where the information is organized in a human-readable format (spreadsheet file). This information is processed by software for a main objective: build a FASTA file that will be delivered to a DNA synthesis company, so they could create the DNA samples that will be distributed by the Distribution Kit. This process occurs everytime a new change is made to the `main` branch of the repository, a widely-adopted practice in software development called continuous integration. Just like in software development contexts, continuous integration can been used for more than only build the 'source code'. We envision a group of processes that could generate documentation, check for errors, analyze retrocompatibility, warning problematic sequences and any automatic process that could make the distribution flow more easy.

## Workflow and scripts
As you could see the Distribution Kit is stored inside Github, and thanks to that Github allow projects to have their run their own continuous integration pipeline runned for free by the company servers. You could see all the pipelines runned so far by checking the `Actions` tab in the top toolbar of the repository. You could also take a look inside `.github/workflow` folder and see the pipeline process from top to bottom and see what scripts are being called.

Talking about it, the `scripts` folder is where all the software that composes the continous integration is located. So if you're trying to solve your `First good issue` or if you're creating a new feature, that will be probably the place. You could understand more about each script by taking a look in the documentation, or by reading the comments inside each script or by taking a look in the unit tests created to a specfic script.

## Your first issue

We know: open source contribution is difficult. Instead of feeling overwhelming by the ammount of know-how, I really encourage you to take a look in the `Issues` tab and see if you could find a issue with the `First good issue` tag associated. This probably you give you a leverage to start working and understanding the system. As first steps we believe the first steps towards this process could be:

- Clone the repository
- Install dependencies
- Run test locally
- Try it out our tutorial

If you find any problem during this first steps or during the solution of you issue, let us know and we will be glad to help you.

## Communication

Talking about helping you, you could find us in the slack channel. Feel free to ask any questions you want. We also have a weekly meeting every Monday, here is the invite for.
