# create relevant statistics from json

SCAN_FILE = "JSurls.json" # either PYurls.json or JSurls.json
OUTPUT_FILE = "jsScanResults.json"

import json
import matplotlib

def main(): 
    with open(SCAN_FILE, 'r') as f:
        results = json.load(f)

    stats = {"Different Name": 0, "stdlib": 0, "Too Big": 0, "No File": 0, 
             "Undetected": 0, "Detected": 0, "Suspicous": 0, "Unsure": 0,
             "Other": 0, "node.js": 0, "File Match": 0, "New File": 0, 
             "Malware": [], "Suspicious": []}
    malware = []
    suspicious = []
    
    for key, value in results.items():
        if value.get("error", None) is not None:
            # error in finding package
            match value.get("error", None):
                case "stdlib":
                    # in standard library
                    stats["stdlib"] += 1
                case "HTTP ERROR 404":
                    # install name differs from import name
                    stats["Different Name"] += 1
                case "no releases":
                    stats["No File"] += 1
                case "node.js":
                    stats["node.js"] += 1
                case _:
                    print(value.get("error", None))
        elif value.get("virustotal", None) is None:
            # could not find url
            print(f"{key} does not have scan data but should: {value}")
        elif value.get("virustotal", {}).get("error", None) is not None:
            # an error occurred but virustotal ran
            match value["virustotal"]["error"]:
                case "FileTooBig":
                    # file larger than 32 MB
                    stats["Too Big"] += 1
                case _:
                    print(f"Other error {value["virustotal"]["error"]} found")
                    stats["Other"] += 1
        else:
            detections = value["virustotal"].get("last_analysis_stats", None)
            if detections["malicious"] > 0:
                stats["Detected"] += 1
                malware.append(key)
            elif detections ["suspicious"] > 0:
                stats["Suspicious"] += 1
                suspicious.append(key)
            elif detections ["undetected"] > 0:
                stats["Undetected"] += 1
            else:
                stats["Unsure"] += 1

            if value.get("virustotal", {}).get("last_submission_date", None) is not None:
                # found file already ran through scanner
                stats["File Match"] += 1
            else:
                # file had not been scanned
                stats["New File"] += 1
    stats["Malware"] = malware
    stats["Suspicious"] = suspicious
    print("Stats", stats)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(stats, f, indent=4)


    


if __name__ == "__main__":
    main()