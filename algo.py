import re
import argparse

# Sample call: python3 algo.py --input LLM_LYPY.json --output pythonprompts.txt
# JS Call: python3 algo.py --input LLM_LYJS.json --output JSprompts.txt


def score_line(line: str) -> float:
    """Score a single JSON line."""
    stripped = line.strip()
    line_lower = stripped.lower()

    # present because some lines are just chatGPT prompts, for some reason
    if line_lower.startswith("\"sure, here"):
        return 0.0

    # checks to see a library/module is specified
    if re.search(r'\blibrary\b', line_lower) or \
       re.search(r'\bmodule\b', line_lower) or \
       re.search(r'\bmodules\b', line_lower):
        score = 10  # flat 10 points if any keyphrase appears
    else:
        score = 0

    # rewards shorter and more to the point prompts, reflecting the study
    if len(stripped) > 0:
        score += 1000 / len(stripped)

    return score

def rank_json_lines(filename="LLM_LY.json", top_n=500, output_file="pythonprompts.txt"):
    """Parse JSON file and write the top lines to a text file."""
    scores = []

    with open(filename, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            score = score_line(line)
            if score > 0:  # only include scored lines
                scores.append((score, i + 1, line.strip()))

    # sort by score descending
    scores.sort(reverse=True, key=lambda x: x[0])

    # write top results to file
    with open(output_file, 'w', encoding='utf-8') as out:
        out.write(f"Top {top_n} lines by score\n")
        out.write("-" * 50 + "\n")
        for score, line_num, content in scores[:top_n]:
            out.write(f"{content}\n")

    print(f" Top {top_n} lines written to '{output_file}'")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rank JSON lines by keyword presence")
    parser.add_argument("--input", "-i", type=str, required=True, help="Input JSON file")
    parser.add_argument("--output", "-o", type=str, required=True, help="Output text file")
    parser.add_argument("--top", "-t", type=int, default=500, help="Number of top lines to save")
    args = parser.parse_args()

    rank_json_lines(filename=args.input, top_n=args.top, output_file=args.output)


