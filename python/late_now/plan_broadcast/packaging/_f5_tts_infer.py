import numpy as np
import argparse
import codecs
import os
import re
from datetime import datetime
from importlib.resources import files
from pathlib import Path

import numpy as np
import soundfile as sf
import tomli
from cached_path import cached_path
from omegaconf import OmegaConf

from f5_tts.infer.utils_infer import (
    mel_spec_type,
    target_rms,
    cross_fade_duration,
    nfe_step,
    cfg_strength,
    sway_sampling_coef,
    speed,
    fix_duration,
    infer_process,
    load_model,
    load_vocoder,
    preprocess_ref_audio_text,
    remove_silence_for_generated_wav,
)
from f5_tts.model import DiT, UNetT
from functools import cache
import pkg_resources

# Constants
MODEL_NAME = "F5-TTS"
ENABLED_SPEAKERS = [
    "personal_space",
]
DEFAULT_SPEAKER = "personal_space"
REMOVE_SILENCE = False
VOCODER_NAME = "vocos"
REPO_NAME = "F5-TTS"
EXP_NAME = "F5TTS_Base"
CKPT_STEP = 1200000


@cache
def _get_voices() -> dict[str, dict[str, str]]:
    config_path = os.path.join(files("f5_tts").joinpath("infer/examples/basic"), "basic.toml")
    # Load configuration from config_path
    with open(config_path, 'rb') as f:
        config = tomli.load(f)


    voice_to_reference_data = {}
    for speaker in ENABLED_SPEAKERS:
        ref_audio = pkg_resources.resource_filename(__name__, f'resources/voice_samples/{speaker}/sample.wav')
        ref_text = open(pkg_resources.resource_filename(__name__, f'resources/voice_samples/{speaker}/transcript.txt'), "rt").read()

        voice_to_reference_data[speaker] = {"ref_audio": ref_audio, "ref_text": ref_text}

    # Process reference audio and text for each voice
    for voice_name, voice_data in voice_to_reference_data.items():
        voice_data["ref_audio"], voice_data["ref_text"] = preprocess_ref_audio_text(
            voice_data["ref_audio"], voice_data["ref_text"]
        )
    return voice_to_reference_data

@cache
def _get_model_and_vocoder():
    # Load vocoder
    vocoder = load_vocoder(
        vocoder_name=VOCODER_NAME,
        is_local=False,
        local_path="../checkpoints/vocos-mel-24khz"
    )

    # Load model configuration
    model_config_path = str(files("f5_tts").joinpath("configs/F5TTS_Base_train.yaml"))

    model_cfg = OmegaConf.load(model_config_path).model.arch

    # Load model checkpoint
    ckpt_file = str(cached_path(f"hf://SWivid/{REPO_NAME}/{EXP_NAME}/model_{CKPT_STEP}.safetensors"))

    print(f"Using {MODEL_NAME}...")

    ema_model = load_model(
        DiT, model_cfg, ckpt_file,
        mel_spec_type=VOCODER_NAME,
    )
    return ema_model, vocoder


def _generate_audio_segments(gen_text, voice_name, ema_model, vocoder):
    voices = _get_voices()
    generated_audio_segments = []
    reg1 = r"(?=\[\w+\])"
    chunks = re.split(reg1, gen_text)
    reg2 = r"\[(\w+)\]"
    final_sample_rate = None

    for text in chunks:
        if not text.strip():
            continue
        match = re.match(reg2, text)

        text = re.sub(reg2, "", text)
        ref_audio_ = voices[voice_name]["ref_audio"]
        ref_text_ = voices[voice_name]["ref_text"]
        gen_text_ = text.strip()
        if gen_text_.strip() == "":
            continue

        audio_segment, final_sample_rate, spectrogram = infer_process(
            ref_audio_,
            ref_text_,
            gen_text_,
            ema_model,
            vocoder,
            mel_spec_type=VOCODER_NAME,
            target_rms=target_rms,
            cross_fade_duration=cross_fade_duration,
            nfe_step=nfe_step,
            cfg_strength=cfg_strength,
            sway_sampling_coef=sway_sampling_coef,
            speed=speed,
            fix_duration=fix_duration,
        )
        generated_audio_segments.append(audio_segment)
    return generated_audio_segments, final_sample_rate


def audio_and_sample_rate_for_setence(sentence: str, voice: str = DEFAULT_SPEAKER) -> (np.array, float):
    model, vocoder = _get_model_and_vocoder()
    audio_segments, sample_rate = _generate_audio_segments(sentence, voice, model, vocoder)
    if audio_segments:
        final_wave = np.concatenate(audio_segments)
        return final_wave, sample_rate
    else:
        return np.array([]), sample_rate

def main():
    gen_text = "testing testing"
    final_wave, sample_rate = audio_and_sample_rate_for_setence(gen_text)
    output_file = os.path.join("./", "test.wav")
    sf.write(output_file, final_wave, sample_rate)  # Assuming a sample rate of 24000 Hz
    print(f"Audio saved to {output_file}")



if __name__ == "__main__":
    main()

