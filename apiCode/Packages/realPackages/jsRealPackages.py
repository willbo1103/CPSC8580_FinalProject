import os
# derived from its opposite
def load_set(path, to_lower=False):
    with open(path, "r", encoding="utf-8") as f:
        if to_lower:
            return set(line.strip().lower() for line in f if line.strip())
        else:
            return [line.strip() for line in f if line.strip()]

def main():
    # paths
    parent_dir = os.path.dirname(os.path.abspath(__file__)) + "/.."
    master_path = os.path.join(parent_dir, "Hallucinations", "allJSpackages.txt")
    file1_path = os.path.join(parent_dir, "gpt5JSpackages.txt")
    output_path = os.path.join(os.path.dirname(__file__), "JS", "gpt5.txt")

    # load lists
    master_packages = load_set(master_path, to_lower=False)
    file1_packages = load_set(file1_path, to_lower=False)

    shared = []

    for pkg in file1_packages:
        if pkg in master_packages:
            shared.append(pkg)

    # write shared packages to file
    with open(output_path, "w", encoding="utf-8") as f:
        for pkg in shared:
            f.write(pkg + "\n")

    print(f"Done! {len(shared)} shared packages written to: {output_path}")

if __name__ == "__main__":
    main()

