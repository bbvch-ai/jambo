from __future__ import annotations

from typing import Literal, TypedDict

from types import NoneType


JSONSchemaType = Literal[
    "string", "number", "integer", "boolean", "object", "array", "null"
]


JSONSchemaNativeTypes: tuple[type, ...] = (
    str, 
    int,
    float,
    bool,
    list,
    set,
    NoneType,
)


JSONType = str | int | float | bool | None | dict[str, "JSONType"] | list["JSONType"]


class JSONSchema(TypedDict, total=False):
    # Basic metadata
    title: str
    description: str
    default: JSONType
    examples: list[JSONType]

    # Type definitions
    type: JSONSchemaType | list[JSONSchemaType]

    # Object-specific keywords
    properties: dict[str, JSONSchema]
    required: list[str]
    additionalProperties: bool | JSONSchema
    minProperties: int
    maxProperties: int
    patternProperties: dict[str, JSONSchema]
    dependencies: dict[str, list[str] | JSONSchema]

    # Array-specific keywords
    items: JSONSchema | list[JSONSchema]
    additionalItems: bool | JSONSchema
    minItems: int
    maxItems: int
    uniqueItems: bool

    # String-specific keywords
    minLength: int
    maxLength: int
    pattern: str
    format: str

    # Number-specific keywords
    minimum: float
    maximum: float
    exclusiveMinimum: float
    exclusiveMaximum: float
    multipleOf: float

    # Enum and const
    enum: list[JSONType]
    const: JSONType

    # Conditionals
    if_: JSONSchema  # 'if' is a reserved word in Python
    then: JSONSchema
    else_: JSONSchema  # 'else' is also a reserved word

    # Combination keywords
    allOf: list[JSONSchema]
    anyOf: list[JSONSchema]
    oneOf: list[JSONSchema]
    not_: JSONSchema  # 'not' is a reserved word


# Fix forward references
JSONSchema.__annotations__["properties"] = dict[str, JSONSchema]
JSONSchema.__annotations__["items"] = JSONSchema | list[JSONSchema]
JSONSchema.__annotations__["additionalItems"] = bool | JSONSchema
JSONSchema.__annotations__["additionalProperties"] = bool | JSONSchema
JSONSchema.__annotations__["patternProperties"] = dict[str, JSONSchema]
JSONSchema.__annotations__["dependencies"] = dict[str, list[str] | JSONSchema]
JSONSchema.__annotations__["if_"] = JSONSchema
JSONSchema.__annotations__["then"] = JSONSchema
JSONSchema.__annotations__["else_"] = JSONSchema
JSONSchema.__annotations__["allOf"] = list[JSONSchema]
JSONSchema.__annotations__["anyOf"] = list[JSONSchema]
JSONSchema.__annotations__["oneOf"] = list[JSONSchema]
JSONSchema.__annotations__["not_"] = JSONSchema
