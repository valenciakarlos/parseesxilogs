import requests
import json
import yaml
import urllib3
from urllib3.exceptions import InsecureRequestWarning

# Suppress insecure request warnings (not recommended for production)
urllib3.disable_warnings(InsecureRequestWarning)

# Replace with your server's details

ip_address = "10.208.64.50"
username = "novmware"
password = "Welcome01"

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
        formatted_response = json.dumps(response.json(), indent=4)  # Use response.json() for automatic JSON parsing

    print("Response text:")
    print(formatted_response)

