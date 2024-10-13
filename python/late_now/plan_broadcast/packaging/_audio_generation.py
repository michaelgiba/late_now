import nltk  # we'll use this to split into sentences
import numpy as np
import os
from functools import cache
from late_now.plan_broadcast._types import (
    AudioFragments,
    AudioGeneration,
    ResourceStagingArea,
    SegmentDetailedScript,
    ShowSegment,
)
from scipy.io.wavfile import write as write_wav
from transformers import AutoProcessor, BarkModel
import torchaudio
import pkg_resources

EFFECTS_TO_FILENAME = {
    "APPLAUSE": "resources/audio/sound_effects/applause/short_applause.wav",
    "LAUGHTER": [
        "resources/audio/sound_effects/laughter/laughter_medium_short.wav",
        "resources/audio/sound_effects/laughter/laughter_loud_short.wav",
        "resources/audio/sound_effects/laughter/drum_laugh.wav",
    ],
    "INTRO_MUSIC": "resources/audio/sound_effects/music/short_theme.wav",
    "CROWD_AWW": "resources/audio/sound_effects/aww/aww.wav",
    "CROWD_OOH": "resources/audio/sound_effects/ooh/ooh.wav",
}
VOICE_PRESET = "v2/en_speaker_6"


def _get_variable_silence(duration_sec: int) -> np.ndarray:
    return np.zeros(int(duration_sec * _get_sample_rate()))  # quarter second of silence


def _get_volume_fade_for_sound_effect(sound_effect: str, num_samples: int) -> np.array:
    if sound_effect in ["APPLAUSE", "LAUGHTER", "CROWD_AWW", "CROWD_OOH"]:
        return np.linspace(1, 0, num_samples)
    elif sound_effect in ["INTRO_MUSIC", "SILENCE"]:
        return np.linspace(1, 1, num_samples)
    else:
        raise ValueError()


