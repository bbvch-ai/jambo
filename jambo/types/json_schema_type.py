from __future__ import annotations

from typing import Dict, List, Literal, TypedDict

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


JSONType = str | int | float | bool | None | Dict[str, "JSONType"] | List["JSONType"]


class JSONSchema(TypedDict, total=False):
    # Basic metadata
    title: str
    description: str
    default: JSONType
    examples: List[JSONType]

    # Type definitions
    type: JSONSchemaType | List[JSONSchemaType]

    # Object-specific keywords
    properties: Dict[str, "JSONSchema"]
    required: List[str]
    additionalProperties: bool | "JSONSchema"
    minProperties: int
    maxProperties: int
    patternProperties: Dict[str, "JSONSchema"]
    dependencies: Dict[str, List[str] | "JSONSchema"]

    # Array-specific keywords
    items: "JSONSchema" | List["JSONSchema"]
    additionalItems: bool | "JSONSchema"
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
    enum: List[JSONType]
    const: JSONType

    # Conditionals
    if_: "JSONSchema"  # 'if' is a reserved word in Python
    then: "JSONSchema"
    else_: "JSONSchema"  # 'else' is also a reserved word

    # Combination keywords
    allOf: List["JSONSchema"]
    anyOf: List["JSONSchema"]
    oneOf: List["JSONSchema"]
    not_: "JSONSchema"  # 'not' is a reserved word


# Fix forward references
JSONSchema.__annotations__["properties"] = Dict[str, JSONSchema]
JSONSchema.__annotations__["items"] = JSONSchema | List[JSONSchema]
JSONSchema.__annotations__["additionalItems"] = bool | JSONSchema
JSONSchema.__annotations__["additionalProperties"] = bool | JSONSchema
JSONSchema.__annotations__["patternProperties"] = Dict[str, JSONSchema]
JSONSchema.__annotations__["dependencies"] = Dict[str, List[str] | JSONSchema]
JSONSchema.__annotations__["if_"] = JSONSchema
JSONSchema.__annotations__["then"] = JSONSchema
JSONSchema.__annotations__["else_"] = JSONSchema
JSONSchema.__annotations__["allOf"] = List[JSONSchema]
JSONSchema.__annotations__["anyOf"] = List[JSONSchema]
JSONSchema.__annotations__["oneOf"] = List[JSONSchema]
JSONSchema.__annotations__["not_"] = JSONSchema
