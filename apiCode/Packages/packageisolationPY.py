import re

def extract_packages(input_file: str, output_file: str):
    packages = set()

    # regex patterns
    import_pattern = re.compile(r"^\s*import\s+(.+)")
    from_pattern = re.compile(r"^\s*from\s+([a-zA-Z0-9_\.]+)\s+import")

    with open(input_file, "r", encoding="utf-8") as infile:
        for line in infile:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            # handle "from <pkg> import ..."
            m = from_pattern.match(line)
            if m:
                full_path = m.group(1)
                top_level = full_path.split(".")[0]
                packages.add(top_level)
                continue

            # handle "import x, y.z, a.b.c"
            m = import_pattern.match(line)
            if m:
                items = m.group(1)
                # split by comma
                parts = [p.strip() for p in items.split(",")]
                for p in parts:
                    # handle things like "x.y.z as q"
                    p = p.split()[0]               # drop alias
                    top_level = p.split(".")[0]    # keep pkg only
                    packages.add(top_level)
                continue

    # write unique top-level package names
    with open(output_file, "w", encoding="utf-8") as outfile:
        for pkg in sorted(packages):
            outfile.write(pkg + "\n")

    print(f"Extracted {len(packages)} unique packages from {output_file}")


# call the function
extract_packages("../Responses/gpt5PYresponses.txt",
                 "gpt5PYpackages.txt")


