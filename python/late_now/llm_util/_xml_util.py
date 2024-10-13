import xml.etree.ElementTree as ET
from dataclasses import is_dataclass


def xml_try_find_and_get_text(xml, tag) -> str | None:
    find_result = xml.find(tag)
    if find_result is not None:
        return find_result.text
    return None


def xml_prompt(raw_text):
    tree = ET.fromstring(raw_text)
    ET.indent(tree)
    return ET.tostring(tree).decode()


def dataclass_as_xml(obj) -> str:
    if not is_dataclass(obj):
        raise ValueError("Object must be a dataclass")

    xml = f"<{obj.__class__.__name__}>"

    for field in obj.__dataclass_fields__:
        value = getattr(obj, field) or ""
        xml += f"\n   <{field}>{value}</{field}>"

    xml += f"\n</{obj.__class__.__name__}>"
    return xml_prompt(xml)


def print_xml(xml):
    print(ET.tostring(xml).decode())


def dataclass_to_prompt_spec(cls) -> str:
    xml = f"<{cls.__name__}>"

    for field in cls.__dataclass_fields__:
        xml += f"\n    <{field}>...</{field}>"

    xml += f"\n</{cls.__name__}>"

    return xml
