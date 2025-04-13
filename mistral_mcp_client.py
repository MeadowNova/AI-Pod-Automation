import requests
from datetime import datetime

def get_filename_from_prompt(prompt):
    """
    Use Mistral MCP to generate a filename from a design prompt,
    following the [Theme]-[Concept]-[Variant]-[Version]-[Date].png convention.
    """
    today = datetime.now().strftime("%Y%m%d")
    version = "v1"
    ai_prompt = (
        f"Given the following design prompt: '{prompt}', extract the Theme, Concept, Variant, Version, and Date "
        f"for use in a filename formatted as [Theme]-[Concept]-[Variant]-[Version]-[Date].png. "
        f"Assume today's date is {today} and version is {version}. If any field is missing, make a reasonable guess. "
        f"Return only the filename."
    )

    url = "http://localhost:11434/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    data = {
        "model": "mistral",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that generates filenames for design assets."},
            {"role": "user", "content": ai_prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 64,
        "stream": False
    }
    response = requests.post(url, headers=headers, json=data, timeout=60)
    response.raise_for_status()
    result = response.json()
    filename = result["choices"][0]["message"]["content"].strip()
    filename = filename.replace("`", "").replace('"', "").replace("'", "")
    return filename
