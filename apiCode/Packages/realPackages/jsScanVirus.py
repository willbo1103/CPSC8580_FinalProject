# get list of npm packages
# run list of npm packages through VirusTotal API
# virustotal uses the sha256 or sha1 of the file uploaded as its identifier

# before running run 'export VIRUSTOTAL_API_KEY=<My-API-Key>'
# you will probably need to change the RESULTS_FILE location or do 'mkdir local'
# you will probably need to run 'pip install vt-py' for virustotal

# IF YOU DO_PACKAGE_LOOKUP after DO_VIRUS_SCAN, IT MAY OVERWRITE SCAN RESULTS

import os
import sys
import requests
import json
import hashlib
import time
import vt # pip install vt-py
from typing import Dict, Optional

DO_PACKAGE_LOOKUP = False
DO_VIRUS_SCAN = True

DIRECTORY = "./JS"
RESULTS_FILE = "JSurls.json" # stores package urls and scan results as json
DOWNLOAD_FOLDER = "local" # folder downloads are temporarily stored (these may not always get deleted correctly)

# before running, do 'export VIRUSTOTAL_API_KEY=<My-API-Key>' in terminal
if DO_VIRUS_SCAN:
    apikey = os.environ.get('VIRUSTOTAL_API_KEY')
    if apikey is None:
        print("Error: API key 'VIRUSTOTAL_API_KEY' does not exist")
        exit()

# find package download url and sha1 hash for it
# look for source if it exists, and return top url if it doesn't
# returns list with entries containing url and sha1 hash
def get_package_url(package_name : str):

    retval: Dict[str, Optional[str]] = {"url": None, "sha1": None, "error": None, "virustotal": None}
    try:

        # Make a request to the npm JSON API for the package
        response = requests.get(f"https://registry.npmjs.org/{package_name}/latest")

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()

            # dump for reading
            # with open(f"local/JS_{package_name}.json", 'w') as f:
            #     json.dump(data, f, indent=4)

            # Extract the URL(s) for the latest version of the package
            urls = data.get('dist', {})

            retval["url"] = urls.get("tarball", {})
            retval["sha1"] = urls.get("shasum", {})
            if len(urls) == 0:
                print(f"Error: No url found for package '{package_name}'.")
                retval["error"] = "no releases"
            return retval
        
        else:
            print(f"Error: Failed to fetch data for '{package_name}', status code {response.status_code}.")
            retval["error"] = f"HTTP ERROR {response.status_code}"
            return retval
    except Exception as e:
        print(f"Error: An exception occurred while fetching data for '{package_name}': {e}")
        retval["error"] = "other"
        return retval


