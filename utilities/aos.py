import os
from requests import *
from pathlib import Path
import json
import yaml
import logging
import time

logging.basicConfig(
    format = '%(asctime)s %(levelname)-8s %(message)s',
    datefmt = '%Y-%m-%d %H:%M:%S',
    level = logging.INFO
)
log = logging.getLogger(__name__)

class AosCloud():
    class Request():
        def __init__(self, url, role, header={"accept": "application/json"}, data=None, files=None):
            self.request_url = url
            self.upload_data = data
            self.upload_files = files
            self.request_headers = header
            self.root_ca = str(Path.home()/".aos"/"security"/"aos-root-certificate.pem")
            self.authenticate_cert = str(Path.home()/".aos"/"security"/f"aos-long-user-{role}.pem")

        def get(self):
            retry = 0
            while retry < 3:
                try:
                    response = get(
                        url = self.request_url,
                        cert = self.authenticate_cert,
                        verify = self.root_ca,
                        headers = self.request_headers
                    )
                    response.raise_for_status()
                    break
                except HTTPError as err:
                    SystemExit(f"{err}\n{response.json()}")
                except ConnectionError as err:
                    log.error(err)
                retry += 1
            if retry == 3:
                SystemExit("Max retries exceed with url. Please check Internet connection")
            return response

        def post(self):
            retry = 0
            while retry < 3:
                try:
                    response = post(
                        url = self.request_url,
                        cert = self.authenticate_cert,
                        headers = self.request_headers,
                        verify = self.root_ca,
                        data = self.upload_data,
                        files = self.upload_files
                    )
                    response.raise_for_status()
                    break
                except HTTPError as err:
                    SystemExit(f"{err}\n{response.json()}")
                except ConnectionError as err:
                    log.error(err)
                retry += 1
            if retry == 3:
                SystemExit("Max retries exceed with url. Please check Internet connection")
            return response
            
        def patch(self):
            retry = 0
            while retry < 3:
                try:
                    response = patch(
                        url = self.request_url,
                        cert = self.authenticate_cert,
                        headers = self.request_headers,
                        verify = self.root_ca,
                        data = self.upload_data
                    )
                    response.raise_for_status()
                    break
                except HTTPError as err:
                    SystemExit(f"{err}\n{response.json()}")
                except ConnectionError as err:
                    log.error(err)
                retry += 1
            if retry == 3:
                SystemExit("Max retries exceed with url. Please check Internet connection")
            return response

        def delete(self):
            retry = 0
            while retry < 3:
                try:
                    response = delete(
                        url = self.request_url,
                        cert = self.authenticate_cert,
                        verify = self.root_ca,
                        headers = self.request_headers
                    )
                    response.raise_for_status()
                    break
                except HTTPError as err:
                    SystemExit(f"{err}\n{response.json()}")
                except ConnectionError as err:
                    log.error(err)
                retry += 1
            if retry == 3:
                SystemExit("Max retries exceed with url. Please check Internet connection")
            return response


    class Entities():
        class ServiceInstance():
            def __init__(self, title, description):
                self.service_title = title
                self.service_description = description
                self.service_id = None
                self.service_uuid = None

            def create_service_instance(self) -> None:
                """
                    Send data with basic configurations (title, description, quotas) to AosCloud to
                    create a service instance. 
                    If the service instance exists, only retrieve information.
                    If not, create a new one and retrieve information.
                """
                data = {
                    "title": self.service_title,
                    "description": self.service_description,
                    "default_quotas": {
                        "cpu_limit": 51,
                        "memory_limit": 10000,
                        "storage_disk_limit": 10000
                    }
                }
                # sv_name = list()
                aos_request = AosCloud.Request(url = "https://sp.aoscloud.io:10000/api/v1/services/",
                                               role = "sp",
                                               header = {"Content-Type": "application/json"},
                                               data = json.dumps(data))

                exist = False 
                for sv in self.list_service_instance():
                    if self.service_title == sv.get("title"):
                        log.info("SERVICE INSTANCE ALREADY EXISTS")
                        self.service_uuid = sv.get("uuid")
                        self.service_id = sv.get("id")
                        exist = True
                
                if not exist:
                    log.info("CREATE NEW SERVICE INSTANCE")
                    response = aos_request.post().json()
                    self.service_uuid = response.get("uuid")
                    self.service_id = response.get("id")
            
            def remove_service_instance(self) -> None:
                """
                    Remove the service instance to AosCloud after testing
                """
                log.info(f"REMOVE SERVICE TITLE: {self.service_title} FROM AOSCLOUD")
                aos_request = AosCloud.Request(url = f"https://sp.aoscloud.io:10000/api/v1/services/{self.service_id}/",
                                               role = "sp")
                aos_request.delete()

            def modify_service_metadata(self, meta_dir, sv_info_file, sv_metadata_file) -> None:
                """
                    Update service_uuid for metadata file (config.yaml) to upload to AosCloud.
                    The service_uuid is collected when the service instance of AosCloud is created
                    and then updated to service.json file. After that, the whole "meta" field of 
                    service.json file is converted into config.yaml
                    Parameters: 
                        meta_dir: path to directory of config.yaml file (class 'str')
                        sv_info_file: service.json file path (class 'str')
                        sv_metadata_file: config.yaml file path (class 'str')
                    Return type: None
                """
                log.info("MODIFY CONFIG.YAML METADATA FILE")
                if not os.path.isdir(meta_dir):
                    os.makedirs(meta_dir)

                if not os.path.exists(sv_metadata_file):
                    with open(sv_metadata_file, "w+"):
                        pass
                
                with open(sv_info_file, "r") as file:
                    service_info = json.load(file)
                    service_info["Service"]["meta"]["publish"]["service_uid"] = self.service_uuid
                
                with open(sv_metadata_file, "w") as file:
                    yaml.dump(service_info["Service"]["meta"], file, sort_keys=False)
                
            def list_service_instance(self) -> list:
                """
                    Get information of each service instance on AosCloud and store in a list.
                    The list will have the following format:
                    [
                        {
                            "title": <value>,
                            "uuid": <value>,
                            "id": <value
                        },
                        {
                        ...
                        }
                    ]
                    Return type: class 'list'
                """
                aos_request = AosCloud.Request(url = "https://sp.aoscloud.io:10000/api/v1/services/",
                                               role = "sp")
                
                response = aos_request.get().json()
                instance_list = list()
                for element in response["results"]:
                    data ={
                        "title": element["title"],
                        "uuid": element["uuid"],
                        "id": element["id"]
                    }
                    instance_list.append(data)
                return instance_list
            
            def latest_service_system_version(self) -> int:
                """
                    AosCloud automatically uses the latest version of uploaded service for service
                    instance, so it is necessary to collect the latest system version of service instance
                    for later validation when service is deployed on Unit.
                    Return type: class 'int'
                """
                aos_request = AosCloud.Request(url = f"https://sp.aoscloud.io:10000/api/v1/services/{self.service_uuid}/service-versions/",
                                               role = "sp")
                
                response = aos_request.get().json()
                service_latest_version = response["results"][0]["id"]
                return service_latest_version

            def list_service_waiting_validation(self) -> list:
                """
                Retrive a list of services that are waiting for validation and store in a list as the following format
                [
                    {
                        "validation_id": <id_1>,
                        "service_titile": <service_1>
                    },
                    {
                        "validation_id": <id_2>,
                        "service_titile": <service_2>            
                    },
                    ...
                ]
                """
                aos_request = AosCloud.Request(url = "https://oem.aoscloud.io:10000/api/v1/fleet-validation-batch/",
                                               role = "oem")
        
                service_validation_list = list()
                response = aos_request.get().json()
                for element in response["results"]:
                    if element["state"] == "Waiting_validation" and element["batch_type"] == "service_layer":
                        data = {
                            "validation_id": element["id"],
                            "service_title": element["service"]["title"]
                        }
                        service_validation_list.append(data)
                return service_validation_list
            
            def approve_service(self) -> None:
                """
                    Check the validation id (fleet id) of service instance created in the list of
                    service waiting validation on AosCloud and approve it to allow service to be deployed
                    on the target device.
                """
                validation_id = [d["validation_id"] for d in self.list_service_waiting_validation() if d["service_title"] == self.service_title][0]
                
                if not validation_id:
                    log.info("SERVICE IS ALREADY VALIDATED")
                    return
                
                log.info("VALIDATE SERVICE BATCH")
                aos_request = AosCloud.Request(url = f"https://oem.aoscloud.io:10000/api/v1/fleet-validation-batch/{validation_id}/approve/",
                                               role = "oem",
                                               header = {"Content-Type": "application/json"},
                                               data = json.dumps({"is_valid": True}))
                aos_request.patch()


        class Subjects():
            def __init__(self, label: str, priority: int, is_group=True):
                self.subject_name = label
                self.subject_priority = priority
                self.is_group = is_group
                self.subject_id = None

            def create_subject(self):
                """
                    Create a subject on AosCloud to assign service for Unit.
                    If the subject exists, only retrieve its id
                    If not, creates a new one and retrieves its id
                """
                data = {
                    "is_group": self.is_group,
                    "label": self.subject_name,
                    "priority": self.subject_priority
                }
                aos_request = AosCloud.Request(url = "https://oem.aoscloud.io:10000/api/v1/subjects/",
                                               role = "oem",
                                               header = {"Content-Type": "application/json"},
                                               data = json.dumps(data))
                sbj_name = list()
                for sbj in self.list_subjects():
                    sbj_name.append(sbj["label"])

                if self.subject_name in sbj_name: 
                    log.info("SUBJECT ALREADY EXISTS")
                    self.subject_id = sbj["id"]
                else:
                    log.info("CREATE NEW SUBJECT")
                    subject = aos_request.post().json()
                    self.subject_id = subject["id"]
                        
            def list_subjects(self) -> list:
                """
                    Get a list of subjects created on AosCloud
                    Parameters: None
                    Return type: class 'list'
                    Note: The list of subjects has the following format:
                    [
                        {
                            "label": <value>,
                            "id": <value>
                        },
                        {
                            ...
                        }
                    ]
                """
                aos_request = AosCloud.Request(url = "https://oem.aoscloud.io:10000/api/v1/subjects/",
                                               role = "oem")        
                response = aos_request.get().json()
                subject_list = [{"label": d["label"], "id": d["id"]} for d in response["results"]]
                return subject_list

            def list_service_assigned(self) -> list:
                """
                    Return a list of service instance assigned to a specific subject
                    Parameters: None
                    Return type: class 'list'
                """
                aos_request = AosCloud.Request(url = f"https://oem.aoscloud.io:10000/api/v1/subjects/{self.subject_id}/services/",
                                               role = "oem")
                response = aos_request.get().json()
                service_assigned = [d["service"]["uuid"] for d in response["results"]]
                return service_assigned
            
            def assign_service_to_subject(self, service_uuid: str) -> None:
                """
                    Assign service to subject to be able to deploy onto Unit
                    Parameters:
                        service_uuid: class 'str'
                    Return type: None
                """
                log.info(f"ASSIGN SERVICE {service_uuid} TO SUBJECT {self.subject_name}")
                data = {
                    "service_uuids": [
                        service_uuid
                    ]
                }
                aos_request = AosCloud.Request(url = f"https://oem.aoscloud.io:10000/api/v1/subjects/{self.subject_id}/services/",
                                               role = "oem",
                                               header = {"Content-Type": "application/json"},
                                               data = json.dumps(data))
                
                if service_uuid not in self.list_service_assigned():
                    aos_request.post()

            def list_unit_assigned(self) -> list:
                """
                    Return a list of unit assigned to a Subject
                """
                aos_request = AosCloud.Request(url = f"https://oem.aoscloud.io:10000/api/v1/subjects/{self.subject_id}/units/",
                                               role = "oem")
                response = aos_request.get().json()
                unit_assigned_list = [d["system_uid"] for d in response["results"]]
                return unit_assigned_list

            def assign_unit_to_subject(self, unit_system_id: str) -> None:
                """
                    Assign Unit to Subject to be able to download service instance from AosCloud
                    Parameters:
                        unit_system_id: class 'str'
                    Return type: None
                """
                data = {
                    "system_uids": [
                        unit_system_id
                    ]
                }
                aos_request = AosCloud.Request(url = f"https://oem.aoscloud.io:10000/api/v1/subjects/{self.subject_id}/units/",
                                               role = "oem",
                                               header = {"Content-Type": "application/json"},
                                               data = json.dumps(data))
                
                if unit_system_id not in self.list_unit_assigned():
                    log.info(f"ASSIGN UNIT WITH ID: {unit_system_id} TO SUBJECT {self.subject_name}")
                    aos_request.post()

            def remove_subject(self):
                log.info(f"REMOVE SUBJECT NAME: {self.subject_name} FROM AOSCLOUD")
                aos_request = AosCloud.Request(url = f"https://oem.aoscloud.io:10000/api/v1/subjects/{self.subject_id}/",
                                               role = "oem")
                aos_request.delete()


        class Unit():
            def __init__(self, id: str, name: str, version: str):
                self.unit_system_id = id
                self.unit_name = name
                self.unit_version = version
                self.unit_id = None #Unique integer value identifying the unit (different from system_id)

            def get_unit_id(self, unit_system_id) -> int:
                """
                    Return the id of a Unit
                    Parameters:
                        unit_system_id: class 'str'
                    Return type: class 'int'
                """
                aos_request = AosCloud.Request(url = "https://oem.aoscloud.io:10000/api/v1/units/",
                                               role = "oem")
                response = aos_request.get().json()
                id = [d["id"] for d in response["results"] if d["system_uid"] == unit_system_id][0]
                return id

            def get_target_system_id(self):
                aos_request = AosCloud.Request(url = "https://oem.aoscloud.io:10000/api/v1/unit-models/",
                                               role = "oem")
                response = aos_request.get().json()
                id = [d["id"] for d in response["results"] if d["name"] == self.unit_name][0]
                return id
                
            def update_target_system(self, unit_config: dict):
                data = {
                    "unit_config": unit_config
                }
                target_system_id = self.get_target_system_id()
                aos_request = AosCloud.Request(url = f"https://oem.aoscloud.io:10000/api/v1/unit-models/{target_system_id}/",
                                               role = "oem",
                                               header = {"Content-Type": "application/json"},
                                               data = json.dumps(data))
                aos_request.patch()

            def is_online(self, timeout) -> bool:
                """
                    Check whether a unit is online or offline
                    Parameters:
                        unit_system_id: class 'str'
                        timeout: class 'int'
                """
                aos_request = AosCloud.Request(url = f"https://oem.aoscloud.io:10000/api/v1/units/{self.unit_system_id}/connection-info/",
                                               role = "oem")
                start_time = time.time()
                while not (online := aos_request.get().json()["is_online"]):
                    if time.time() - start_time > timeout:
                        SystemExit("UNIT IS OFFLINE")
                return True

            def system_monitoring(self, timeout):
                aos_request = AosCloud.Request(url = f"https://oem.aoscloud.io:10000/api/v1/units/{self.unit_system_id}/monitoring/",
                                               role = "oem")
                start_time = time.time()
                while True:
                    response = aos_request.get().json()
                    verify = False if not response[0] else True
                    if verify:
                        time.sleep(10) #Wait around 10s to get full information from unit
                        cpu_val, ram_val, used_disk_val, in_traffic_val, out_traffic_val = [
                            (d["cpu"][0]["value"], d["ram"][0]["value"], d["usedDisk"][0]["value"], d["inTraffic"][0]["value"], d["outTraffic"][0]["value"])
                            for d in response][0]
                        print(f"cpu used: {cpu_val}\nram used: {ram_val}\ndisk used: {used_disk_val}\nin-traffic network: {in_traffic_val}\nout-traffic network: {out_traffic_val}")
                        break
                    if (time.time() - start_time > timeout):
                        break
                return verify

            def verify_sota_function(self, service_uuid, service_latest_system_version, timeout) -> bool:
                """
                    Verifying SOTA function requires 2 conditions:
                    - Service instance is assigned to Unit
                    - Status of that service instance is active
                    Parameters:
                        unit_system_id: class 'str'
                        service_uuid: class 'str'
                        service_latest_system_version: class 'int'
                    Return type: class 'bool'
                """
                aos_request = AosCloud.Request(url = f"https://oem.aoscloud.io:10000/api/v1/units/{self.unit_system_id}/subjects-services/",
                                               role = "oem")
                start_time = time.time()
                while True:
                    time.sleep(10)
                    response = aos_request.get().json()
                    aos_version, run_state = [(d["instances"][0]["aos_version"], d["instances"][0]["run_state"]) for d in response["results"] if d["service"]["uuid"] == service_uuid][0]
                    verify = True if aos_version == service_latest_system_version and run_state == "active" else False
                    if (time.time() - start_time > timeout) or verify:
                        break                    
                return verify
                
            def verify_fota_function(self, uploaded_component_id, uploaded_component_version, timeout) -> bool:
                """
                    Verify the FOTA functionality by checking the vendor version of a specific component after
                    updating firmware
                """
                self.unit_id = self.get_unit_id(self.unit_system_id)
                aos_request = AosCloud.Request(url = f"https://oem.aoscloud.io:10000/api/v1/units/{self.unit_id}/",
                                               role = "oem")
                log.info("UPDATE NEW KERNEL IMAGE. PLEASE CHECK THE DEVICE AND REBOOT MANUALLY")
                start_time = time.time()
                while True:
                    time.sleep(10)            
                    response = aos_request.get().json()
                    current_vendor_version = [d["installed_component"]["vendor_version"] for d in response["unit_update_components"] if d["component_id"] == uploaded_component_id]
                    if not current_vendor_version or current_vendor_version[0] != uploaded_component_version:
                        return False
                    elif (time.time() - start_time > timeout):
                        return False
                    elif current_vendor_version == uploaded_component_version:
                        return True

        class Component():
            def __init__(self):
                self.batch_id = None
                self.component_upload_id = None
                self.component_id = None
                self.component_vendor_version = None

            def upload_batch_file(self, file) -> None:
                """
                    Upload firmware batch file to AosCloud
                """
                log.info("UPLOAD COMPONENT BATCH FILE")
                aos_request = AosCloud.Request(url = "https://oem.aoscloud.io:10000/api/v1/update-components/upload/",
                                               role = "oem",
                                               files = file)
                
                response = aos_request.post().json()
                self.batch_id = str(response["id"]) #Since the type of response["id"] is 'int' not 'str'

            def get_detail_of_batch_file(self, id: str) -> list:
                """
                    Retrieve a list that contains information of uploaded batch file
                    [
                        {
                            "component_id": component_name_1,
                            "version": component_version_1
                        },
                        {
                            "component_id": component_name_2,
                            "version": component_version_2
                        }
                    ]
                """
                aos_request = AosCloud.Request(url = f"https://oem.aoscloud.io:10000/api/v1/update-components/upload/{id}/",
                                               role = "oem")
                # Wait until component is built from batch file
                while True:
                    response = aos_request.get().json()
                    if response["state"] == "ready":
                        break
                # After component is built, gather its information
                uploaded_components = list()
                for component in response["metadata_info"]["components"]:
                    self.component_id = component["id"]
                    self.component_vendor_version = component["vendorVersion"]
                    uploaded_components.append(dict(component_id = self.component_id,
                                                    version = self.component_vendor_version))
                return uploaded_components
            
            def get_component_upload_id(self) -> int:
                aos_request = AosCloud.Request(url = "https://oem.aoscloud.io:10000/api/v1/update-components/",
                                               role = "oem")
                response = aos_request.get().json()
                component_upload_id = [d["id"] for d in response["results"] if 
                                            d["component_id"] == self.component_id and
                                            d["vendor_version"] == self.component_vendor_version and
                                            d["state"] == "Ready"][0]
                return component_upload_id

            def remove_uploaded_component(self):
                log.info(f"REMOVE COMPONENT {self.component_id} FROM AOSCLOUD")
                self.component_upload_id = self.get_component_upload_id()
                aos_request = AosCloud.Request(url = f"https://oem.aoscloud.io:10000/api/v1/update-components/{self.component_upload_id}/",
                                               role = "oem")
                aos_request.delete()
            
            def list_component_waiting_validation(self):
                """
                    Retrive a list of services that are waiting for validation and store in a list as the following format
                    [
                        {
                            "validation_id": <id_1>,
                            "update_components": [
                                {
                                    "component_id": component_name_1,
                                    "version": component_version_1
                                },
                                {
                                    "component_id": component_name_2,
                                    "version": component_version_2
                                }                        
                            ]
                        },
                        {
                            "validation_id": <id_2>,
                            "update_components": [
                                {
                                    "component_id": component_name_3,
                                    "version": component_version_3
                                },
                                {
                                    "component_id": component_name_4,
                                    "version": component_version_4
                                }                        
                            ]
                        }
                        ...
                    ]
                """
                aos_request = AosCloud.Request(url = "https://oem.aoscloud.io:10000/api/v1/fleet-validation-batch/",
                                               role = "oem")
                component_validation_list = list()
                response = aos_request.get().json()
                for element in response["results"]:
                    if (element["state"] == "Waiting_validation" or element["state"] == "Invalid") \
                                and element["batch_type"] == "component":
                        validation_id = element["id"]
                        components_to_update = list()
                        if element["component_stack_to"]:
                            for component in element["component_stack_to"]:
                                components_to_update.append(dict(component_id = component["component_id"],
                                                                 version = component["version"]))           
                        component_validation_list.append(dict(validation_id = validation_id,
                                                              update_components = components_to_update))
                return component_validation_list
            
            def approve_component(self) -> None:
                validation_id = None
                #Check whether batch file is in the list of component waiting for validation
                uploaded_component_from_batch_file = self.get_detail_of_batch_file(self.batch_id)
                validation_id = [d["validation_id"] for d in self.list_component_waiting_validation() if d["update_components"] == uploaded_component_from_batch_file]           
                if not validation_id:
                    log.info("COMPONENT IS ALREADY VALIDATED")
                    return
                else:
                    log.info("APPROVE UPDATED COMPONENT")
                    aos_request = AosCloud.Request(url = f"https://oem.aoscloud.io:10000/api/v1/fleet-validation-batch/{validation_id[0]}/approve/",
                                                   role = "oem",
                                                   header = {"Content-Type": "application/json"},
                                                   data = json.dumps({"is_valid": True}))
                    aos_request.patch()