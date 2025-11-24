# get list of pypi packages (mostly working except those with multiple names)
# run list of pypi packages through VirusTotal API

# before running run 'export VIRUSTOTAL_API_KEY=<My-API-Key>'
# you will probably need to change the RESULTS_FILE location

import os
import sys
import requests
import json
import vt # pip install vt-py
from typing import Dict, Optional
# from packaging.version import parse as parse_version

DO_PACKAGE_LOOKUP = True
DO_VIRUS_SCAN = False

DIRECTORY = "./Python"
RESULTS_FILE = "local/PYurls.json" # stores package urls and scan results as json

# before running, do 'export VIRUSTOTAL_API_KEY=<My-API-Key>' in terminal
if DO_VIRUS_SCAN:
    apikey = os.environ.get('VIRUSTOTAL_API_KEY')
    if apikey is None:
        print("Error: API key 'VIRUSTOTAL_API_KEY' does not exist")
        exit()
    client = vt.Client(apikey)


# find package download url and sha256 hash for it
# look for source if it exists, and return top url if it doesn't
# returns list with entries containing url and sha256 hash
def get_package_url(package_name : str):

    retval: Dict[str, Optional[str]] = {"url": None, "sha256": None, "error": None, "virustotal": None}
    try:
        # check if in standard library
        if package_name in sys.stdlib_module_names:
            retval["error"] = "stdlib"
            return retval

        # Make a request to the PyPI JSON API for the package
        response = requests.get(f'https://pypi.org/pypi/{package_name}/json')

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()

            # dump for reading
            # with open(f"local/dumps/{package_name}.json", 'w') as f:
            #     json.dump(data, f, indent=4)

            # Extract the URL(s) for the latest version of the package
            urls = data.get('urls', {})
            if len(urls) == 0:
                print(f"Error: No url found for package '{package_name}'.")
                retval["error"] = "no releases"
                return retval
            
            for i in range(0, len(urls)):
                if urls[i]["python_version"] == "source":
                    retval["url"] = urls[i]["url"]
                    retval["sha256"] = urls[i]["digests"]["sha256"]
                    return retval
            # if no source, then just pick one
            print(f"Warning: Picking top url")
            retval["url"] = urls[0]["url"]
            retval["sha256"] = urls[0]["digests"]["sha256"]
            return retval
        
            # this doesn't work well
            # releases = data.get('releases', {})
            # if releases:
            #     # Sort versions using `packaging.version.parse` to handle pre-release versions
            #     latest_version = sorted(releases.keys(), key=parse_version, reverse=True)[0]
            #     package_url = releases[latest_version][0].get('url')
            #     return package_url
            # else:
            #     print(f"Error: No releases found for package '{package_name}'.")
            #     return "No file"
        else:
            print(f"Error: Failed to fetch data for '{package_name}', status code {response.status_code}.")
            retval["error"] = f"HTTP error {response.status_code}"
            return retval
    # except IndexError as e:
    #     # it appears that everything the brings up this exception has no releases
    #     print(f"Error: '{package_name}' appears to have no urls {e}")
    #     retval["error"] = "no releases"
    #     return retval
    except Exception as e:
        print(f"Error: An exception occurred while fetching data for '{package_name}': {e}")
        retval["error"] = "other"
        return retval


# scan file and return dict with fields
# virus: True, False
# response: api response
def get_vt_report(hash : str):
    file = client.get_object(f"/files/{hash}")
    dict = file.to_dict()
    del dict["vt_report"]["attributes"]["last_analysis_results"]
    return dict


