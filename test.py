import argparse
import time
from Sota.sota import sota_test
from Fota.fota import fota_test
from Monitoring.monitoring import monitoring_test
from Provisioning.provisioning import provision_test
from rich.console import Console
from rich.table import Table

def get_command_line_args():
    parser = argparse.ArgumentParser(description="Script to verify all AosEdge functions")
    sub_parser = parser.add_subparsers(title="Subcommands", dest="command", help="Test AosEdge functions")

    def add_common_args(sub_parser):
        sub_parser.add_argument("--unit-id", nargs="?", required=True)
        sub_parser.add_argument("--unit-name", nargs="?", required=True)
        sub_parser.add_argument("--unit-version", nargs="?", required=True)

    provision_parser = sub_parser.add_parser("provisioning", help="Verify Provisioning function")
    add_common_args(provision_parser)
    provision_parser.add_argument("--unit-ip", nargs="?", required=True)
    provision_parser.set_defaults(function=test_provision)

    sota_parser = sub_parser.add_parser("sota", help="Verify SOTA function")
    add_common_args(sota_parser)
    sota_parser.set_defaults(function=test_sota)

    fota_parser = sub_parser.add_parser("fota", help="Verify FOTA function")
    add_common_args(fota_parser)
    fota_parser.add_argument("--new-firmware", nargs="?", required=True)
    fota_parser.set_defaults(function=test_fota)

    monitoring_parser = sub_parser.add_parser("monitoring", help="Verify Monitoring function")
    add_common_args(monitoring_parser)
    monitoring_parser.set_defaults(function=test_monitoring)

    all_parser = sub_parser.add_parser("all", help="Verify all functions of AosEdge")
    add_common_args(all_parser)
    all_parser.add_argument("--unit-ip", nargs="?", required=True)
    all_parser.add_argument("--new-firmware", nargs="?", required=True)
    all_parser.set_defaults(function=test_all)

    args = parser.parse_args()
    return args

def test_function(test_name, function, **kwargs):
    print(f"START {test_name} TESTS")
    print("Logs:")
    start_time = time.time()
    status = "PASS" if function(**kwargs) else "FAILED"
    time_execution = round(float(time.time() - start_time), 4)
    print(f"END {test_name} TESTS\n\n")
    return [status, time_execution]

def test_provision(id, name, version, ip, **kwargs):
    return provision_test(unit_id=id, unit_ip=ip, unit_name=name, unit_version=version)

def test_sota(id, name, version, **kwargs):
    return sota_test(unit_id=id, unit_name=name, unit_version=version)

def test_fota(id, name, version, new_firmware, **kwargs):
    return fota_test(unit_id=id, unit_name=name, unit_version=version, new_firmware=new_firmware)

def test_monitoring(id, name, version, **kwargs):
    return monitoring_test(unit_id=id, unit_name=name, unit_version=version)

def test_all(id, name, version, ip, new_firmware):
    return (
        test_function("PROVISIONING", test_provision, id=id, name=name, version=version, ip=ip),
        test_function("FOTA", test_fota, id=id, name=name, version=version, new_firmware=new_firmware),
        test_function("SOTA", test_sota, id=id, name=name, version=version),
        test_function("MONITORING", test_monitoring, id=id, name=name, version=version),
    )

if __name__ == "__main__":
    arg = get_command_line_args()
    
    table = Table(title="AosEdge Test Functions")
    columns = ["No.", "Board ID", "Board Name", "Board Version", "Function", "Result", "Time execution"]
    rows = list()
    if arg.command == "all":
        results = test_all(id=arg.unit_id, name=arg.unit_name, version=arg.unit_version, 
                           ip=getattr(arg, "unit_ip", None), new_firmware=getattr(arg, "new_firmware", None))
        test_name = ["PROVISIONING", "FOTA", "SOTA", "MONITORING"]
        for i, test in enumerate(results):
            rows.append(
                [f"{i+1}", f"{arg.unit_id}", f"{arg.unit_name}", f"{arg.unit_version}", f"{test_name[i]}", f"{test[0]}", f"{test[1]}"]
            )
    else:    
        results = test_function(arg.command.upper(), arg.function, id=arg.unit_id, name=arg.unit_name, 
                                version=arg.unit_version, ip=getattr(arg, "unit_ip", None), new_firmware=getattr(arg, "new_firmware", None))
        print(results)
        rows.append(
            ["1", f"{arg.unit_id}", f"{arg.unit_name}", f"{arg.unit_version}", f"{arg.command.upper()}", f"{results[0]}", f"{results[1]}"]
        )
    for column in columns:
        table.add_column(column)
    for row in rows:
        table.add_row(*row, style="bright_green")
    console = Console()
    console.print(table)