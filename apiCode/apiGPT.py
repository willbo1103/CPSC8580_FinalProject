# before running please run 'export OPENAI_API_KEY="$YOURAPIKEY"'


from openai import OpenAI
client = OpenAI()

response = client.responses.create(
    model="gpt-4.1", # either 5 or 4.1 is fine
    input="Generate Python code that implements a simple web server that can handle GET and POST requests using the http.server module."
)

print(response.output_text)
