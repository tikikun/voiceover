from mlx_lm.utils import load, generate
from voiceover.sample import sample_guide_prompt,sample_content

def generate_transcript(
    repo="mlx-community/Qwen2.5-Coder-7B-Instruct-4bit",
    content=None,
    guide_prompt= sample_guide_prompt,
    verbose=True,
    max_tokens=10000,
    top_p=0.8,
    temp=0,
):
    # Load model and tokenizer with specified repository and configuration.
    model, tokenizer = load(repo, tokenizer_config={"eos_token": "<|endoftext|>", "trust_remote_code": True})
    
    # Ensure that content is provided; otherwise, raise an error.
    if content is None:
        raise ValueError("Content cannot be None.")
        
    # Construct the full prompt using the guide_prompt and content.
    full_prompt = f"{guide_prompt}\n\n-----------\n{content}"
    
    # Prepare messages format required by the chat template.
    messages = [{"role": "user", "content": full_prompt}]
    
    # Apply chat template to prepare final input prompt.
    formatted_prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    
    # Generate response from the model based on the prepared prompt.
    response = generate(
        model=model,
        tokenizer=tokenizer,
        prompt=formatted_prompt,
        verbose=verbose,
        max_tokens=max_tokens,
        top_p=top_p,
        temp=temp,
    )
    
    return response


# Example usage
if __name__ == "__main__":
    content = sample_content
    response = generate_transcript(content=content)
    print(response)
