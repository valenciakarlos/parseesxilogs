import requests
import json
import yaml
import urllib3
from urllib3.exceptions import InsecureRequestWarning
import argparse

def validate_arguments():
    parser = argparse.ArgumentParser(description="Access HPE server via iLO IP using redfis to collect BIOS information")
    # The first argument, input_file, is a positional argument (required).
    parser.add_argument("hostname", help="iLO IP Address")
    parser.add_argument("-u", "--username", help="iLO Username")
    parser.add_argument("-p", "--password", help="iLO Password")


    args = parser.parse_args()
    return args

##### MAIN ######


# Suppress insecure request warnings (not recommended for production)
urllib3.disable_warnings(InsecureRequestWarning)

# Call arguments validation script
args = validate_arguments()
ip_address = args.hostname
username = args.username
password = args.password

# URL for accessing BIOS settings
bios_url = f"https://{ip_address}/redfish/v1/Systems/1/Bios/Settings"


# Headers for authentication
headers = {'Content-Type': 'application/json'}

# Send a GET request to retrieve BIOS settings
response = requests.get(bios_url, auth=(username, password), headers=headers, verify=False)


# Check for successful response
if response.status_code == 200:
    # Parse the JSON response
    try:
        bios_data = json.loads(response.text)
        print("**BIOS Settings:**")
        for setting, value in bios_data['Attributes'].items():
            print(f"- {setting}: {value}")
    except json.JSONDecodeError as e:
        print(f"Error parsing response as JSON: {e}")
else:
    print("Error retrieving BIOS settings. Response code:", response.status_code)

    # Pretty-print the response text, attempting both YAML and JSON
    try:
        formatted_response = yaml.dump(yaml.safe_load(response.content), default_flow_style=False)
    except yaml.YAMLError:
        formatted_response = json.dumps(response.json(), indent=6)  # Use response.json() for automatic JSON parsing

    print("------------ BIOS Settings ----------------")
    print(formatted_response)

systems_url = f"https://{ip_address}/redfish/v1/Systems/1"

response = requests.get(systems_url, auth=(username, password), headers=headers, verify=False)

if response.status_code == 200:
    print("---------- System Settings ---------------------------")
    formatted_response=json.dumps(response.json(), indent=8)
    print(formatted_response)