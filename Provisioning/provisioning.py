import os
import sys
import subprocess
import json

UTILITIES_DIR = os.path.dirname(os.path.realpath(__file__))
while not os.path.isdir(os.path.join(UTILITIES_DIR, "utilities")):
    UTILITIES_DIR = os.path.realpath(UTILITIES_DIR + "/../")
UTILITIES_DIR = os.path.join(UTILITIES_DIR, "utilities")
sys.path.insert(0, UTILITIES_DIR)

from aos import *

def provision_test(unit_ip: str, unit_id: str, unit_name: str, unit_version: str) -> bool:
    log.info(f"PROVISION TARGET DEVICE {unit_name}")
    unit = AosCloud.Entities.Unit(id      = unit_id,
                                  name    = unit_name,
                                  version = unit_version)
    if unit_id in unit.get_provisioned_units():
        log.info("UNIT IS ALREADY PROVISIONED")
        return True
    elif subprocess.run([f"aos-prov -u {unit_ip}:8089"], shell=True, capture_output=True).returncode == 0:
        log.info("UNIT IS SUCCESSFULLY PROVISIONED")
        target_system_file = os.path.join(os.path.dirname(__file__), "target_system.json")
        with open(target_system_file, "r") as config_file:
            config = json.load(config_file)
        log.info(f"UPLOAD UNIT MODEL FOR DEVICE {unit_name}")
        unit.update_target_system(unit_config = config)
        return True
    else:
        log.error("FAILED TO PROVISION UNIT")
        return False
