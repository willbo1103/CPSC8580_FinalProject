import re

def extract_js_packages(input_file, output_file):
    packages = set()

    # regex patterns for import and require statements
    import_pattern = re.compile(r"""import\s+(?:[\s\S]+?\s+from\s+)?['"]([^'"]+)['"]""")
    require_pattern = re.compile(r"""require\s*\(\s*['"]([^'"]+)['"]\s*\)""")

    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()

            # skip blank lines and comment lines (starting with '#')
            if not line or line.startswith("#"):
                continue

            # find matches
            imports = import_pattern.findall(line)
            requires = require_pattern.findall(line)

            for pkg in imports + requires:
                # skips relative imports (like ./ or ../)
                if not pkg.startswith(('.', '/')):
                    packages.add(pkg)

    # count unique packages
    package_count = len(packages)

    # writes results to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        if packages:
            f.write(f"Packages found ({package_count} total):\n")
            for p in sorted(packages):
                f.write(f"{p}\n")
        else:
            f.write("No packages found.\n")

    print(f" {package_count} packages written to {output_file}")


# function call, shouldnt need any changes
extract_js_packages("../Responses/gpt5JSresponses.txt", "gpt5JSpackages.txt")

