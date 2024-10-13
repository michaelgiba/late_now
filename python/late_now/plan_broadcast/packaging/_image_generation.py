from late_now.plan_broadcast._types import ShowSegment, ResourceStagingArea
from diffusers import DiffusionPipeline
import torch
from functools import cache
from late_now.llm_util import prompt_general_llm

# Can be set to 1~50 steps. LCM support fast inference even <= 4 steps. Recommend: 1~8 steps.
NUM_INFERENCE_STEPS = 8


@cache
def _get_model_pipe():
    pipe = DiffusionPipeline.from_pretrained("SimianLuo/LCM_Dreamshaper_v7")
    # To save GPU memory, torch.float16 can be used, but it may compromise image quality.
    pipe.to(torch_device="cuda", torch_dtype=torch.float32)
    return pipe


def _image_prompt_from_source_material(source_material: str) -> str:
    return f"""
    Given the following source material, generate a description of an image which 
    would accompany this article. Use no more than 5 words and say nothing else.

    Source Material: {source_material}"""


def image_for_segment(segment: ShowSegment, staging_area: ResourceStagingArea):
    pipe = _get_model_pipe()
    llm_prompt_for_image_prompt = _image_prompt_from_source_material(
        segment.source_material
    )
    image_prompt = prompt_general_llm(llm_prompt_for_image_prompt)
    image_prompt = (
        f"vibrant, Hilarious, cartoonish, funny image of {image_prompt!r}, 8k"
    )
    images = pipe(
        prompt=image_prompt,
        num_inference_steps=NUM_INFERENCE_STEPS,
        guidance_scale=0,
        lcm_origin_steps=50,
    ).images
    image_path = staging_area.image_path(ext="png")
    images[0].save(image_path)
    return image_path
