import os
import sys
import json
import subprocess

UTILITIES_DIR = os.path.dirname(os.path.realpath(__file__))
while not os.path.isdir(os.path.join(UTILITIES_DIR, "utilities")):
    UTILITIES_DIR = os.path.realpath(UTILITIES_DIR + "/../")
UTILITIES_DIR = os.path.join(UTILITIES_DIR, "utilities")
sys.path.insert(0, UTILITIES_DIR)

from aos import *

#Directory path
WORK_DIR = os.path.dirname(os.path.realpath(__file__))
JSON_DIR = os.path.join(WORK_DIR, "json")
META_DIR = os.path.join(WORK_DIR, "meta")

#Service configuration files
service_json = os.path.join(JSON_DIR, "service.json")
config_yaml  = os.path.join(META_DIR, "config.yaml") 

#Change working dir to current directory
os.chdir(WORK_DIR)

def sota_test(unit_id: str, unit_name: str, unit_version: str):
    verify = False

    # Retrieve information from service.json file
    with open (service_json, "r") as jsonfile:
        info = json.load(jsonfile)

    #Initiate unit, service and subject objects
    unit = AosCloud.Entities.Unit(id      = unit_id,
                                  name    = unit_name,
                                  version = unit_version)

    service = AosCloud.Entities.ServiceInstance(title       = info["Service"]["instance"]["title"],
                                                description = info["Service"]["instance"]["description"])

    subject = AosCloud.Entities.Subjects(label     = info["Subject"]["label"],
                                         priority  = info["Subject"]["priority"],
                                         is_group  = info["Subject"]["is_group"])
    
    if not unit.is_online(timeout=10):
        return verify

    service.create_service_instance()
        
    # Modify config.yaml file to sign and upload instance to AosCloud
    service.modify_service_metadata(meta_dir = META_DIR, 
                                    sv_info_file = service_json, 
                                    sv_metadata_file = config_yaml)
    
    log.info("SIGN AND UPLOAD NEW VERSION OF SERVICE")
    subprocess.run(["aos-signer go"], timeout=10, shell=True, capture_output=True)
        
    subject.create_subject()
    
    subject.assign_service_to_subject(service.service_uuid)

    subject.assign_unit_to_subject(unit.unit_system_id)

    service.approve_service()

    if unit.verify_sota_function(service.service_uuid, service.latest_service_system_version(), timeout=40):
        verify = True
    
    log.info("CLEAN UP RESOURCES AFTER TESTING SOTA FUNCTION")
    subject.remove_subject()
    service.remove_service_instance()
    return verify
    