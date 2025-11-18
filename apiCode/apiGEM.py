# pip install -q -U google-genai
# before running please run 'export GEMINI_API_KEY=<YOUR_API_KEY>'

import time
from google import genai

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client()

# Choose model, either gemini-2.5-pro or gemini-2.5-flash
MODEL = "gemini-2.5-pro" # flash is fast, pro has more thinking

# Input file (prompts) and output file (responses)
INPUT_FILE = "Prompts/pythonprompts.txt" # either pythonprompts or JSprompts
OUTPUT_FILE = f"Responses/{MODEL}PYresponses.txt" # either PYresponses or JSresponses
ERROR_FILE = f"Responses/{MODEL}PYerror.txt"

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
                    # config=types.GenerateContentConfig(
                    #     thinking_config=types.ThinkingConfig(thinking_budget=0) # Disables thinking
                    # ),
                )

                print(f" Got response for prompt {i}")
                # print(response.usage_metadata)

                reply = response.text.strip()

                # log prompt + response
                out.write(f"\nPROMPT {i}:\n{prompt}\nRESPONSE:\n{reply}\n{'-'*60}\n")

                # to prevent API flooding
                time.sleep(1.5)
            except Exception as e:
                print(f"L Error for prompt {i}: {e}")
                # write prompt number to error file for handling later
                with open(ERROR_FILE, "a", encoding="utf-8") as stderr:
                    stderr.write(f"{i}\n")
                out.write(f"\nPROMPT {i} ERROR:\n{prompt}\nError: {e}\n{'-'*60}\n")
                time.sleep(1.5)

    print(f"\n Finished processing all prompts. Responses saved to {OUTPUT_FILE}")
    client.close()

if __name__ == "__main__":
    main()

