"""
Copyright (c) 2021-2022 OVGU LIA
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
"""
import json
import logging
import os
import requests
import threading
from requests.utils import quote
from flask import render_template, Response, redirect, session, Flask
from flask_restful import Api, Resource, request
from flask_login import LoginManager, UserMixin
import flask_login

try:
    from utils.i40data import Generic
except ImportError:
    from main.utils.i40data import Generic
try:
    from utils.utils import HTTPResponse
except ImportError:
    from main.utils.utils import HTTPResponse

try:
    from abstract.endpointhandler import AASEndPointHandler
except ImportError:
    from main.abstract.endpointhandler import AASEndPointHandler

try:
    from aasendpointhandlers.rstapi_endpointresources import AssetAdministrationShells, AssetAdministrationShell, \
        ConceptDescriptions, ConceptDescription, Submodels, Submodel, AssetAdministrationShellsSubmodelRefs, \
        SubmodelELements, SubmodelElementByIdShortPath, AASStaticSource, AASStaticWebSources, AASRTDataVisualizer, \
        AASWebInterfaceConversationMessage
except ImportError:
    from main.aasendpointhandlers.rstapi_endpointresources import AssetAdministrationShells, AssetAdministrationShell, \
        ConceptDescriptions, ConceptDescription, Submodels, Submodel, AssetAdministrationShellsSubmodelRefs, \
        SubmodelELements, SubmodelElementByIdShortPath, AASStaticSource, AASStaticWebSources, AASRTDataVisualizer, \
        AASWebInterfaceConversationMessage

try:
    from aasendpointhandlers.rstapi_endpointresources import RetrieveMessage, AASWebInterfaceHome, AASWebInterface, \
        AASWebInterfaceStandardSubmodel, AASWebInterfaceSearch, AASWebInterfaceSubmodels, \
        AASWebInterfaceSubmodelElemValue, AASWebInterfaceSkill, AASWebInterfaceSKillLog, \
        AASWebInterfaceProductionManagement, AASDocumentationDownload, AASDocumentationDownload, \
        AASDocumentationDownloadSubmodel
except ImportError:
    from main.aasendpointhandlers.rstapi_endpointresources import RetrieveMessage, AASWebInterfaceHome, AASWebInterface, \
        AASWebInterfaceStandardSubmodel, AASWebInterfaceSearch, AASWebInterfaceSubmodels, \
        AASWebInterfaceSubmodelElemValue, AASWebInterfaceSkill, AASWebInterfaceSKillLog, \
        AASWebInterfaceProductionManagement, AASDocumentationDownload, AASDocumentationDownload, \
        AASDocumentationDownloadSubmodel

drv_rst_app = Flask(__name__)
drv_rst_app.secret_key = os.urandom(24)
drv_rst_app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
drv_rst_api = Api(drv_rst_app)
drv_rst_app.logger.disabled = True
log = logging.getLogger('Python AAS Rest API')
log.setLevel(logging.ERROR)
log.disabled = True
login_manager = LoginManager()
login_manager.init_app(drv_rst_app)


class User(UserMixin):
    pass


users = {'OVGUAdmin': {'password': 'liaadmin'}}


@login_manager.user_loader
def user_loader(_id):
    if _id not in users:
        return

    user = User()
    user._id = _id
    return user


@login_manager.request_loader
def request_loader(request):
    _id = request.form.get('email')
    if _id not in users:
        return
    user = User()
    user.id = _id
    user.is_authenticated = request.form['password'] == users[_id]['password']
    return user


class Logout(Resource):
    def __init__(self, pyAAS):
        self.pyAAS = pyAAS

    def get(self):
        session['logged_in'] = False
        return redirect("login")


