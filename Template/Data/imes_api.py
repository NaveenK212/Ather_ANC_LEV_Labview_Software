import argparse
import json

# ============================================
# ARGUMENTS
# ============================================
parser = argparse.ArgumentParser()

parser.add_argument("--user", required=True)
parser.add_argument("--stage", required=True)
parser.add_argument("--worknode", required=True)
parser.add_argument("--sn", required=True)
parser.add_argument("--result", required=True)
parser.add_argument("--remark", default="")

args = parser.parse_args()

# ============================================
# JSON OUTPUT
# ============================================
data = {
    "OPType": "Check&UpdateStation",
    "masterType": "TestStage",
    "operatinguser": args.user,
    "site": "",
    "StageName": args.stage,
    "WorkNode": args.worknode,
    "SN": args.sn,
    "TestResult": args.result,
    "jsonObj": "[{\"parameter\":\"Test1\",\"value\":\"Test Value\"}]",
    "DefectRemark": args.remark
}

print(json.dumps(data, indent=4))
