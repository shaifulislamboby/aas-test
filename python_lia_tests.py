import requests
import json

base_url = "http://192.168.0.2:60008"
session = requests.session()
session.auth = ('OVGUAdmin', 'liaadmin')

shells_response = session.get(f'{base_url}/shells')
print(shells_response.json())
with open('responses/Lia responses/shells.json', 'w') as f:
    json.dump(shells_response.json(), f)

shells_delete = session.delete(f'{base_url}/shells/aHR0cHM6Ly9leGFtcGxlLmNvbS9pZHMvYWFzLzMzODNfODAxMl8yMTEyXzczNjQ=')
print(shells_delete.json())
with open('responses/Lia responses/shell_delete.json', 'w') as f:
    json.dump(shells_delete.json(), f)

submodels_response = session.get(f'{base_url}/submodels')

with open('responses/Lia responses/submodels.json', 'w') as f:
    json.dump(submodels_response.json(), f)

submodel_delete_response = session.delete(f'{base_url}/submodels/aHR0cHM6Ly9leGFtcGxlLmNvbS9pZHMvc20vNzI4MF85MDMwXzExMTJfNTc1OQ==')

with open('responses/Lia responses/specific_submodel_delete.json', 'w') as f:
    json.dump(submodels_response.json(), f)


concept_description_response = session.get(f'{base_url}/concept-descriptions').json()

with open('responses/Lia responses/submodels.json', 'w') as f:
    json.dump(concept_description_response, f)

response_specific_submodel = session.get(f'{base_url}/submodels/aHR0cHM6Ly9leGFtcGxlLmNvbS9pZHMvc20vNzI4MF85MDMwXzExMTJfNTc1OQ==')

with open('responses/Lia responses/submodels_one_specific.json', 'w') as f:
    json.dump(response_specific_submodel.json(), f)

delete_response_for_concept_description = session.delete(f'{base_url}/concept-descriptions/aHR0cHM6Ly9hZG1pbi1zaGVsbC5pby9zYW5kYm94L1NHMi9UZWNobmljYWxEYXRhL1N1YlNlY3Rpb24vMS8x')
with open('responses/Lia responses/concept-description_delete.json', 'w') as f:
    json.dump(delete_response_for_concept_description.json(), f)
