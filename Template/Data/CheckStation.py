# --sn EX-0000035-01_07_I26060033

import argparse
import json
import sys
import requests
# ============================================
# ARGUMENTS
# ============================================
parser = argparse.ArgumentParser()
parser.add_argument("--sn", required=True)
parser.add_argument("--remark", default="")
parser.add_argument(
    "--jsonobj",
    default='[{"parameter":"Test1","value":"Test Value"}]',
    help="JSON string (array of objects) to send as jsonObj parameter"
)
args = parser.parse_args()
# ============================================
# HARDCODED ENDPOINT
# ============================================
ENDPOINT = "http://192.168.28.6:7081/api/productionstage"
# ============================================
# EXPECTED STRING TO CHECK IN RESPONSE
# ============================================
EXPECTED_STRING = "Last station:CB_FG_Label_Binding,Next Station:HIPOT"
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
    "OPType": "CheckStation",
    "masterType": "TestStage",
    "operatinguser": "Admin",
    "site": "D004",
    "StageName": "CP_FG_Label_Binding",
    "WorkNode": "CP_FG_Label_Binding05",
    "SN": args.sn,
    "TestResult": "1",
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

    # Get response body as text for string checking, regardless of content type
    response_text = response.text
    try:
        parsed = response.json()
        print(json.dumps(parsed, indent=4))
    except ValueError:
        parsed = None
        print(response_text)

    # ============================================
    # CHECK IF EXPECTED STRING IS PRESENT IN RESPONSE
    # ============================================
    if EXPECTED_STRING in response_text:
        print(f"\n[CHECK] PASS")
    else:
        print(f"\n[CHECK] FAIL")
        sys.exit(1)

except requests.exceptions.RequestException as e:
    print(f"\nError sending request: {e}")
    sys.exit(1)
