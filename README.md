# citations_for_data

Code for getting data citations

Required Packages:

* requests

## Intro

The goal is to get a list of data citations for a given dataset, where each citation is a paper or some other work that cites or references the data.

For example code, see src/demo.py.  To support the use case of an LTER site archiving at EDI, the code first gets metadata for all data packages for an LTER site, then gets the citations for each data package. The citations are then written to a file.

This code uses APIs from PASTA to get DOIs and metadata for each data package, DataCite to find citations of the data, and Crossref to get metadata about the citations such as author and title.