def main():
    files = os.listdir(DIRECTORY)
    models = []
    all_packages = {} # dict of packages from each model
    unique_packages = set()

    # get all packages from all files
    for file in files: 
        # print(f"Scanning {file}...", end="")
        filepath = os.path.join(DIRECTORY, file)

        if os.path.isfile(filepath):
            # get model name from filename
            base_name, ext = os.path.splitext(file)
            models.append(base_name)

            # put all packages in file into a dict
            with open(filepath, 'r') as f:
                packages = f.readlines()
            packages = [pkg.strip() for pkg in packages]
            all_packages[base_name] = packages
        else:
            print(f"Error: {filepath} does not exist")

        # print(" DONE")
    print(f"Finished parsing {len(files)} files")

    for packages in all_packages.values():
        unique_packages.update(packages)
    # print(unique_packages)
    # print(len(unique_packages))

    # load results of last url search
    if os.path.isfile(RESULTS_FILE):
        try:
            print(f"Found results file {RESULTS_FILE}")
            with open(RESULTS_FILE, 'r') as f:
                results = json.load(f)
        except Exception as e:
            print(f"Error: could not parse RESULTS_FILE: {e}")
            results = {}
    else:
        print(f"Could not find results file {RESULTS_FILE}")
        results = {}

    if DO_PACKAGE_LOOKUP:
        # scan for package links
        # this returns a "good enough" list, but errors have to be manually fixed
        print("Doing package lookup")
        try:
            for key in results.keys():
                results[key]["virustotal"] = None
            for package in unique_packages:
                # only scan if it's not in the results
                if package not in results.keys():
                    # package has not been seen before
                    print(f"Searching for {package}...")
                    results[package] = get_package_url(package)
                    pass
                # used for making manual corrections during development
                elif package in results.keys() and results[package]["url"] == "HTTP ERROR 404":
                    # print(f"Searching again for {package}...")
                    # results[package] = get_package_url(package)
                    pass

        except KeyboardInterrupt:
            # allow user to terminate whenever
            print("\nKeyboard Interrupt Received")
        except Exception as e:
            print(f"An Exception occured while looking for packages: {e}")
        finally:
            # store results
            print(f"Writing results to {RESULTS_FILE}")
            with open(RESULTS_FILE, 'w') as f:
                json.dump(results, f, indent=4)
            pass
    else:
        print("Skipping package lookup")


    if not DO_VIRUS_SCAN: 
        print("Skipping Virus Scan")
        client.close()
        exit()
    else:
        print("Doing Virus Scan")
    
    # run scan for everything in results
    try:
        for key, entry in results.items():
            try:
                if "vt_report" not in entry.keys():
                    if entry["sha256"] is not None:
                        # if link has a sha256, it was found
                        print(f"Getting file report for {key}")
                        entry["vt_report"] = get_vt_report(entry["sha256"])
                        results.update({key:entry})
                        pass
                    else:
                        # write nothing but note we scanned this item
                        print(f"Skipping {key}")
                        entry["vt_report"] = None
                        results.update({key:entry})
                        pass
                elif entry["vt_report"] is None:
                    pass
                    
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except Exception as e:
                print(f"An Exception occured while scanning {key}: {e}")
    
    except KeyboardInterrupt:
        # allow user to terminate whenever
        print("\nKeyboard Interrupt Received")
    except Exception as e:
        print(f"An Exception occured while scanning packages: {e}")
    finally:
        # store results
        print(f"Writing results to {RESULTS_FILE}")
        with open(RESULTS_FILE, 'w') as f:
            json.dump(results, f, indent=4)
        pass

    # experiments with virustotal
    # azure_hash = "f56d22acaba0ce74b821fd3d012d18854f9d0b3662d5a3a9240b1bd587c96b23"
    # file = client.get_object(f"/files/{azure_hash}")
    # print(type(file))
    # print(file)
    # print(file.get("size"))
    # print(file.get("sha256"))
    # print(file.get("type_tag"))
    # print(file.get("last_analysis_stats"))

    # url = f"https://www.virustotal.com/api/v3/files/{azure_hash}"
    # headers = {"accept": "application/json", "x-apikey": apikey}
    # response = requests.get(url, headers=headers)
    # print(response.text)

    client.close()
    # print(models)
    # print(all_packages)

if __name__ == "__main__":
    main()