import os

def load_set(path, to_lower=False):
    with open(path, "r", encoding="utf-8") as f:
        if to_lower:
            return set(line.strip().lower() for line in f if line.strip())
        else:
            return [line.strip() for line in f if line.strip()]

def normalize(pkg: str) -> str:
    # make dashes and underscores the same, to avoid formatting issues
    pkg = pkg.lower()
    pkg = pkg.replace("-", "_")
    return pkg

def main():
    # paths
    parent_dir = os.path.dirname(os.path.abspath(__file__)) + "/.."
    master_path = os.path.join(os.path.dirname(__file__), "allpythonpackages.txt")
    file1_path = os.path.join(parent_dir, "claudeopusPYpackages.txt")
    output_path = os.path.join(os.path.dirname(__file__), "claudeopushalluncinations.txt")

    # load lists
    master_packages_lower = {normalize(x) for x in load_set(master_path, to_lower=False)}
    file1_packages = load_set(file1_path, to_lower=False)

    missing = []

    for pkg in file1_packages:
        normalized = normalize(pkg)

        if normalized not in master_packages_lower:
            missing.append(normalized)

    # write hallucinations to file
    with open(output_path, "w", encoding="utf-8") as f:
        for pkg in missing:
            f.write(pkg + "\n")

    print(f"Done! {len(missing)} packages not found in master written to: {output_path}")

if __name__ == "__main__":
    main()

