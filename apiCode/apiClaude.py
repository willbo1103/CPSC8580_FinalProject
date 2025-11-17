# before running please run:
# export ANTHROPIC_API_KEY="$YOUR_API_KEY"

import time
from anthropic import Anthropic

# Initialize the client

client = Anthropic(api_key="")

# Input file (prompts) and output file (responses)
INPUT_FILE = "Prompts/JSprompts2.txt"  # either pythonprompts or JSprompts
OUTPUT_FILE = "Responses/claudeopusJSresponses2.txt"  # changes based on LLM and input file

# model, between claude-opus-4-1 and claude-sonnet-4-5
MODEL = "claude-opus-4-1"

def main():
    # read prompts from file (either pythonprompts or JSprompts)
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        prompts = [line.strip() for line in f if line.strip()]

    print(f"Loaded {len(prompts)} prompts from {INPUT_FILE}")

    with open(OUTPUT_FILE, "a", encoding="utf-8") as out:
        for i, prompt in enumerate(prompts, start=1):
            try:
                print(f"Sending prompt {i}/{len(prompts)}...")

                # Send to Claude
                response = client.messages.create(
                    model=MODEL,
                    max_tokens=1000,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )

                # extract reply text
                reply = response.content[0].text.strip() if response.content else "(no response)"

                # log prompt + response
                out.write(f"\nPROMPT {i+250}:\n{prompt}\nRESPONSE:\n{reply}\n{'-'*60}\n")

                print(f" Got response for prompt {i}")

                # to prevent API flooding
                time.sleep(1.5)

            except Exception as e:
                print(f"L Error for prompt {i}: {e}")
                out.write(f"\nPROMPT {i+250} ERROR:\n{prompt}\nError: {e}\n{'-'*60}\n")

    print(f"\n Finished processing all prompts. Responses saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

