import os
import sys

UTILITIES_DIR = os.path.dirname(os.path.realpath(__file__))
while not os.path.isdir(os.path.join(UTILITIES_DIR, "utilities")):
    UTILITIES_DIR = os.path.realpath(UTILITIES_DIR + "/../")
UTILITIES_DIR = os.path.join(UTILITIES_DIR, "utilities")
sys.path.insert(0, UTILITIES_DIR)

from aos import *

def monitoring_test(unit_id: str, unit_name: str, unit_version: str):
    unit = AosCloud.Entities.Unit(id      = unit_id,
                                  name    = unit_name,
                                  version = unit_version)
    
    if not unit.is_online(timeout=600): #Modify timeout based on VDK or real board
        return False

    log.info("GATHER SYSTEM INFORMATION")

    if unit.system_monitoring(timeout=300):
        return True
