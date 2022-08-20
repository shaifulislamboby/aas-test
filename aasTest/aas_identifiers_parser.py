import re
from dataclasses import dataclass, field

import requests

import aasTest.helpers as helpers


@dataclass
class BaseParser:

    @property
    def raw_value(self):
        return getattr(self, f'raw_{helpers.convert_camel_case_to_snake_case(self.__class__.__name__)}')

    @property
    def mode_type(self):
        return self.raw_value.get('modelType').get('name')

    @property
    def id_type(self):
        return self.raw_value.get('identification').get('idType')

    @property
    def identification(self) -> dict:
        return self.raw_value.get('identification')

    @property
    def id_short_path(self):
        return helpers.create_url_encoded_from_id(self.raw_value.get('idShort'))

    @property
    def identifier(self):
        return helpers.convert_to_base64_form(self.raw_value.get('identification').get('id'))


@dataclass
class SubModel(BaseParser):
    raw_sub_model: dict

    @property
    def kind(self):
        return self.raw_sub_model.get('kind')

    @property
    def semantic_id(self):
        return self.raw_sub_model.get('semanticId')


@dataclass
class AssetAdministrationShell(BaseParser):
    raw_asset_administration_shell: dict
    sub_model_collection_uri: str
    sub_models: [SubModel] = field(default_factory=list)
    parsing_limit: int = 100

    @property
    def asset_information(self) -> dict:
        return self.raw_asset_administration_shell.get('assetInformation')

    @property
    def sub_models_raw_list(self) -> list:
        return self.raw_asset_administration_shell.get('submodels')

    @property
    def number_of_sub_models(self):
        return len(self.raw_asset_administration_shell.get('submodels'))

    @property
    def sub_model_ids(self) -> list:
        sub_model_ids = []
        for sub_model in self.sub_models_raw_list:
            sub_model_ids.append(helpers.convert_to_base64_form(sub_model.get('keys')[0].get('value')))
        return sub_model_ids

    @property
    def collect_all_sub_models(self) -> bool:
        if '{' not in self.sub_model_collection_uri:
            raise ValueError('Provided submodel collection path does not contains the path parameter for sub model id'
                             'without id we won`t be able to fetch particular sub model, so please provide a url'
                             'where we can get all the information for a particular submodel')

        for _ids in self.sub_model_ids:
            url = re.sub('{.*?}', _ids, self.sub_model_collection_uri)
            response = requests.get(url=url).json()
            sub_model = SubModel(raw_sub_model=response)
            self.sub_models.append(sub_model)
        return True


@dataclass
class ConceptDescription(BaseParser):
    raw_concept_description: dict

    @property
    def description(self):
        return self.raw_concept_description.get('description')


base_url = 'http://0.0.0.0:8080/'
res_aas = requests.get(f'{base_url}shells/').json()[0]
aas = AssetAdministrationShell(raw_asset_administration_shell=res_aas,
                               sub_model_collection_uri=f'{base_url}submodels/{{ssss}}')

aas