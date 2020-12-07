import configparser
import logging
import os

logger = logging.getLogger(__name__)
logger.debug('Importing Module : '+__name__)

class conf_mgr(object):

        def __init__(self,config_name='config.ini'):
                self.config = configparser.ConfigParser()
                self.conf_name=config_name
                
        def save_conf(self):
                """Save the Current config of this class
                
                """
                with open(self.conf_name,'w') as configfile:
                        self.config.write(configfile)
                logger.debug('Saved: '+self.conf_name)
                
        def read_conf(self):
                """Read the saved config if any."""
                self.config.read(self.conf_name)
                logger.debug('Loaded: '+self.conf_name)

        def create_conf(self):
                """Called when no config is found and initial values need to be entered
                """
                self.config['simpro_auth']={
                        'server':'',
                        'client_id':'',
                        'client_secret':'',
                        'save_location':'',
                        'username':'',
                        'password':''
                }
                self.config['simpro_tracker']={
                        'serial':'',
                        'last_known_location':''
                }                
                self.config['ttm_auth']={
                        'server':'',
                        'client_id':'',
                        'client_secret':'',
                        'save_location':''
                }
                logger.debug('Created: '+self.conf_name)

        def check_docker(self):
                docker_enviroment_variables=[
                        {'env_var':'SIMPRO_SERVER','section':'simpro_auth','value':'server'},
                        {'env_var':'SIMPRO_CLIENT_ID','section':'simpro_auth','value':'client_id'},
                        {'env_var':'SIMPRO_CLIENT_SECRET','section':'simpro_auth','value':'client_secret'},
                        {'env_var':'SIMPRO_USERNAME','section':'simpro_auth','value':'username'},
                        {'env_var':'SIMPRO_PASSWORD','section':'simpro_auth','value':'password'},
                        {'env_var':'SIMPRO_SAVE_LOCATION','section':'simpro_auth','value':'save_location'},
                        {'env_var':'SIMPRO_SERIAL','section':'simpro_tracker','value':'serial'},
                        {'env_var':'SIMPRO_LAST_KNOWN_LOCATION','section':'simpro_tracker','value':'last_known_location'},
                        {'env_var':'TTM_SERVER','section':'ttm_auth','value':'server'},
                        {'env_var':'TTM_CLIENT_ID','section':'ttm_auth','value':'client_id'},
                        {'env_var':'TTM_CLIENT_SECRET','section':'ttm_auth','value':'client_secret'},
                        {'env_var':'TTM_SAVE_LOCATION','section':'ttm_auth','value':'save_location'}]
                result=False
                try:
                        self.config['ttm_auth']
                        self.config['simpro_auth']
                        self.config['simpro_tracker']
                except KeyError:
                        self.create_conf()
                        pass
                else:
                        pass

                for var in docker_enviroment_variables:
                        if  not os.getenv(var['env_var'],'') == '':
                                result=True
                                logger.debug('Loaded env_var: '+var['env_var'])
                                self.config[var['section']][var['value']]=os.getenv(var['env_var'],'')
                return result                                

        def check_conf(self):
                """Some basic checks to ensure that the config is usable"""
                #TODO - more validation checks
                if self.check_docker():
                        return True  
                else:
                        self.read_conf()            
                try:
                        self.config['ttm_auth']
                        self.config['simpro_auth']
                        self.config['simpro_tracker']
                except KeyError:
                        logger.error('No existing config found creating blank config')
                        self.create_conf()
                        self.save_conf()
                        return False
                else:
                        logging.debug('Found expected headers in the config file')
                        return True
