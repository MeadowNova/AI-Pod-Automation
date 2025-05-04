import os
from mistral_mcp_client import get_filename_from_prompt
from agents.stable_diffusion import create_stable_diffusion_client

PROMPT = "french cat smoking a cigarette in a cafe eating michelin star salmon dish, funny, monet inspired art, vintage."
NEGATIVE_PROMPT = ""
OUTPUT_DIR = "data/designs/drafts"

# Get filename from Mistral MCP
filename = get_filename_from_prompt(PROMPT)
output_path = os.path.join(OUTPUT_DIR, filename)

# Create Stable Diffusion client
import sys
sys.path.append(os.getcwd())
import os
api_key = os.environ.get("OPENROUTER_API_KEY")
sd_client = create_stable_diffusion_client(
    use_api=True,
    api_key=api_key,
    config={"output_dir": OUTPUT_DIR}
)

# Generate image
success, result = sd_client.generate_image(
    prompt=PROMPT,
    negative_prompt=NEGATIVE_PROMPT,
    width=1024,
    height=1024,
    num_inference_steps=50,
    guidance_scale=7.5
)

if success:
    try:
        os.rename(result, output_path)
        print(f"Image generated and renamed to: {output_path}")
    except Exception as e:
        print(f"Image generated but failed to rename: {e}")
        print(f"Original path: {result}")
else:
    print(f"Image generation failed: {result}")
