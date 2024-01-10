import os
import sys

UTILITIES_DIR = os.path.dirname(os.path.realpath(__file__))
while not os.path.isdir(os.path.join(UTILITIES_DIR, "utilities")):
    UTILITIES_DIR = os.path.realpath(UTILITIES_DIR + "/../")
UTILITIES_DIR = os.path.join(UTILITIES_DIR, "utilities")
sys.path.insert(0, UTILITIES_DIR)

from aos import *

def monitoring_test(unit_id: str):
    verify = False
    unit = AosCloud.Entities.Unit(id      = unit_id,
                                  name    = None,
                                  version = None)
    log.info("GATHER SYSTEM INFORMATION")
    if unit.system_monitoring(timeout=30):
        verify = True
    return verify