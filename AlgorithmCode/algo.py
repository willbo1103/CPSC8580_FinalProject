import re
import argparse
import os
import sys

# Sample call:
# python3 algo.py --input LLM_LYPY.json --output pythonprompts.txt
# python3 algo.py --input LLM_LYJS.json --output JSprompts.txt

# list of incentivized phrases/words
TARGET_PHRASES = [
    "Project structure",
    "Tech stack",
    "Step by step",
    "Starter Code",
    "Include styling suggestions",
    "Basics",
    "Template",
    "Structured plan",
    "Suggest alternatives",
    "Code segments",
    "Qualifying questions",
    "Locally",
    "Mock webpage",
    "Generate features",
    "Skeleton code",
    "Generate ideas",
    "Base code",
    "Help me plan",
    "Connect GUI",
    "Stage per clock cycle",
    "Highlight hazards",
    "Design process",
    "List of resources",
    "Tutorial",
    "Iteration",
    "Explain in detail",
    "Format",
    "Pseudocode",
    "Basic code structure",
    "Generate",
    "Create",
    "Creates",
    "Function",
    "Functions",
    "Data",
    "Client",
    "Clients",
    "Request",
    "Requests",
    "Framework",
    "Frameworks",
    "Script",
    "Scripts",
    "Example",
    "Examples",
    "Module",
    "Modules",
    "Library"
]

# compile regex for faster matching
escaped_phrases = [re.escape(p.lower()) for p in TARGET_PHRASES]
target_pattern = re.compile('|'.join(escaped_phrases), flags=re.IGNORECASE)


def score_line(line: str) -> float:
    stripped = line.strip()
    if not stripped:
        return 0.0

    # skip any line that has multiple prompts (cleaning data)
    if "\\n2." in stripped:
        return 0.0

    line_lower = stripped.lower()

    # skip unhelpful entries (it still contains the prompt they gave that helped them make the samples???)
    if line_lower.startswith("\"sure, here"):
        return 0.0

    score = 0.0

    # reward short and to the point prompts
    score += 2000.0 / len(stripped)

    # per-phrase bonuses
    matches = target_pattern.findall(line_lower)
    score += len(matches) * 25.0

    return score


def rank_json_lines(filename="LLM_LY.json", top_n=500, output_file="pythonprompts.txt"):
    samples_dir = "Samples"
    os.makedirs(samples_dir, exist_ok=True)

    input_path = os.path.join(samples_dir, filename)
    output_path = os.path.join(samples_dir, output_file)

    if not os.path.isfile(input_path):
        print(f"L ERROR: Input file not found: {input_path}", file=sys.stderr)
        return

    scores = []

    with open(input_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            score = score_line(line)
            if score > 0:
                scores.append((score, i + 1, line.strip()))

    # sort by score descending
    scores.sort(reverse=True, key=lambda x: x[0])

    # write top results
    with open(output_path, 'w', encoding='utf-8') as out:
        for score, line_num, content in scores[:top_n]:
            out.write(f"{content}\n")

    print(f" Top {min(top_n, len(scores))} lines written to '{output_path}'")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rank JSON lines by keyword presence")
    parser.add_argument("--input", "-i", type=str, required=True, help="Input JSON file (inside Samples/)")
    parser.add_argument("--output", "-o", type=str, required=True, help="Output text file (saved in Samples/)")
    parser.add_argument("--top", "-t", type=int, default=500, help="Number of top lines to save")
    args = parser.parse_args()

    rank_json_lines(filename=args.input, top_n=args.top, output_file=args.output)