def _get_sound_effect_data(sound_effect: str, duration: int) -> np.array:
    if sound_effect == "SILENCE":
        return _get_variable_silence(duration)

    options = EFFECTS_TO_FILENAME[sound_effect]
    if isinstance(options, list):
        file_path = pkg_resources.resource_filename(__name__, np.random.choice(options))
    else:
        file_path = pkg_resources.resource_filename(__name__, options)

    data, _ = torchaudio.load(file_path)
    data = data.squeeze().numpy()

    duration_samples = int(duration * _get_sample_rate())
    fade = _get_volume_fade_for_sound_effect(sound_effect, duration_samples)

    if len(data) > duration_samples:
        # Fade over the course of duration_samples
        data = data[:duration_samples] * fade

    elif len(data) < duration_samples:
        data = np.tile(data, duration_samples // len(data) + 1)
        data = data[:duration_samples] * fade

    return data


@cache
def _get_pad_silence() -> np.ndarray:
    return np.zeros(int(0.25 * _get_sample_rate()))  # quarter second of silence


def _get_model():
    model = BarkModel.from_pretrained("suno/bark-small").to("cuda")
    model.enable_cpu_offload()
    processor = AutoProcessor.from_pretrained("suno/bark-small")
    return processor, model


@cache
def _get_sample_rate():
    # model.generation_config.sample_rate
    return 24_000


def _generate_audio(
    processor, model, text: str, speedup: float = 1.1, gain: float = 1.3
) -> np.ndarray:
    inputs = processor(text, voice_preset=VOICE_PRESET).to("cuda")
    audio_array = model.generate(**inputs)
    audio_array = audio_array.cpu().numpy().squeeze()

    # Speed up the audio by a factor of two
    # audio_array = librosa.effects.time_stretch(audio_array, rate=speedup)
    # audio_array, _ = librosa.effects.trim(audio_array)
    # audio_array *= gain
    return audio_array


def _generate_audio_for_line(
    processor, model, text: str
) -> tuple[np.ndarray, list[tuple[str, float]]]:
    pieces = []
    sentences = nltk.sent_tokenize(text)
    sentences_and_durations = []

    for _, sentence in enumerate(sentences):
        audio_array = _generate_audio(processor, model, sentence)
        pad_silence = _get_pad_silence().copy()
        piece = [audio_array, pad_silence]
        pieces += piece
        piece_duration = (len(audio_array) + len(pad_silence)) / _get_sample_rate()
        sentences_and_durations.append((sentence, piece_duration))

    return np.concatenate(pieces), sentences_and_durations


def _soft_clip(x):
    """Applies soft clipping to the input signal."""
    return np.arctan(x)


def _walter_pause_for_sound_effect_length(
    sound_effect: float, duration_sec: str
) -> float:
    if sound_effect == "SILENCE":
        return duration_sec
    elif sound_effect == "APPLAUSE":
        return duration_sec * 0.9
    elif sound_effect == "LAUGHTER":
        return duration_sec * 0.5
    elif sound_effect == "INTRO_MUSIC":
        return duration_sec
    elif sound_effect == "CROWD_AWW":
        return duration_sec * 0.8
    elif sound_effect == "CROWD_OOH":
        return duration_sec * 0.8
    else:
        raise ValueError()


def _generate_long_audio(
    detailed_script: SegmentDetailedScript,
) -> tuple[np.ndarray, list[tuple[str, float]], float]:
    processor, model = _get_model()

    walter_pieces = []
    sound_effect_pieces = []
    audio_fragments = []
    total_sound_effect_duration_sec = 0
    total_walter_duration_sec = 0

    def _print_track_lengths():
        tmp_walter_track = np.concatenate(walter_pieces)
        tmp_sound_effect_track = np.concatenate(sound_effect_pieces)
        print(
            f"walter: {len(tmp_walter_track) / _get_sample_rate()} sound: {len(tmp_sound_effect_track) / _get_sample_rate()}"
        )

    for line in detailed_script.lines:
        print(
            f"pre: {line} {total_sound_effect_duration_sec=} {total_walter_duration_sec=}"
        )

        if line.line_type == "sound":
            # Create sound effect.
            effect_duration_sec = line.content["duration_seconds"]
            sound_effect_type = line.content["sound_effect"]
            sound_effect_audio = _get_sound_effect_data(
                sound_effect_type, effect_duration_sec
            )

            # Create Walter pause which may be shorter than the effect itself.
            walter_pause_length_sec = _walter_pause_for_sound_effect_length(
                sound_effect_type, effect_duration_sec
            )

            # Save pieces
            audio_fragments.append(
                AudioFragments(
                    absolute_start_time_sec=total_sound_effect_duration_sec,
                    audio_type=f"sound={sound_effect_type}",
                    audio=sound_effect_audio,
                    duration_sec=effect_duration_sec,
                    sentence=f"*{sound_effect_type}*",
                    line_body_motion=None,
                )
            )
            sound_effect_pieces.append(sound_effect_audio)
            walter_pieces.append(_get_variable_silence(walter_pause_length_sec))

            # Append length
            total_sound_effect_duration_sec += effect_duration_sec
            total_walter_duration_sec += walter_pause_length_sec

        elif line.line_type == "dialog":
            # Create speech
            piece_audio, piece_sentences_and_durations = _generate_audio_for_line(
                processor, model, line.content["text"]
            )
            total_walter_piece_duration_sec = len(piece_audio) / _get_sample_rate()

            # Create sound effect pause length to align with the end of the walter speech
            sound_effect_pause_length_sec = max(
                (total_walter_duration_sec + total_walter_piece_duration_sec)
                - total_sound_effect_duration_sec,
                0,
            )

            # Save pieces

            for piece_sentence, piece_duration in piece_sentences_and_durations:
                audio_fragments.append(
                    AudioFragments(
                        absolute_start_time_sec=total_walter_duration_sec,
                        audio_type="speech",
                        audio=piece_audio,
                        duration_sec=piece_duration,
                        sentence=piece_sentence,
                        line_body_motion=line.content.get("body_motion"),
                    )
                )
                total_walter_duration_sec += piece_duration

            sound_effect_pieces.append(
                _get_variable_silence(sound_effect_pause_length_sec)
            )
            walter_pieces.append(piece_audio)

            # Append length
            total_sound_effect_duration_sec += sound_effect_pause_length_sec

        print(f"{line} {_print_track_lengths()}")

    walter_track = np.concatenate(walter_pieces)
    sound_effect_track = np.concatenate(sound_effect_pieces)

    def pad_smaller_track(track_a, track_b):
        if len(track_a) < len(track_b):
            track_a = np.pad(track_a, (0, len(track_b) - len(track_a)))
        elif len(track_b) < len(track_a):
            track_b = np.pad(track_b, (0, len(track_a) - len(track_b)))
        return track_a, track_b

    walter_track, sound_effect_track = pad_smaller_track(
        walter_track, sound_effect_track
    )
    total_duration = len(walter_track) / _get_sample_rate()

    del model
    del processor

    return (
        _soft_clip(walter_track + sound_effect_track),
        audio_fragments,
        total_duration,
    )


def audio_for_segment(
    segment: ShowSegment, staging_area: ResourceStagingArea
) -> AudioGeneration:
    long_audio, audio_fragments, total_duration = _generate_long_audio(
        segment.detailed_script
    )
    speech_path = staging_area.audio_path(ext="wav")
    write_wav(speech_path, _get_sample_rate(), long_audio)

    return AudioGeneration(
        total_duration_sec=total_duration,
        relative_audio_path=os.path.relpath(speech_path, staging_area.tmpdir),
        audio_fragments=audio_fragments,
    )
