"""Retrieves metadata for datasets at EDI for a given scope."""

import xml.etree.ElementTree as ET

import requests


SCOPE = 'knb-lter-ble'


def get_package_ids_for_scope(scope):
   """Returns a list of package IDs for a given scope.
   
   Args:
      scope (str): The scope of the package IDs to retrieve, e.g., knb-lter-ble
      
   Returns:
      list: A sorted list of package IDs for the given scope, e.g., ['1', '2', '3']
   """
   url = 'https://pasta.lternet.edu/package/eml/' + scope
   response = requests.get(url)
   if response.status_code == 200:
      response_text = response.text
      ids = [int(x) for x in response_text.split('\n')]
      return [str(x) for x in sorted(ids)]
   else:
      raise Exception('Error: ' + str(response.status_code))


def get_revisions_for_package(scope, package):
   """Returns a list of revisions for a given package.

   Args:
      scope (str): The scope of the package, e.g., knb-lter-ble
      package (str): The package ID, e.g., 1

   Returns:
      list: A sorted list of revisions for the given package, e.g., ['1', '2', '3']
   """
   package = str(package)
   url = 'https://pasta.lternet.edu/package/eml/' + scope + '/' + package
   response = requests.get(url)
   if response.status_code == 200:
      response_text = response.text
      revisions = [int(x) for x in response_text.split('\n')]
      return [str(x) for x in sorted(revisions)]
   else:
      raise Exception('Error: ' + str(response.status_code))


def get_doi_for_revision(scope, package, revision):
   """Returns the DOI for a given package revision.
   
   Args:
      scope (str): The scope of the package, e.g., knb-lter-ble
      package (str): The package ID, e.g., 1
      revision (str): The revision number, e.g., 1

   Returns:
      str: The DOI for the given package revision, e.g., 10.6073/pasta/abc123
   """
   package = str(package)
   revision = str(revision)
   url = 'https://pasta.lternet.edu/package/doi/eml/' + scope + '/' + package + '/' + revision
   response = requests.get(url)
   if response.status_code == 200:
      # The response text is in the form 'doi:10.6073/pasta/abc123', so trim off the 'doi:'.
      return response.text[4:]
   else:
      raise Exception('Error: ' + str(response.status_code))


def get_package_info(scope, package, revision):
   """Returns a dictionary of metadata for a given package revision.
   
   Args:
      scope (str): The scope of the package, e.g., knb-lter-ble
      package (str): The package ID, e.g., 1
      revision (str): The revision number, e.g., 1

   Returns:
      dict: A dictionary of metadata for the given package revision, e.g., 
      {'scope': 'knb-lter-ble',
       'package': '1',
       'revision': '7',
       'xml': xml_object_of_all_metadata,
       'title': 'My Title', 
       'pubDate': '2019-01-01', 
       'doi': '10.6073/pasta/abc123', 
       'creator': 'Smith'}
   """
   package = str(package)
   revision = str(revision)
   url = 'https://pasta.lternet.edu/package/metadata/eml/' + scope + '/' + package + '/' + revision
   response = requests.get(url)
   if response.status_code == 200:
      meta = {}
      tree = ET.fromstring(response.text)
      meta['scope'] = scope
      meta['package'] = package
      meta['revision'] = revision
      meta['xml'] = tree
      meta['title'] = tree.find('dataset/title').text
      meta['pubDate'] = tree.find('dataset/pubDate').text

      # Get the doi from the identifiers if the system is https://doi.org
      identifiers = tree.findall('dataset/alternateIdentifier')
      meta['doi'] = None
      for identifier in identifiers:
         if identifier.attrib['system'] == 'https://doi.org':
            # Check if the text is in the form 'doi:10.6073/pasta/abc123', and if so trim off the 'doi:'.
            if identifier.text[:4] == 'doi:':
               meta['doi'] = identifier.text[4:]
            else:
               meta['doi'] = identifier.text

      # Get the creator(s) of the dataset.
      creators = tree.findall('dataset/creator')
      creator_string = ''
      for creator in creators:
         # If there is a surName, use it. Otherwise, use organizationName.
         if creator.find('individualName/surName') is not None:
            creator_name = creator.find('individualName/surName').text
            creator_string += creator_name + ', '
         else:
            creator_name = creator.find('organizationName').text
            creator_string += creator_name + ', '
      meta['creator'] = creator_string[:-2]

      return meta

   else:
      raise Exception('Error: ' + str(response.status_code))


def get_meta_for_all_items_in_scope(scope):
   """Returns a dictionary of metadata for all packages in a given scope.

   Args:
      scope (str): The scope of the package, e.g., knb-lter-ble

   Returns:
      dict: A dictionary of metadata for all packages in the given scope, indexed by package, e.g.,
      {'1': [{'scope': 'knb-lter-ble', 'package': '1', 'revision': '7', 'xml': xml_metadata, ...}, {...}, ...],
       '2': [...]}
   """
   result = {}
   ids = get_package_ids_for_scope(scope)
   print('Found ' + str(len(ids)) + ' packages in scope ' + scope + '.')
   for id in ids:
      meta_list = []
      revisions = get_revisions_for_package(scope, id)
      for revision in revisions:
         print('Getting metadata for ' + scope + '.' + id + '.' + revision + '...')
         meta = get_package_info(scope, id, revision)
         meta_list.append(meta)
      result[id] = meta_list
   return result


if __name__ == '__main__':
   meta = get_meta_for_all_items_in_scope(SCOPE)