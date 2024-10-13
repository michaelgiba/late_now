# Use a pipeline as a high-level helper
from transformers import pipeline
import gc
import torch


def _load_model():
    pipe = pipeline(
        "text-generation",
        model="PrunaAI/IlyaGusev-gemma-2-9b-it-abliterated-bnb-4bit-smashed",
        device_map="auto",
    )
    return pipe


def _build_prompt_with_system(prompt, system_prompt) -> str:
    return f"""
    {system_prompt}
    
    User prompt: {prompt}
    """


def completion(prompt: str, system_prompt: str, temperature: float) -> str:
    model = _load_model()
    passed_prompt = _build_prompt_with_system(prompt, system_prompt)
    if len(passed_prompt) > 5000:
        print("WARNING: Had to truncate the prompt to get it into memory.")
        print(passed_prompt)

    result = model(
        [
            {"role": "user", "content": passed_prompt[:5000]},
        ],
        temperature=temperature,
        max_new_tokens=1024,
        do_sample=True,
    )
    raw_result = result[0]["generated_text"][-1]["content"]
    del model
    torch.cuda.empty_cache()
    gc.collect()
    return {"choices": [{"message": {"content": raw_result}}]}
