import os
import time
from openai import OpenAI

# export COPILOT_API_KEY="sk-your-deepseek-key"

endpoint = "https://cpsc8580.openai.azure.com/openai/v1/"
deployment_name = "CPSC8580-gpt-4o-mini"


INPUT_FILE = "Prompts/JSprompts.txt" # either pythonprompts or JSprompts
OUTPUT_FILE = "Responses/azureresponsesJS2.txt"

MODEL= "gpt-4o-mini"
client = OpenAI(
    base_url=endpoint,
    api_key=os.environ.get("COPILOT_API_KEY")
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
                #print(f"Sending prompt {i}/{len(prompts)}...")
                print(f"Sending prompt {i+250}/{len(prompts)}...")


                response = client.chat.completions.create(
                    model=MODEL,
                    messages=[{"role": "user", "content": prompt}]
                )

                reply = response.choices[0].message.content.strip()

                #out.write(f"\nPROMPT {i}:\n{prompt}\nRESPONSE:\n{reply}\n{'-'*60}\n")
                out.write(f"\nPROMPT {i+250}:\n{prompt}\nRESPONSE:\n{reply}\n{'-'*60}\n")
                #print(f"Got response for prompt {i}")
                print(f"Got response for prompt {i+250}")

                time.sleep(1.5)  # prevent rate limiting

            except Exception as e:
                #print(f"L Error for prompt {i}: {e}")
                print(f"L Error for prompt {i+250}: {e}")
                #out.write(f"\nPROMPT {i} ERROR:\n{prompt}\nError: {e}\n{'-'*60}\n")
                out.write(f"\nPROMPT {i+250} ERROR:\n{prompt}\nError: {e}\n{'-'*60}\n")

    print(f"\nFinished processing all prompts. Responses saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

'''
completion = client.chat.completions.create(
    model=deployment_name,
    messages=[
        {
            "role": "user",
            "content": "What is the capital of France?",
        }
    ],
)

print(completion.choices[0].message)
'''
