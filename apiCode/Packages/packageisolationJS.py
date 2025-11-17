import re

def extract_js_packages(input_file, output_file):
    packages = set()

    # regex patterns for ES imports and require()
    import_pattern = re.compile(r"""import\s+(?:[\s\S]+?\s+from\s+)?['"]([^'"]+)['"]""")
    require_pattern = re.compile(r"""require\s*\(\s*['"]([^'"]+)['"]\s*\)""")

    def get_top_level(pkg: str) -> str:
        # skip relative imports
        if pkg.startswith(('.', '/')):
            return None

        # scoped packages: @scope/name/subpath
        if pkg.startswith("@"):
            parts = pkg.split("/")
            if len(parts) >= 2:
                return f"{parts[0]}/{parts[1]}"
            return pkg  # rare, but valid case

        # non-scoped: take first / segment
        return pkg.split("/")[0]

    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()

            # skip blank lines and comment lines
            if not line or line.startswith("#"):
                continue

            imports = import_pattern.findall(line)
            requires = require_pattern.findall(line)

            for pkg in imports + requires:
                top = get_top_level(pkg)
                if not top:
                    continue

                # ignore any packages starting with "$"
                if top.startswith("$"):
                    continue

                packages.add(top)

    # write output
    with open(output_file, 'w', encoding='utf-8') as f:
        if packages:
            for p in sorted(packages):
                f.write(f"{p}\n")
        else:
            f.write("No packages found.\n")

    print(f"{len(packages)} top-level packages written to {output_file}")


# function call
extract_js_packages("../Responses/azure5nanoresponsesJS.txt", "azure5nanoJSpackages.txt")

