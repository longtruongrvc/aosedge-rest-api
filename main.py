import argparse
import time
from Sota.sota import sota_test
from Fota.fota import fota_test
from Monitoring.monitoring import monitoring_test
from Provisioning.provisioning import provision_test
from rich.console import Console
from rich.table import Table

def get_command_line_args():
    # Get unit infomation from command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--unit-id", nargs = "?", required = True)
    parser.add_argument("--unit-name", nargs = "?", required = True)
    parser.add_argument("--unit-version", nargs = "?", required = True)
    parser.add_argument("--unit-ip", nargs = "?", required = True)
    parser.add_argument("--new-firmware", nargs = "?", required = True)
    args = parser.parse_args()
    return args

def test_provision(id, ip, name, version):
    print("START PROVISIONING TEST")
    print("Logs:")
    start_time = time.time()
    status = "PASS" if provision_test(unit_id=id, unit_ip=ip, unit_name=name, unit_version=version) else "FAILED"
    time_execution = round(float(time.time() - start_time), 4)
    print("END PROVISIONING TEST\n\n")
    return status, time_execution

def test_sota(id, name, version):
    print("START SOTA TEST")
    print("Logs:")
    start_time = time.time()
    status = "PASS" if sota_test(unit_id=id, unit_name=name, unit_version=version) else "FAILED"
    time_execution = round(float(time.time() - start_time), 4)
    print("END SOTA TEST\n\n")
    return status, time_execution

def test_fota(id, name, version, firmware):
    print("START FOTA TEST")
    print("Logs:")
    start_time = time.time()
    status = "PASS" if fota_test(unit_id=id, unit_name=name, unit_version=version, new_firmware=firmware) else "FAILED"
    time_execution = round(float(time.time() - start_time), 4)
    print("END FOTA TEST\n\n")
    return status, time_execution

def test_monitoring(id):
    print("START SYSTEM MONITORING TEST")
    print("Logs:")
    start_time = time.time()
    status = "PASS" if monitoring_test(unit_id=id) else "FAILED"
    time_execution = round(float(time.time() - start_time), 4)
    print("END SYSTEM MONITORING TEST\n\n")
    return status, time_execution
        

if __name__ == "__main__":
    device_id = get_command_line_args().unit_id
    device_name = get_command_line_args().unit_name
    device_version = get_command_line_args().unit_version
    device_ip = get_command_line_args().unit_ip
    new_device_firmware = get_command_line_args().new_firmware

    # Test
    table = Table(title="AosEdge Test Functions")
    columns = ["No.", "Board ID", "Board Name", "Board Version", "Function", "Time execution", "Result"]
    provision_status, provision_time = test_provision(id=device_id, ip=device_ip, name=device_name, version=device_version)
    fota_status, fota_time = test_fota(id=device_id, name=device_name, version=device_version, firmware=new_device_firmware)
    sota_status, sota_time = test_sota(id=device_id, name=device_name, version=device_version)
    monitoring_status, monitoring_time = test_monitoring(id=device_id)

    # Summary table
    rows = [
        ["1", f"{device_id}", f"{device_name}", f"{device_version}", "Provisioning", f"{provision_time}", f"{provision_status}"],
        ["2", f"{device_id}", f"{device_name}", f"{device_version}", "SOTA", f"{sota_time}", f"{sota_status}"],
        ["3", f"{device_id}", f"{device_name}", f"{device_version}", "FOTA", f"{fota_time}", f"{fota_status}"],
        ["4", f"{device_id}", f"{device_name}", f"{device_version}", "Monitoring", f"{monitoring_time}", f"{monitoring_status}"],
    ]
    
    for column in columns:
        table.add_column(column)
    for row in rows:
        table.add_row(*row, style="bright_green")

    console = Console()
    console.print(table)
