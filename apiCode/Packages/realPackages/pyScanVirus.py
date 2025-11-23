# get list of pypi packages (mostly working except those with multiple names)
# run list of pypi packages through VirusTotal API
import os
import sys
import requests
import json
# from packaging.version import parse as parse_version


import random
random.seed()

DIRECTORY = "./Python"
URL_FILE = "local/PYurls.json" # stores results as json

def get_package_url(package_name : str):
    """
    Fetch the PyPI metadata for a given package and return the download URL for the latest release.
    """
    try:
        # Make a request to the PyPI JSON API for the package
        response = requests.get(f'https://pypi.org/pypi/{package_name}/json')

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()

            # dump for reading
            # with open(f"local/dumps/{package_name}.json", 'w') as f:
            #     json.dump(data, f, indent=4)

            # Extract the URL for the latest version of the package
            urls = data.get('urls', {})
            link = urls[0]["url"]
            if link is None:
                print(f"Error: No url found for package '{package_name}'.")
                return "No url"
            else:
                return link 
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
            return f"HTTP ERROR {response.status_code}"
    except IndexError as e:
        # it appears that everything the brings up this exception has no releases
        print(f"Error: '{package_name}' appears to have no urls")
        return "No url"
    except Exception as e:
        print(f"Error: An exception occurred while fetching data for '{package_name}': {e}")
        return None


# scan file and return dict with fields
# virus: True, False
# response: api response
def scan(package : str):
    return {"virus": random.choice(seq=(True, False)), "response": {}}

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

    # load results of last scan
    if os.path.isfile(URL_FILE):
        try:
            print(f"Found results file {URL_FILE}")
            with open(URL_FILE, 'r') as f:
                results = json.load(f)
        except Exception as e:
            print(f"Error: could not parse URL_FILE: {e}")
            results = {}
    else:
        print(f"Could not find results file {URL_FILE}")
        results = {}


    # scan for package links
    # this returns a "good enough" list, but errors have to be manually fixed
    try:
        for package in unique_packages:
            # only scan if it's not in the results or stdlib
            if package in sys.stdlib_module_names:
                if package not in results.keys():
                    print(f"Package {package} in stdlib")
                results[package] = "stdlib"
            elif package not in results.keys():
                print(f"Searching for {package}...")
                results[package] = get_package_url(package)
            # elif package in results.keys() and results[package] is None:
            elif package in results.keys() and (results[package] is None or not results[package].startswith("https://")):
                # print(f"Searching again for {package}...")
                results[package] = get_package_url(package)
                # print(f"{package}")

    except KeyboardInterrupt:
        # allow user to terminate whenever
        print("\nKeyboard Interrupt Received")
    except Exception as e:
        print(f"An Exception occured while scanning packages: {e}")
    finally:
        # store results
        print(f"Writing results to {URL_FILE}")
        with open(URL_FILE, 'w') as f:
            json.dump(results, f, indent=4)
        pass


    # print(models)
    # print(all_packages)

if __name__ == "__main__":
    main()