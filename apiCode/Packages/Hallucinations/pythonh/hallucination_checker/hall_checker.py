import subprocess
import sys

def main():
    outfile_name = "Azuremini_hall_checker_output.txt"

    packages = ["asgi",
"boto3_guardduty",
"datadog_lambda_construct",
"dataworld",
"execjs",
"hanaclient",
"kinetica",
"my_construct",
"my_pybind11_module",
"my_stack",
"mylib_wrapper",
"mypy_boto3_autoscalingplans",
"mypy_boto3_code_star_connections",
"mypy_boto3_location_service",
"mypy_boto3_mediainfo",
"mypy_boto3_rdsdataservice",
"mypy_boto3_resourcegroups",
"mypy_boto3_resourcetagging",
"vmware",
"years",
"yogadata"]

    with open(outfile_name, "w") as outfile:
        #run command pip install package
        for package in packages:
            result = subprocess.run(["pip", "install", package],capture_output = True, text = True)
            # SUCCESS → write stdout
            if result.returncode == 0:
                outfile.write(f"\n--- SUCCESS: {package} ---\n")
                outfile.write(result.stdout)

            # FAILURE → write stderr
            else:
                outfile.write(f"\n--- FAILURE: {package} ---\n")
                outfile.write(result.stderr)

if __name__ == "__main__":
    main()