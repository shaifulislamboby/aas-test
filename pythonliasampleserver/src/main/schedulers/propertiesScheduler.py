'''
Created on 24 Oct 2021

@author: pakala
'''
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from importlib import import_module

try:
    from modules import *
except ImportError:
    from main.modules import *

class Scheduler(object):
    """
    The scheduler of the Administration Shell
    """

    def __init__(self, pyAAS):
        self.pyAAS = pyAAS
        self.f_modules = {}

        jobstores = {
            'default': MemoryJobStore()
        }
        executors = {
            'default': ThreadPoolExecutor(20),
        }
        job_defaults = {
            'coalesce': False,
            'max_instances': 3
        }

        # initialize the scheduler
        self.scheduler = BackgroundScheduler(
            jobstores=jobstores, executors=executors, job_defaults=job_defaults)
        self.triggers = {}

    def configure(self):
        """Configures the triggers and jobs out of the given configuration

        :param lxml.etree.ElementTree configuration: XML DOM tree of
        the configuration

        """
        # add each trigger of the configuration to the scheduler
        propertydict = self.pyAAS.tdPropertiesList
        for key in propertydict:
            propertyData = propertydict[key]
            propertyData["key"] = key
            params = [self.pyAAS,propertyData]
            propertyName = propertyData["propertyName"]
            updateFrequency = propertyData["updateFrequency"]
            if (updateFrequency == "subscribe"):
                updateFunction = import_module("modules."+"f_propertySubscribe").function
                self.scheduler.add_job(updateFunction,args=params, id=propertyName)
            else:
                updateFunction = import_module("modules."+"f_propertyRead").function
                self.scheduler.add_job(updateFunction, "interval" ,seconds=6, args=params, id=propertyName, replace_existing=True)

    def start(self):
        """Runs the scheduler.

        After the scheduler has been started, we can no longer alter
        its settings.

        """
        self.scheduler.start()

    def stop(self):
        self.scheduler.shutdown()