class Login(Resource):
    def __init__(self, pyAAS):
        self.pyAAS = pyAAS

    def get(self):
        if session.get('logged_in'):
            return redirect("/home")
        else:
            try:
                return Response(render_template('login.html', exDomain=self.pyAAS.exDomain))
            except Exception as E:
                return str(E)

    def post(self):
        try:
            loginInfo = request.form
            _id = loginInfo["user"]
            password = loginInfo["password"]

            if password == users[_id]['password']:
                user = User()
                user.id = user
                flask_login.login_user(user)
                session['logged_in'] = True
                return redirect("home")
            else:
                return redirect("login")
        except Exception as E:
            return str(E)


@drv_rst_app.errorhandler(404)
def page_not_found(e):
    return redirect("login")


class AASEndPointHandler(AASEndPointHandler):

    def __init__(self, pyAAS, msgHandler):
        self.pyAAS = pyAAS

        self.msgHandler = msgHandler
        self.registryURL = self.pyAAS.lia_env_variable["LIA_REGISTRYENDPOINT"]
        self.transportHeader = {"content-type": "application/json"}

    def configure(self):

        self.ipaddressComdrv = '0.0.0.0'
        self.portComdrv = self.pyAAS.lia_env_variable["LIA_AAS_RESTAPI_PORT_INTERN"]

        # REST API
        drv_rst_api.add_resource(AssetAdministrationShells, "/shells", resource_class_args=tuple([self.pyAAS]))
        drv_rst_api.add_resource(ConceptDescriptions, "/concept-descriptions", resource_class_args=tuple([self.pyAAS]))
        drv_rst_api.add_resource(Submodels, "/submodels", resource_class_args=tuple([self.pyAAS]))

        drv_rst_api.add_resource(AssetAdministrationShell, "/shells/<path:aasIdentifier>",
                                 resource_class_args=tuple([self.pyAAS]))
        drv_rst_api.add_resource(ConceptDescription, "/concept-descriptions/<path:cdIdentifier>",
                                 resource_class_args=tuple([self.pyAAS]))
        drv_rst_api.add_resource(Submodel, "/submodels/<path:submodelIdentifier>/submodel",
                                 resource_class_args=tuple([self.pyAAS]))
        drv_rst_api.add_resource(SubmodelElementByIdShortPath,
                                 "/submodels/<path:submodelIdentifier>/submodel/submodel-elements/<path:idShortPath>",
                                 resource_class_args=tuple([self.pyAAS]))

        drv_rst_api.add_resource(AssetAdministrationShellsSubmodelRefs, "/shells/<path:aasIdentifier>/aas/submodels",
                                 resource_class_args=tuple([self.pyAAS]))
        drv_rst_api.add_resource(SubmodelELements, "/submodels/<path:submodelIdentifier>/submodel/submodel-elements",
                                 resource_class_args=tuple([self.pyAAS]))

        # drv_rst_api.add_resource(AAS, "/shells/<path:aasIdentifier>/aas", resource_class_args=tuple([self.pyAAS]))
        '''
        drv_rst_api.add_resource(AASAssetInformationRefs, "/shells/<path:aasIdentifier>/aas/asset-information", resource_class_args=tuple([self.pyAAS]))
        drv_rst_api.add_resource(AASassetInformation, "/assetInformation", resource_class_args=tuple([self.pyAAS]))
        drv_rst_api.add_resource(AASassetInformationById, "/assetInformation/<path:assetId>", resource_class_args=tuple([self.pyAAS]))
'''
        # HTTP Communication
        drv_rst_api.add_resource(RetrieveMessage, "/i40commu", resource_class_args=tuple([self.pyAAS]))
        # Web API
        drv_rst_api.add_resource(Login, "/login", resource_class_args=tuple([self.pyAAS]))
        drv_rst_api.add_resource(Logout, "/logout", resource_class_args=tuple([self.pyAAS]))

        drv_rst_api.add_resource(AASWebInterfaceHome, "/home", resource_class_args=tuple([self.pyAAS]))
        drv_rst_api.add_resource(AASWebInterface, "/<int:aasIndex>/home", resource_class_args=tuple([self.pyAAS]))
        drv_rst_api.add_resource(AASWebInterfaceStandardSubmodel, "/<int:aasIndex>/<string:stdsubmodelType>",
                                 resource_class_args=tuple([self.pyAAS]))
        drv_rst_api.add_resource(AASWebInterfaceSubmodels, "/<int:aasIndex>/submodels",
                                 resource_class_args=tuple([self.pyAAS]))
        drv_rst_api.add_resource(AASWebInterfaceSKillLog, "/<int:aasIndex>/log/<path:skillName>",
                                 resource_class_args=tuple([self.pyAAS]))
        drv_rst_api.add_resource(AASWebInterfaceProductionManagement, "/<int:aasIndex>/productionmanager",
                                 resource_class_args=tuple([self.pyAAS]))

        drv_rst_api.add_resource(AASWebInterfaceSkill, "/<int:aasIndex>/<string:skillName>",
                                 resource_class_args=tuple([self.pyAAS]))

        drv_rst_api.add_resource(AASWebInterfaceSearch, "/<int:aasIndex>/search",
                                 resource_class_args=tuple([self.pyAAS]))
        drv_rst_api.add_resource(AASWebInterfaceConversationMessage, "/<int:aasIndex>/search/<query>",
                                 resource_class_args=tuple([self.pyAAS]))

        drv_rst_api.add_resource(AASWebInterfaceSubmodelElemValue, "/<int:aasIndex>/submodels/elem",
                                 resource_class_args=tuple([self.pyAAS]))

        # Skill WEB API
        # ProductionManger
        drv_rst_api.add_resource(AASDocumentationDownload, "/documentation/document/<filename>",
                                 resource_class_args=tuple([self.pyAAS]))
        drv_rst_api.add_resource(AASDocumentationDownloadSubmodel, "/<int:aasId>/document/<filename>",
                                 resource_class_args=tuple([self.pyAAS]))
        # static folder path

        drv_rst_api.add_resource(AASStaticSource, "/static/<filename>", resource_class_args=tuple([self.pyAAS]))

        drv_rst_api.add_resource(AASStaticWebSources, "/static/<string:type>/<filename>",
                                 resource_class_args=tuple([self.pyAAS]))
        drv_rst_api.add_resource(AASRTDataVisualizer, "/<int:aasId>/rtdata", resource_class_args=tuple([self.pyAAS]))

        self.pyAAS.serviceLogger.info("REST API namespaces are configured")

    def update(self, channel):
        pass

    def run(self):
        drv_rst_app.run(host=self.ipaddressComdrv, port=self.portComdrv)
        self.pyAAS.serviceLogger.info("REST API namespaces are started")

    def start(self):
        restServerThread = threading.Thread(target=self.run)
        restServerThread.start()

    def stop(self):
        self.pyAAS.serviceLogger.info("REST API namespaces are stopped.")

    def dispatchMessage(self, send_Message):
        try:
            if (send_Message["frame"]["type"] == "register"):
                registerURL = self.registryURL + "/api/v1/registry/" + quote(self.pyAAS.AASID, safe='')
                registerdata = (json.dumps(send_Message))
                r = requests.put(url=registerURL, data=registerdata, headers=self.transportHeader)
                data = json.loads(r.text)
                self.msgHandler.putIbMessage(data)
            elif (send_Message["frame"]["type"] == "HeartBeat"):
                publishURL = self.registryURL + "/i40commu"
                r = requests.post(publishURL, data=json.dumps(send_Message), headers=self.transportHeader)
            else:
                transportURL = self.registryURL + "/i40commu"
                transportHeader = {"content-type": "application/json"}
                transportResponse = requests.post(transportURL, data=json.dumps(send_Message),
                                                  headers=self.transportHeader)
        except Exception as e:
            self.pyAAS.serviceLogger.info("Unable to publish the message to the target http server", str(e))
            httpResponse = HTTPResponse(self.pyAAS)
            self.pyAAS.msgHandler.putIbMessage(httpResponse.createExceptionResponse(send_Message))

    def retrieveMessage(self, testMesage):  # todo
        pass
