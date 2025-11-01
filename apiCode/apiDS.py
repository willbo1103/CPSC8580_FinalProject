import os
import time
from openai import OpenAI

# export DEEPSEEK_API_KEY="$YOUR_API_KEY_HERE"


# Input file (prompts) and output file (responses)
INPUT_FILE = "Prompts/JSprompts.txt" # either pythonprompts or JSprompts
OUTPUT_FILE = "Responses/DSJSresponses.txt" # changes based on LLM and input file

MODEL = "deepseek-reasoner"
client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'), base_url="https://api.deepseek.com")

def main():

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        prompts = [line.strip() for line in f if line.strip()]
        print(f"Loaded {len(prompts)} prompts from {INPUT_FILE}")

        with open(OUTPUT_FILE, "a", encoding="utf-8") as out:
            for i, prompt in enumerate(prompts, start=1):
                try:
                    print(f"Sending prompt {i}/{len(prompts)}...")

                        response = client.responses.create(
                            model=MODEL,
                            input=prompt
                        )

                        reply = response.output_text.strip()

                        # log prompt + response
                        out.write(f"\nPROMPT {i}:\n{prompt}\nRESPONSE:\n{reply}\n{'-'*60}\n")

                        print(f" Got response for prompt {i}")

                        # to prevent API flooding
                        time.sleep(1.5)

                except Exception as e:
                    print(f"L Error for prompt {i}: {e}")
                    out.write(f"\nPROMPT {i} ERROR:\n{prompt}\nError: {e}\n{'-'*60}\n")

        print(f"\n Finished processing all prompts. Responses saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
