import os
import sys

UTILITIES_DIR = os.path.dirname(os.path.realpath(__file__))
while not os.path.isdir(os.path.join(UTILITIES_DIR, "utilities")):
    UTILITIES_DIR = os.path.realpath(UTILITIES_DIR + "/../")
UTILITIES_DIR = os.path.join(UTILITIES_DIR, "utilities")
sys.path.insert(0, UTILITIES_DIR)

from aos import *

def fota_test(unit_id: str, unit_name: str, unit_version: str, new_firmware: str):
    verify = False
    if not os.path.exists(os.path.join(os.path.dirname(__file__), new_firmware)):
        log.error(f"No such file or directory: {new_firmware}")
        return verify
    
    unit = AosCloud.Entities.Unit(id      = unit_id,
                                  name    = unit_name,
                                  version = unit_version)

    if not unit.is_online(timeout=20):
        return verify

    with open(os.path.join(os.path.dirname(__file__), new_firmware), "rb") as fp:
        file_data = fp.read()

    firmware_to_upload = {
        "file": (new_firmware, file_data)
    }
    component = AosCloud.Entities.Component()
    component.upload_batch_file(firmware_to_upload)
    component.approve_component()
    if unit.verify_fota_function(component.component_id, component.component_vendor_version, timeout=500):
        verify = True
    log.info("CLEAN UP RESOURCES AFTER TESTING FOTA FUNCTION")
    component.remove_uploaded_component()
    return verify