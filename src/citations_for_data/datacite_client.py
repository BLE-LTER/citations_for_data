"""Retrieve citations from DataCite REST API."""

import requests
import json

try:
   import citations_for_data.crossref_client as crossref_client
except:
   import crossref_client


def clean_identifier(identifier):
   identifier = identifier.strip()
   if 'https://doi.org/' in identifier:
      identifier = identifier.replace('https://doi.org/', '')
   if identifier[:4] == 'doi:':
      identifier = identifier[4:]
   return identifier


def add_citations_from_relationships(relationships_child, citation_type, citations_list):
   if 'data' in relationships_child:
      for item in relationships_child['data']:
         if 'id' in item:
            # Make sure we don't already have this citation by checking the identifier
            found = False
            identifier = clean_identifier(item['id'])
            for citation in citations_list:
               if citation['identifier'] == identifier:
                  found = True
                  break
            if found:
               continue

            citation = {}
            citation['identifier'] = identifier
            if 'type' in item:
               if item['type'] == 'dois':
                  citation['identifier_type'] = 'DOI'
               else:
                  citation['identifier_type'] = item['type']
            else:
               citation['identifier_type'] = 'Unknown'
            citation['type'] = citation_type
            citations_list.append(citation)


def get_citations_for_doi(doi):
   """Returns a list of citations for a given DOI.

   Args:
      doi (str): The DOI to retrieve citations for, e.g., 10.6073/pasta/abc123

   Returns:
      list: A list of citations represented as a dictionary for the given DOI, e.g., 
      [{'identifier': '10.123/abc', 'identifier_type': 'DOI', 'citation': 'citation text', 'type': 'IsCitedBy'}, ...]
   """
   citations = []  # list of citations, where each citation is a dictionary
   url = 'https://api.datacite.org/dois/' + doi
   response = requests.get(url)
   if response.status_code == 200:
      response_json = json.loads(response.text)
      citations = []
      if 'data' in response_json:
         # Get citations from relatedIdentifiers
         if 'attributes' in response_json['data']:
            if 'relatedIdentifiers' in response_json['data']['attributes']:
               for item in response_json['data']['attributes']['relatedIdentifiers']:
                  if 'relatedIdentifier' in item:
                     citation = {}
                     citation['identifier'] = clean_identifier(item['relatedIdentifier'])
                     if 'relationType' in item:
                        citation['type'] = item['relationType']
                     else:
                        citation['type'] = 'Unknown'
                     if 'relatedIdentifierType' in item:
                        citation['identifier_type'] = item['relatedIdentifierType']
                     else:
                        citation['identifier_type'] = 'Unknown'
                     citations.append(citation)

         # Get citations from references and citations within relationships
         if 'relationships' in response_json['data']:
            if 'references' in response_json['data']['relationships']:
               add_citations_from_relationships(response_json['data']['relationships']['references'], 'References', citations)
            if 'citations' in response_json['data']['relationships']:
               add_citations_from_relationships(response_json['data']['relationships']['citations'], 'Citations', citations)

      # For each citation, get the author, title, and year to build citation text
      for citation in citations:
         if citation['identifier_type'] == 'DOI':
            try:
               crossref_citation = crossref_client.get_citation_for_doi(citation['identifier'])
               citation['citation'] = crossref_citation['citation']
            except Exception as e:
               print(e)
               citation['citation'] = ''
         else:
            citation['citation'] = ''
      return citations
   else:
      raise Exception('Error: ' + str(response.status_code))


if __name__ == '__main__':
   #citations = get_citations_for_doi('10.6073/pasta/e0e71c2d59bf7b08928061f546be6a9a') # ble.3.1
   citations = get_citations_for_doi('10.6073/pasta/bb7d76017b8a8534c4960346705bcb77') # ble.5.2
   for citation in citations:
      print(citation)
