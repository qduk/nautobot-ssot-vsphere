"""Functions used to ascertain DataCenter and Service based on SL1 attributes."""
import re

ORGANIZATION_DC_MAPPINGS = [
    {
        "GTN": [
            r"^JUPITER$",
            r"Germantown",
            r"SOUTH AMERICA|JUPITER 2|HUGHES NOC|ENTERPRISE|EM7|T19 DDNS|E05-J2WW-GTN|SBSS|HUGHES RFT|GSDS|T19-NMS|SYSTEM|FACILITY|JUP2 RFT|HUGHES EXXONMOBILE|T19 RFT",
            r"^GTN",
        ]
    },
    {
        "T19": [
            r"^T19-",
        ]
    },
    {
        "GEE": [
            r"^ROW",
        ]
    },
    {
        "DET": [
            r"Detroit",
        ]
    },
    {
        "NLV": [
            r"Vegas",
        ]
    },
    {"split": [r"^JUPITER-", r"^JUP2-", r"^J1", r"^J2", r"^J3"]},
]


DEVICE_NAME_DC_MAPPINGS = [
    {"GTN": [r"^GTN|^DSS|^VMWHN|ac5|ac3|a34|a36|ac303|b12"]},
    {"DET": [r"^DET"]},
    {"GIL": [r"GIL"]},
    {"SWA": [r"SWA"]},
    {"NLV": [r"^NLV|^NVX"]},
    {"BXI": [r"^BXI"]},
    {"SV8": [r"SV8"]},
    {"SLC": [r"SLC"]},
    {"CHY": [r"CHY"]},
    {"CH1": [r"CH1"]},
    {"DA1": [r"DA1"]},
    {"GIL": [r"GIL"]},
    {"SEA": [r"SEA"]},
]

ORGANIZATION_SERVICE_MAPPINGS = {"jupiter": "j1", "jup2": "j2"}

SERVICE_MAPPINGS = [
    {"j1": [r"^J1"]},
    {"j2": [r"^J2"]},
    {"j3": [r"^J3"]},
]


def normalize_service(service):
    """Normalize service.

    Args:
        service (str): Service name.
    """
    service = service.lower()

    if service in ORGANIZATION_SERVICE_MAPPINGS:
        service = ORGANIZATION_SERVICE_MAPPINGS[service]

    return service


def parse_organization_for_site_service(organization):
    """Determine if the organization value provides site and service information."""
    site = "unknown"
    service = "unknown"

    if organization == "Fusion":
        service = "fsn"

    for regex_mapping in ORGANIZATION_DC_MAPPINGS:  # pylint: disable=too-many-nested-blocks
        for key, patterns in regex_mapping.items():
            for pattern in patterns:  # pylint: disable=undefined-loop-variable
                if re.search(pattern, organization, re.IGNORECASE):
                    if key == "split":
                        service, site = organization.replace(" ", "-", 1).split("-", 1)
                    else:
                        site = key

    service = normalize_service(service)

    return (service, site.lower())


def parse_name_for_site(device_name):
    """Try to parse name to find out if the device's site can be determined from its name.

    Args:
        device_name (str): Name of the device.
    """
    site = "unknown"
    for regex_mapping in DEVICE_NAME_DC_MAPPINGS:
        for key, patterns in regex_mapping.items():
            for pattern in patterns:
                if re.search(pattern, device_name, re.IGNORECASE):
                    site = key

    return site.lower()


def parse_name_for_service(device_name):
    """Try to parse name to find out if the device's service can be determined from its name.

    Args:
        device_name (str): Name of the device.
    """
    service = "unknown"
    for regex_mapping in SERVICE_MAPPINGS:
        for key, patterns in regex_mapping.items():
            for pattern in patterns:
                if re.search(pattern, device_name, re.IGNORECASE):
                    service = key
                else:
                    service = "hns"

    return service


def get_site_and_service(organization, device_name):
    """Determine device data center based on organization or device name attributes."""
    service, site = parse_organization_for_site_service(organization)
    if service == "unknown" and site == "unknown":
        service = parse_name_for_service(device_name)
        site = parse_name_for_site(device_name)
    elif service == "unknown":
        service = parse_name_for_service(device_name)
    elif site == "unknown":
        site = parse_name_for_site(device_name)

    # Some site names include 'rfgw' or 'snc' at the end. These are tags applied to the location so they are not needed when determining the site a device goes to.
    site = site.replace("-", " ").split(" ")[0]

    return (service, site)
