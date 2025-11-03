import os
import time
from openai import OpenAI

# Make sure you've run in your shell before executing:
# export DEEPSEEK_API_KEY="sk-your-deepseek-key"

INPUT_FILE = "Prompts/pythonprompts.txt"
OUTPUT_FILE = "Responses/deepseek3responsesPY2.txt"

MODEL = "deepseek-chat"
client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        all_prompts = [line.strip() for line in f if line.strip()]
        #prompts = all_prompts[:250]  # Use only the first 250 prompts
        prompts = all_prompts[250:500]  # Use only the 251-500 prompts
        #prompts = [line.strip() for line in f if line.strip()]
        print(f"Loaded {len(prompts)} prompts from {INPUT_FILE}")

    with open(OUTPUT_FILE, "a", encoding="utf-8") as out:
        for i, prompt in enumerate(prompts, start=1):
            try:
                print(f"Sending prompt {i+250}/{len(prompts)}...")

                response = client.chat.completions.create(
                    model=MODEL,
                    messages=[{"role": "user", "content": prompt}]
                )

                reply = response.choices[0].message.content.strip()

                out.write(f"\nPROMPT {i+250}:\n{prompt}\nRESPONSE:\n{reply}\n{'-'*60}\n")
                print(f"Got response for prompt {i+250}")

                time.sleep(1.5)  # prevent rate limiting

            except Exception as e:
                print(f"L Error for prompt {i+250}: {e}")
                out.write(f"\nPROMPT {i+250} ERROR:\n{prompt}\nError: {e}\n{'-'*60}\n")

    print(f"\nFinished processing all prompts. Responses saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()