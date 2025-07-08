from jambo.types.json_schema_type import JSONSchema

from typing import TypedDict


class TypeParserOptions(TypedDict):
    required: bool
    context: JSONSchema
    ref_cache: dict[str, type]
