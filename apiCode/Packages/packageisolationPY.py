import re

def extract_packages(input_file: str, output_file: str):
    packages = set()

    with open(input_file, "r", encoding="utf-8") as infile:
        for line in infile:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            else:
                # match "from" and "import" statements
                match = re.match(r"^(?:from|import)\s+([a-zA-Z0-9_\.]+)", line)
                if match:
                    pkg = match.group(1)  # keep full package path
                    packages.add(pkg)

    # write unique package names to output file
    with open(output_file, "w", encoding="utf-8") as outfile:
        for pkg in sorted(packages):
            outfile.write(pkg + "\n")

    print(f" Found {len(packages)} unique packages. Written to '{output_file}'.")


# call the function (create second file if needed)
extract_packages("../Responses/gpt4PYresponses.txt", "gpt4PYpackages.txt")
