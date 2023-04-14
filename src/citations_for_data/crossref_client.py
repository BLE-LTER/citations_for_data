import requests


def get_citation_for_doi(doi):
   url = f'https://api.crossref.org/works/{doi}'
   response = requests.get(url)

   citation = {}  # {doi: '', title: '', authors: '', year: '', 'citation': ''}
   if response.status_code == 200:
      data = response.json()['message']
      citation['doi'] = doi

      # The author names are in the 'family' field if present, otherwise use the 'name' field
      authors = []
      for author in data['author']:
         if 'family' in author:
            authors.append(author['family'])
         elif 'name' in author:
            authors.append(author['name'])
         else:
            raise Exception('Error: author name not found')

      citation['authors'] = ', '.join(authors)
      citation['title'] = data['title'][0]
      citation['year'] = data['created']['date-parts'][0][0]
      citation['citation'] = f'{citation["authors"]} ({citation["year"]}). {citation["title"]}. doi:{citation["doi"]}'
   else:
      raise Exception(f'Error: {response.status_code} {response.reason}')
   return citation


if __name__ == '__main__':
   citation = get_citation_for_doi('10.5670/oceanog.2022.119')
   print(citation)