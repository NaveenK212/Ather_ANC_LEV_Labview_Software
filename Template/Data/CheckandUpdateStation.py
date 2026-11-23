# --sn EX-0000035-01-_07_I26060033 --result 1 --remark PASS --user operator


import argparse
import json
import sys
import requests

# ============================================
# ARGUMENTS
# ============================================
parser = argparse.ArgumentParser()
parser.add_argument("--user", required=True)
parser.add_argument("--sn", required=True)
parser.add_argument("--result", required=True)
parser.add_argument("--remark", default="")
parser.add_argument(
    "--jsonobj",
    default='[{"parameter":"Test1","value":"Test Value"}]',
    help="JSON string (array of objects) to send as jsonObj parameter"
)
args = parser.parse_args()
#print(args.jsonobj)

# ============================================
# HARDCODED ENDPOINT
# ============================================
ENDPOINT = "http://192.168.28.6:7081/api/productionstage"

# ============================================
# VALIDATE jsonObj (must be valid JSON, sent as a JSON string to match original format)
# ============================================
try:
    # Validate it's proper JSON, but keep it as a string for the payload
    json.loads(args.jsonobj)
    jsonobj_str = args.jsonobj
except json.JSONDecodeError as e:
    print(f"Error: --jsonobj is not valid JSON: {e}")
    sys.exit(1)

# ============================================
# JSON PAYLOAD
# ============================================
data = {
    "OPType": "Check&UpdateStation",
    "masterType": "TestStage",
    "operatinguser": args.user,
    "site": "D004",
    "StageName": "HIPOT",
    "WorkNode": "HIPOT",
    "SN": args.sn,
    "TestResult": args.result,
    "jsonObj": jsonobj_str,
    "DefectRemark": args.remark
}

#print("Payload to send:")
#print(json.dumps(data, indent=4))

# ============================================
# SEND POST REQUEST
# ============================================
headers = {"Content-Type": "application/json"}

try:
    response = requests.post(ENDPOINT, json=data, headers=headers, timeout=10)
    response.raise_for_status()
    print(f"\nStatus Code: {response.status_code}")
    print("Response:")
    try:
        print(json.dumps(response.json(), indent=4))
    except ValueError:
        print(response.text)
except requests.exceptions.RequestException as e:
    print(f"\nError sending request: {e}")
    sys.exit(1)
