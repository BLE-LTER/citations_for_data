def clean_identifier(identifier):
   identifier = identifier.strip()
   if 'https://doi.org/' in identifier:
      identifier = identifier.replace('https://doi.org/', '')
   if identifier[:4] == 'doi:':
      identifier = identifier[4:]
   return identifier
