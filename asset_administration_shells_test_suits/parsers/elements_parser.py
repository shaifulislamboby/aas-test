import re
from dataclasses import dataclass
from typing import Union

import requests

from asset_administration_shells_test_suits.helpers import helpers


@dataclass
class BaseParser:
    """
    This is the base class for parsing required information for the tests.
    This will be extended and this only has the base functionality, but almost all
    the required functionality in this class.
    """
    password: Union[str, None]
    _id: Union[str, None]

    @property
    def session(self):
        """
        This method will generate a session object with provided auth, if they are provided
        This will help to test server where it is required to pass some auth parameter
        :return:
        """
        if self.password and self._id:
            session = requests.Session()
            session.auth = (self._id, self.password)
            return session
        return False

    @property
    def raw_value(self):
        """
        :return: it will collect the raw_value of specific class and save it as raw_value as general use case.
        """
        return getattr(self, f'raw_{helpers.convert_camel_case_to_snake_case(self.__class__.__name__)}')

    @property
    def mode_type(self):
        """
        :return: name of the model type
        """
        return self.raw_value.get('modelType').get('name')

    @property
    def id_type(self):
        """
        :return: This method will collect the id_type
        """
        return self.raw_value.get('identification').get('idType')

    @property
    def identification(self) -> dict:
        """
        This will collect the identification of the AAS or submodels or concept-description
        :return:
        """
        return self.raw_value.get('identification')

    @property
    def id_short_path(self):
        """
        This will collect the idShort of the AAS or submodels or concept-description
        :return:
        """
        return helpers.create_url_encoded_from_id(self.raw_value.get('idShort'))

    @property
    def identifier(self):
        """
        This method will collect the id and convert it to base64 format and save it,
        As for getting particular asset administration shell, submodels or concept-description we will need
        the base64 format of the id of that particular object
        :return:
        """
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
        """
        This property method will collect all the submodels that belongs to an AAS,
        By making request to the url that has been provided for the submodel
        collections.
        :return:
        """
        sub_models = []
        if '{' not in self.sub_model_collection_uri:
            raise ValueError('Provided submodel collection path does not contains the path parameter for sub model id'
                             'without id the test won`t be able to fetch particular sub model, so please provide a url'
                             'where the test can get all the information for a particular submodel')

        for _ids in self.sub_model_ids:
            url = re.sub('{.*?}', _ids, self.sub_model_collection_uri)
            """"This method will use try and except here in case submodels endpoint is not implemented, then the
            test shall run with the AAS only, it should not stop running for the endpoint not being available."""
            try:
                if self.session:
                    response = self.session.get(url=url).json()
                else:
                    response = requests.get(url=url).json()
                sub_model = SubModel(raw_sub_model=response, _id=None, password=None)
            except Exception as error:
                sub_model = {'error': error}
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
