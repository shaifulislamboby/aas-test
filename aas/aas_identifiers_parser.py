import re
from dataclasses import dataclass
from typing import Union

import requests

import helpers as helpers


@dataclass
class BaseParser:
    password: Union[str, None]
    _id: Union[str, None]

    @property
    def session(self):
        if self.password and self._id:
            session = requests.Session()
            session.auth = (self._id, self.password)
            return session
        return False

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

    @property
    def has_sub_model_elements(self):
        if 'submodelElements' in self.raw_sub_model:
            return True
        return False

    @property
    def id_short_path_sub_model_elements(self):
        if 'submodelElements' in self.raw_sub_model:
            return helpers.create_url_encoded_from_id(self.raw_sub_model.get('submodelElements')[0].get('idShort'))
        return 'not available'


@dataclass
class AssetAdministrationShell(BaseParser):
    raw_asset_administration_shell: dict
    sub_model_collection_uri: str
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
    def sub_models(self):
        sub_models = []
        if '{' not in self.sub_model_collection_uri:
            raise ValueError('Provided submodel collection path does not contains the path parameter for sub model id'
                             'without id we won`t be able to fetch particular sub model, so please provide a url'
                             'where we can get all the information for a particular submodel')

        for _ids in self.sub_model_ids:
            url = re.sub('{.*?}', _ids, self.sub_model_collection_uri)
            if self.session:
                response = self.session.get(url=url).json()
            else:
                response = requests.get(url=url).json()
            sub_model = SubModel(raw_sub_model=response, _id=None, password=None)
            sub_models.append(sub_model)

        return sub_models


@dataclass
class ConceptDescription(BaseParser):
    raw_concept_description: dict

    @property
    def description(self):
        return self.raw_concept_description.get('description')


@dataclass
class Packages(BaseParser):
    raw_packages: dict
