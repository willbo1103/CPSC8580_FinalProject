import importlib
import subprocess
import sys
import platform

# macOS frameworks (PyObjC)
MACOS_FRAMEWORKS = {
    "cocoa", "coreaudiokit", "coremotion",
    "datadetection", "discrecordingui", "pyobjctools", "objc"
}

# pip name aliases (pip_name → import_name mismatch)
PIP_ALIAS = {
    "aws_cdk": "aws-cdk-lib",
    "OpenGL": "PyOpenGL",
}

# Python built-ins
BUILTINS = {"concurrent", "cProfile", "pstats"}



# files
HALL_FILE = "../gemini-2.5-flashhalluncinations.txt" 
# RESP_FILE = "../../../gemini-2.5-flashPYpackages.txt"
RESP_FILE = "../../../../Responses/gemini-2.5-flashPYresponses.txt"
OUTFILE = "gemini_hall_output.txt"

def parse_import(line):
    """
    Takes a line like:
        'from numpy import array'
        'import openjpeg'
    Returns: (module, attribute)
    """
    line = line.strip()

    if line.startswith("from "):
        # from X import Y
        parts = line.split()
        module = parts[1]
        # Handle: from X import A, B, C
        if "," in line:
            attribute = parts[3].split(",")[0]
        else:
            attribute = parts[3]
        return module, attribute

    elif line.startswith("import "):
        # import X or import X as Y
        parts = line.split()
        module = parts[1]
        # Drop trailing comma if present
        module = module.replace(",", "")
        return module, None

    return None, None

def test_hallucination(module, attribute):
    """
    Returns: (classification_string, extra_info_string)
    """

    # ------------ CASE 0: Built-ins ------------
    if module in BUILTINS:
        return "REAL (built-in)", ""

    # ------------ CASE 1: Direct import works ------------
    try:
        mod = importlib.import_module(module)
        import_success = True
    except ImportError:
        import_success = False

    # If direct import worked, check attribute
    if import_success:
        if attribute is None:
            return "REAL (importable module)", ""
        else:
            try:
                getattr(mod, attribute)
                return "REAL (module + attribute)", ""
            except:
                return "SUBMODULE/ATTRIBUTE HALLUCINATION", ""

    # ------------ CASE 2: macOS framework ------------
    if module.lower() in MACOS_FRAMEWORKS:
        if platform.system() == "Darwin":
            return "MACOS FRAMEWORK (PyObjC may be missing)", ""
        else:
            return "MACOS-ONLY FRAMEWORK (hallucinated on this platform)", ""

    # ------------ CASE 3: Pip install attempt ------------
    pip_name = PIP_ALIAS.get(module, module)

    pip_try = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--dry-run", pip_name],
        capture_output=True, text=True
    )

    if pip_try.returncode == 0:
        # pip package exists → retry import
        try:
            mod = importlib.import_module(module)
            if attribute is None:
                return "REAL (pip-installable)", ""
            try:
                getattr(mod, attribute)
                return "REAL (pip-installable + attribute)", ""
            except:
                return "ATTRIBUTE HALLUCINATION (pip pkg exists)", ""
        except:
            return "IMPORT ERROR after pip install attempt", pip_try.stderr

    # ------------ CASE 4: Nothing worked → hallucinated ------------
    return "HALLUCINATED", ""

def main():
    
    hall_list = []
    to_try = []
    previous_word = None 

    # make a list of every hallucinated package
    with open(HALL_FILE, "r", encoding="utf-8") as hall_file:
        hall_list = [line.strip().lower() for line in hall_file if line.strip()]

    with open(RESP_FILE, "r", encoding="utf-8") as resp_file:

        # strip lines in resp file
        for line in resp_file:
            line_stripped = line.strip()

            # only consider lines with import stmt
            if not ("import" in line_stripped):
                continue
            
            # ok, now we have a line with import stmt; need to tokenize line

            words = line_stripped.replace(",", " ").split()

            for word in words:
                if word.lower() in hall_list:
                    if f"import {word.lower()}" in line_stripped.lower() or f"from {word.lower()}" in line_stripped.lower():
                        to_try.append(line_stripped)
    
    # remove duplicates
    to_try = list(set(to_try))

    # test each import and write outfile

    with open(OUTFILE, "w", encoding="utf-8") as out:
        for line in to_try:
            module, attribute = parse_import(line)

            # Skip malformed lines (module = None)
            if module is None:
                out.write(f"SKIPPED (cannot parse): {line}\n\n")
                continue

            classification, extra = test_hallucination(module, attribute)

            out.write(f"LINE: {line}\n")
            out.write(f"  module     : {module}\n")
            out.write(f"  attribute  : {attribute}\n")
            out.write(f"  result     : {classification}\n")
            if extra:
                out.write(f"  extra      : {extra}\n")
            out.write("\n----------------------------------------\n\n")

    print(f"\n Finished processing all prompts. Responses saved to {OUTFILE}")

if __name__ == "__main__":
    main()