from ollama import OpenAI

# To use Ollama, ensure you have the Ollama server running locally
# You can start the Ollama server with: ollama serve --model llama3.2:1b
# The base_url should point to the local Ollama REST endpoint

client = OpenAI(
    base_url="http://10.0.0.209:11434/v1",  # The local Ollama REST endpoint
    api_key="dummy",  # Required to instantiate OpenAI client, it can be a random string
)

response = client.chat.completions.create(
    model="llama3.2:latest",
    messages=[
        {"role": "system", "content": "You are a science teacher."},
        {"role": "user", "content": "Why is the sky blue?"},
    ],
)
