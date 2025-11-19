import subprocess
import sys

def main():
    outfile_name = "DSresponder_hall_checker_output.txt"

    packages = ["chat__poa",
"cocoa",
"coreaudiokit",
"coremotion",
"datadetection",
"opengl",
"portableserver",
"pyobjctools",
"_mylib",
"aliyunsdkvpc",
"ansible_changelog",
"aws_cdk",
"braket",
"brotli_wrapper",
"cprofile",
"chem_ml_module",
"colcon",
"concurrent",
"core_module",
"data_processor",
"datadog_checks",
"devpi_utils",
"django_objects_to_fixed_format",
"firebase_config",
"isl",
"metal_fx_bindings",
"migrations_manager",
"my_notebook",
"mylib_build",
"mypy_boto3_acmpca",
"mypy_boto3_database_migration_service",
"mypy_boto3_elasticinference",
"mypy_boto3_iot_events_data",
"mypy_boto3_media_store_data",
"mypy_boto3_serverlessapplicationrepository",
"mypy_boto3_ssoadmin",
"mypy_boto3_wafregional",
"notebook_data_lib",
"objc",
"ocient",
"openpyxl_template",
"opentelemetry",
"pagination_app",
"phase_wrapper",
"pstats",
"rest_framework",
"rust_lint",
"scalable_web_app_stack",
"sqlqueryengine",
"stardog",
"tencentcloud",
"type_annotations",
"xml",
"your_etl_module",
"your_main_file",
"yrs",
"zeo_client",
"zeo_server",
"{package_name}"]

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