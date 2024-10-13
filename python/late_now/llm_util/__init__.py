import xml.etree.ElementTree as ET
from enum import Enum, auto

from late_now.llm_util import _groq_backend, _local_backend, _openai_backend
from ._xml_util import xml_prompt
from late_now.plan_broadcast._characters import WALTER_SPANKS_BIO

UNKNOWN_RESPONSE = "|UNK|"


def _walter_system_prompt() -> str:
    return f"You are Walter Spanks. <bio>{WALTER_SPANKS_BIO}</bio> Respond as Walter Spanks."


class LLMBackendType(Enum):
    GROQ = auto()
    LOCAL = auto()
    OPENAI = auto()


BACKEND_TYPE_TO_BACKEND = {
    LLMBackendType.GROQ: _groq_backend,
    LLMBackendType.LOCAL: _local_backend,
    LLMBackendType.OPENAI: _openai_backend,
}

ACTIVE_HUMOR_TYPE = LLMBackendType.LOCAL
ACTIVE_HUMOR_BACKEND = BACKEND_TYPE_TO_BACKEND[ACTIVE_HUMOR_TYPE]
ACTIVE_GENERAL_TYPE = LLMBackendType.OPENAI
ACTIVE_GENERAL_BACKEND = BACKEND_TYPE_TO_BACKEND[ACTIVE_GENERAL_TYPE]


def prompt_walter(prompt: str, temperature=1.0):
    return _prompt_backend(
        ACTIVE_HUMOR_BACKEND,
        prompt,
        system_prompt=_walter_system_prompt(),
        temperature=temperature,
    )


def prompt_screenwriter(
    prompt: str, *, screenwriter_system_prompt: str, temperature=0.9
):
    return _prompt_backend(
        ACTIVE_GENERAL_BACKEND,
        prompt,
        system_prompt=screenwriter_system_prompt,
        temperature=temperature,
    )


def prompt_general_llm(prompt: str, system_prompt: str = "", temperature=1.0):
    return _prompt_backend(
        ACTIVE_GENERAL_BACKEND,
        prompt,
        system_prompt=system_prompt,
        temperature=temperature,
    )


def _prompt_backend(backend, prompt: str, system_prompt: str, temperature: float):
    json_response = backend.completion(
        prompt, system_prompt=system_prompt, temperature=temperature
    )
    print(json_response)
    content = json_response["choices"][0]["message"]["content"]
    return content.removesuffix("<|eot_id|>")


def try_parse_xml_llm_response(response: str):
    # trim up to the first '<' character and the last '>' character
    if "<" not in response or ">" not in response:
        return None

    response = response[response.index("<") : response.rindex(">") + 1]
    print(response)

    def _inner(response):
        try:
            return xml_prompt(response)
        except ET.ParseError:
            return xml_prompt(
                prompt_general_llm(
                    f"""
                    Correct any XML syntax errors in the following string, preserving the tags 
                    and structure as much as possible. Remove any non-XML information. Respond 
                    with absolutely no other text besides XML. String:
                    {response}
                    """,
                    system_prompt="You are an XML corrector. You fix XML errors, preserving content.",
                )
            )

    try:
        return ET.fromstring(_inner(response))
    except ET.ParseError:
        return None
