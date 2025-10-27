# pip install -q -U google-genai
# before running please run 'export GEMINI_API_KEY="$YOURAPIKEY"'

import time
from google import genai
from google.genai import types

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client()

# Choose model
MODEL = "gemini-2.5-flash" # flash is fast, pro has more thinking

# Input file (prompts) and output file (responses)
INPUT_FILE = "Prompts/pythonprompts.txt" # either pythonprompts or JSprompts
OUTPUT_FILE = f"Responses/{MODEL}PYresponses.txt" # either PYresponses or JSresponses

def main():
    # read prompts from file (either pythonprompts or JSprompts)
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        prompts = [line.strip() for line in f if line.strip()]

    print(f"Loaded {len(prompts)} prompts from {INPUT_FILE}")

    with open(OUTPUT_FILE, "a", encoding="utf-8") as out:
        print(f"Saving responses to {OUTPUT_FILE}")
        time.sleep(2)

        for i, prompt in enumerate(prompts, start=1):
            try:
                print(f"¡ Sending prompt {i}/{len(prompts)}...")

                response = client.models.generate_content(
                    model=MODEL, 
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        thinking_config=types.ThinkingConfig(thinking_budget=0) # Disables thinking
                    ),
                )

                reply = response.text.strip()

                # log prompt + response
                out.write(f"\nPROMPT {i}:\n{prompt}\nRESPONSE:\n{reply}\n{'-'*60}\n")

                print(f" Got response for prompt {i}")

                # to prevent API flooding
                time.sleep(5)

            except Exception as e:
                print(f"L Error for prompt {i}: {e}")
                out.write(f"\nPROMPT {i} ERROR:\n{prompt}\nError: {e}\n{'-'*60}\n")

    print(f"\n Finished processing all prompts. Responses saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

