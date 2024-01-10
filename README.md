# How to use

## Description

This CI pipeline aims to test the AosEdge functions including:
- Provisioning target device to AosCloud
- Update software for unit from AosCloud
- Update firmware for unit from AosCloud
- Monitoring unit

## Preparation

### Prepare AosCloud certificates for authentication
In order to communicate with AosCloud server through RESTFUL API, the script requires 4 certificates as below:
- aos-user-oem.pem: include a certificate chain including public key, private key and root certificates for OEM user.
- aos-user-sp.pem: include a certificate chain including public key, private key and root certificates for SP user
- aos-user-oem.p12: OEM user certificates - AosEdge SDK tools use this cert to authenticate with AosCloud
- aos-user-sp.p12: SP user certificate - AosEdge SDK tools use this cert to authenticate with AosCloud
- aos-root-certificate.pem: AosEdge root certificate used to trust the server certificate

### Software-Update
- Source code of the application must be placed in ````src```` folder
- Provide service configurations within ````service.json```` file in the ```Sota``` folder. Note that the "service_uid" field must be left empty, others can be modified optionally.

### Firmware-Update
- Place the firmware to update in the ```Fota``` folder.

## How to use this CI pipeline
1. Boot target device with AosEdge image. Make sure the device can connect with Internet.
2. Check VIN ID, IP and device models (name and version)
   ```bash
   ifconfig  # Check IP
   cat /var/aos/vis/vin  # Check VIN ID
   cat /etc/aos/board_model or /etc/aos/unit_model # Check device models
   ```
3. Run the main script with the following arguments
   ```bash
   python3 main.py \
      --unit-id <VIN_ID> \
      --unit-ip <IP> \
      --unit-name <NAME> \
      --unit-version <VERSION> \ #Format: x.y.z (E.g.: 1.0.0)
      --new-firmware <NAME_OF_FIRMWARE>
   ```