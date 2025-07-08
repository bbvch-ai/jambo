from jambo.parser._type_parser import GenericTypeParser
from jambo.types.type_parser_options import TypeParserOptions

from pydantic import Field
from typing import Annotated, Unpack
from types import UnionType
from functools import reduce
from operator import or_


class AnyOfTypeParser(GenericTypeParser):
    mapped_type = UnionType

    json_schema_type = "anyOf"

    def from_properties_impl(
        self, name, properties, **kwargs: Unpack[TypeParserOptions]
    ):
        if "anyOf" not in properties:
            raise ValueError(f"Invalid JSON Schema: {properties}")

        if not isinstance(properties["anyOf"], list):
            raise ValueError(f"Invalid JSON Schema: {properties['anyOf']}")

        mapped_properties = self.mappings_properties_builder(properties, **kwargs)

        sub_properties = properties["anyOf"]

        sub_types = [
            GenericTypeParser.type_from_properties(name, subProperty, **kwargs)
            for subProperty in sub_properties
        ]

        if not kwargs.get("required", False):
            mapped_properties["default"] = mapped_properties.get("default")

        # By defining the type as Union of Annotated type we can use the Field validator
        # to enforce the constraints of each union type when needed.
        # We use Annotated to attach the Field validators to the type.
        # Only wrap in Annotated[T, Field(**v)] if there are meaningful field constraints
        # Don't wrap for simple cases where v only contains {'default': None}
        field_types = [
            Annotated[t, Field(**v)] if self._has_meaningful_constraints(v) else t
            for t, v in sub_types
        ]

        union_type = reduce(or_, field_types)

        return union_type, mapped_properties
