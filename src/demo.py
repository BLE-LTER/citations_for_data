"""Demonstrates how to report citations for datasets.

Outputs a CSV file with the following columns:
      scope: The scope of the datasets, e.g., knb-lter-ble
      package_id: The package ID, e.g., 1
      revision: The revision number, e.g., 1
      pubdate: The publication date of the dataset, e.g., 2021
      title: The title of the dataset, e.g., My dataset
      creators: The creators of the dataset, e.g., Smith, Wang
      doi: The DOI of the dataset, e.g., 10.6073/pasta/abc123
      citation: A citation for an item that cites or otherwise references the dataset, 
         e.g., Smith, Wang (2021). A paper about some data. doi:some_article_doi
"""

import csv

from citations_for_data import edi_client, datacite_client

# The scope of the datasets to report citations for
SCOPE = 'knb-lter-ble'
# The output CSV file
OUT_CSV = 'citations.csv'
# CSV columns
CSV_COLS = ['scope', 'package_id', 'revision', 'pubdate', 'title', 'creators', 'doi', 'citation']

rows = []  # The rows of the CSV file
rows.append(CSV_COLS)  # Add the column headers

# Get package metadata for all datasets in the scope. This can take a while,
# so you may want to comment out the call to get_meta_for_all_items_in_scope()
# and uncomment the next two lines to get metadata for a single dataset.
meta = edi_client.get_meta_for_all_items_in_scope(SCOPE)
# example_meta = edi_client.get_package_info(SCOPE, 9, 1)
# meta = {"9": [example_meta]}

for package_id in meta.keys():  # The keys are the package IDs
   for item in meta[package_id]:
      # Each item represents a revision of a dataset
      # Get the citations for this dataset
      print('Getting citations for ' + SCOPE + '.' + package_id + '.' + item['revision'] + '...')
      citations = datacite_client.get_citations_for_doi(item['doi'])
      for citation in citations:
         # For each citation, add a row to the CSV file
         row = [SCOPE, package_id, item['revision'], item['pubDate'], item['title'], item['creator'], item['doi'], citation['citation']]
         rows.append(row)

# Get citations for datasets that are not in EDI, but for which we have a DOI
# I would read these in from a table. But here's a simple example with only one item in the list.
datasets = [
   {'scope': 'knb-lter-ble', 
    'package_id': 'n/a', 
    'revision': 'n/a', 
    'pubDate': '2021', 
    'title': 'Some Model Data', 
    'creator': 'Rawlins, M.', 
    'doi': '10.6073/pasta/a49b3da18b4c83d6ff69d9d878bb7dc3'},
]

print('Getting citations for standalone DOIs...')
for d in datasets:
   print('   Getting citations for ' + d['doi'] + '...')
   citations = datacite_client.get_citations_for_doi(d['doi'])
   for citation in citations:
      # For each citation, add a row to the CSV file
      row = [d['scope'], d['package_id'], d['revision'], d['pubDate'], d['title'], d['creator'], d['doi'], citation['citation']]
      rows.append(row)

# Write the citations to a CSV file
with open(OUT_CSV, 'w', newline='') as csvfile:
   writer = csv.writer(csvfile)
   writer.writerows(rows)

print('Done. Wrote citations to ' + OUT_CSV + '.')
