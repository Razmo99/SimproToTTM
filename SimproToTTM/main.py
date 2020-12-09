#!/usr/bin/env python3
import logging
import logging.handlers
import SimproAPI
import TelstraTrackMonitorAPI
import time
import json
import schedule
from conf_mgr import conf_mgr
import os, pathlib

#Change the current working directory to be the parent of the main.py
os.chdir(pathlib.Path(__file__).resolve().parent)
#Initialise logging
logging_format='%(asctime)s - %(levelname)s - [%(module)s]::%(funcName)s() - %(message)s'
log_name = os.getenv("LOG_SAVE_LOCATION",'simpro_to_ttm.log')
rfh = logging.handlers.RotatingFileHandler(
filename=log_name, 
mode='a',
maxBytes=5*1024*1024,
backupCount=2,
encoding='utf-8',
delay=0
)
console=logging.StreamHandler()
console.setLevel(logging.INFO)
logging.basicConfig(
    level=logging.DEBUG,
    format=logging_format,
    handlers=[rfh,console]
)

logger = logging.getLogger(__name__)

def main():
    #Initialise Config
    conf = conf_mgr()
    #if the config has sections and it passes the check config fun continue
    if conf.check_conf():
        #Initialise the TelstraTrackMonitorAPI.TokenManager with the fields pulled from the config
        ttm_token = TelstraTrackMonitorAPI.TokenManager(
            server=conf.config['ttm_auth']['server'],
            client_id=conf.config['ttm_auth']['client_id'],
            client_secret=conf.config['ttm_auth']['client_secret'],
            save_location=conf.config['ttm_auth']['save_location']
        )
        ttm_token.load_token()
        logger.debug('Initialised TTM Token Manager')
        #Initialise the SimproAPI.TokenManager with the fields pulled from the config
        simpro_token=SimproAPI.TokenManager(
            server=conf.config['simpro_auth']['server'],
            client_id=conf.config['simpro_auth']['client_id'],
            client_secret=conf.config['simpro_auth']['client_secret'],
            username=conf.config['simpro_auth']['username'],
            password=conf.config['simpro_auth']['password'],
            save_location=conf.config['simpro_auth']['save_location']
        )
        simpro_token.load_token()
        logger.debug('Initialised Simpro Token Manager')
    else:
        exit()

    if ttm_token.update_token() and simpro_token.update_token():
        simpro_trackable_companies=[10]
        #List containing information on companies that have trackable plants.
        with SimproAPI.Trackables(simpro_token.server,simpro_token.access_token) as trackables:
            simpro_trackable_companies=trackables.get_companies(
                simpro_trackable_companies,
                [conf.config['simpro_tracker']['serial'],conf.config['simpro_tracker']['last_known_location']]
            )
        #List containing all eligable ttm devices to match for.
        ttm_devices=[]
        with TelstraTrackMonitorAPI.Sessions(ttm_token.server,ttm_token.access_token) as TTM:
            ttm_devices=TTM.devices_get(
                {'$filter':'not(deviceFriendlyName eq null)',
                '$select':'serialNumber, lastLatitude, lastLongitude'}
            ).json()
        #Place to stick match results
        simpro_equipment_updates=[]
        #Iterate over simpro companies
        if ttm_devices:
            for company in simpro_trackable_companies:
                #Iterate over all simpro plants
                for trackable_plant in company['trackable_plants']:
                    #compare the ttm data to the simpro plant data for serial matches
                    compare_data=SimproAPI.Trackables(simpro_token.server,simpro_token.access_token).compare_equipment(
                        company['id'], # id of the company
                        trackable_plant['id'], # id of the trackable plant
                        trackable_plant['trackable_plant'], # Plant equipment to match againts
                        ttm_devices, # List of ttm devices to match against
                        'serialNumber', #Serial Number field in ttm
                        ['serialNumber','lastLatitude','lastLongitude'], # other ttm fields to return when a match is found
                        conf.config['simpro_tracker']['serial'], # Simpro serial number field
                        [conf.config['simpro_tracker']['last_known_location']] #simpro Fields to return on a match
                        )
                    #for each match append it to a updates list
                    for data in compare_data:
                        simpro_equipment_updates.append(data)
        #For each company if we have equipment updates; action them.
        if simpro_equipment_updates:
            #Iterate over each update
            with SimproAPI.Sessions(simpro_token.server,simpro_token.access_token) as simpro_patch_session:
                for simpro_equipment_update in simpro_equipment_updates:
                    #Iterate over the custom fields to modify
                    for simpro_equipment_custom_field in simpro_equipment_update['plant_custom_fields']:
                        #Patch changes to simpro
                        map_url="http://maps.google.com/maps?q={0},{1}".format(simpro_equipment_update['match_returned_custom_fields']["lastLatitude"],simpro_equipment_update['match_returned_custom_fields']["lastLongitude"])
                        if not map_url == simpro_equipment_custom_field['value']:
                            simpro_patch_specific=simpro_patch_session.plants_and_equipment_custom_fields_patch_specific(
                                simpro_equipment_update['company_id'],
                                simpro_equipment_update['plant_type_id'],
                                simpro_equipment_update['plant_id'],
                                simpro_equipment_custom_field['id'],
                                {'Value':map_url}
                            )
                            if simpro_patch_specific.ok:
                                logger.info('Successfully Patched changes: {company_id: '+str(simpro_equipment_update['company_id'])+' plant_type_id: '+str(simpro_equipment_update['plant_type_id'])+' plant_id: '+str(simpro_equipment_update['plant_id'])+' custom_field_id: '+str(simpro_equipment_custom_field['id'])+'}')
                            else:
                                logger.info('Failed to Patched changes: {company_id: '+str(simpro_equipment_update['company_id'])+' plant_type_id: '+str(simpro_equipment_update['plant_type_id'])+' plant_id: '+str(simpro_equipment_update['plant_id'])+' custom_field_id: '+str(simpro_equipment_custom_field['id'])+'}')
                        else:
                            logger.info('Skipping; Location has not changed for: {company_id: '+str(simpro_equipment_update['company_id'])+' plant_type_id: '+str(simpro_equipment_update['plant_type_id'])+' plant_id: '+str(simpro_equipment_update['plant_id'])+' custom_field_id: '+str(simpro_equipment_custom_field['id'])+'}')
        else:
            logger.info('Did not find any equipment to patch in simpro')
    else:
        logger.exception('Unable to sync. Failed to update tokens.')

def catch_exceptions(cancel_on_failure=False):
    def catch_exceptions_decorator(job_func):
        @functools.wraps(job_func)
        def wrapper(*args, **kwargs):
            try:
                return job_func(*args, **kwargs)
            except:
                import traceback
                print(traceback.format_exc())
                if cancel_on_failure:
                    return schedule.CancelJob
        return wrapper
    return catch_exceptions_decorator

if __name__ == "__main__":
    #@catch_exceptions(cancel_on_failure=False)
    def job():
        logger.info('started job')
        logger.info('------------- Starting Session -------------')
        start=time.time()   
        main()
        end=time.time()
        logger.info('Synced in:'+str(end-start)+' Second(s)')
        logger.info('------------- Finished Session -------------')

    run_every = os.getenv('SCHEDULE_RUN_EVERY_MINUTES',30)
    logger.info('Syncing every: '+run_every+' minutes')
    schedule.every(int(run_every)).minutes.do(job)
    while 1:
        schedule.run_pending()
        time.sleep(1)