def download_file(download_url : str, sha1 : str, local_filepath : str):   
    # download file and create sha1 hash
    hasher = hashlib.sha1()
    try:
        with requests.get(download_url, stream=True) as r:
            r.raise_for_status()

            with open(local_filepath, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        hasher.update(chunk)
        # check hash
        if sha1 == hasher.hexdigest():
            print("Done")
        else:
            print("Error: Hashes don't match")
            raise ValueError("Hashes of files do not match")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred during download: {e}")
        if os.path.exists(local_filepath):
            os.remove(local_filepath)
        return None
    except Exception as e:
        print(f"An error occurred during download: {e}")
        return None


# downloads file from PyPI, then uploads to virustotal for scanning
# returns dict with relevant virustotal scan results
def vt_download_and_scan_file(download_url : str, sha1 : str):
    # download_url = "https://files.pythonhosted.org/packages/87/45/89d90a0c6d5cb5cffb5d8591741f27a8ef406f631e41d1273121e54c64ff/chemlib-2.2.4.tar.gz"
    filename = download_url.split('/').pop()
    local_filepath = os.path.join(DOWNLOAD_FOLDER, filename)
    hasher = hashlib.sha1()

    # use file if it's on disk
    if os.path.exists(local_filepath):
        with open(local_filepath, 'rb') as f:
            chunk = 0
            while chunk != b'':
                chunk = f.read(65536) 
                hasher.update(chunk)
    
    # download if not on disk
    if not os.path.exists(local_filepath) or sha1 != hasher.hexdigest():
        print(f"Downloading {filename}... ", end="")
        download_file(download_url, sha1, local_filepath)
        
    # unsure if this is needed
    if os.path.getsize(local_filepath) >= 32*1024*1024: # 32 MB
        os.remove(local_filepath)
        return {"error": "FileTooBig"}

    # upload to virustotal
    print(f"Uploading file for analysis...")
    try:
        with vt.Client(apikey) as client: # type: ignore
            with open(local_filepath, 'rb') as f:
                analysis = client.scan_file(f, wait_for_completion=True)
                
            vtdict = analysis.to_dict()
            vtdict = vtdict.get("attributes", {})
            retval = {}
            retval["size"] = os.path.getsize(local_filepath)
            retval["name"] = filename
            retval["error"] = vtdict.get("bundle_info", {}).get("error", None)
            retval["last_analysis_stats"] = vtdict.get("stats", None)
            # with open('local/vtanalysis.json', 'w') as f:
            #     json.dump(analysis.to_dict(), f, indent=4)
            if os.path.exists(local_filepath):
                os.remove(local_filepath)
            return retval

    except vt.APIError as e:
        # https://docs.virustotal.com/reference/errors
        if os.path.exists(local_filepath):
                os.remove(local_filepath)
        return {"error": e.code}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    if os.path.exists(local_filepath):
            os.remove(local_filepath)


# scan file and return dict with fields
# virus: True, False
# returns dict with relevant virustotal scan results
def get_vt_report(hash : str):
    try:
        with vt.Client(apikey) as client: # type: ignore
            file = client.get_object(f"/files/{hash}")
    except vt.APIError as e:
        # https://docs.virustotal.com/reference/errors
        raise e
            
    vtdict = file.to_dict()     
    del vtdict["attributes"]["last_analysis_results"]
    vtdict = vtdict["attributes"]

    # with open("local/nbformat_vt.json", 'r') as f:
    #     vtdict = json.load(f)
    #     vtdict = vtdict["attributes"]
    
    retval = {}
    retval["last_submission_date"] = vtdict.get("last_submission_date", None)
    retval["last_modification_date"] = vtdict.get("last_modification_date", None)
    retval["size"] = vtdict.get("size", None)
    retval["name"] = vtdict.get("meaningful_name", None)
    retval["error"] = vtdict.get("bundle_info", {}).get("error", None)
    retval["total_votes"] = vtdict.get("total_votes")
    retval["last_analysis_statsst"] = vtdict.get("last_analysis_stats")
    return retval


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
                # elif package in results.keys() and results[package]["url"] != "HTTP ERROR 404":
                #     print(f"Searching again for {package}...")
                #     results[package] = get_package_url(package)
                #     pass
                if results[package]["error"] == "HTTP ERROR 404" and package.startswith("node:"):
                    results[package]["error"] = "node.js"


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

    # vt_download_and_scan_file("https://files.pythonhosted.org/packages/a2/8c/58f469717fa48465e4a50c014a0400602d3c437d7c0c468e17ada824da3a/certifi-2025.11.12.tar.gz", "d8ab5478f2ecd78af242878415affce761ca6bc54a22a27e026d7c25357c3316")

    if not DO_VIRUS_SCAN: 
        print("Skipping Virus Scan")
        exit()
    else:
        print("Doing Virus Scan")

    # response = get_vt_report(results["nbformat"]["sha1"])
    # with open("local/nbformat_vt.json", 'w') as f:
    #     json.dump(response, f, indent=4)
    # client.close()
    # exit()
    
    # run scan for everything in results
    try:
        for key, entry in results.items():
            try:
                lastscan = entry.get("virustotal", None)
                if lastscan is None or lastscan.get("error", None) in ["NotFoundError", "QuotaExceededError"]:
                    if entry["sha1"] is not None:
                        # if link has a sha1, it was found
                        print(f"Getting file report for {key}")
                        entry["virustotal"] = get_vt_report(entry["sha1"])
                        results.update({key:entry})
                        time.sleep(1)
                        pass
                    else:
                        # write nothing but note we scanned this item
                        print(f"Skipping analyzing {key}")
                        # entry["vt_report"] = None
                        # results.update({key:entry})
                        pass
                    
            except KeyboardInterrupt:
                raise
            except vt.APIError as e:
                time.sleep(1)
                if e.code == "NotFoundError":
                    entry["virustotal"] = vt_download_and_scan_file(entry["url"], entry["sha1"])
                    results.update({key:entry})
                    # stop process if get error in list
                    # if len(entry["virustotal"]) < 2 or entry["virustotal"].get("error", "") in ["FileTooBig"]:
                    # if entry["virustotal"].get("error", "") in [None, "FileTooBig"]:
                        # raise
                else:
                    raise
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
    # print(file.get("sha1"))
    # print(file.get("type_tag"))
    # print(file.get("last_analysis_stats"))

    # url = f"https://www.virustotal.com/api/v3/files/{azure_hash}"
    # headers = {"accept": "application/json", "x-apikey": apikey}
    # response = requests.get(url, headers=headers)
    # print(response.text)

    # print(models)
    # print(all_packages)

if __name__ == "__main__":
    main()