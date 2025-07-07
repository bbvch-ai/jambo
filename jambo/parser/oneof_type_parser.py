from jambo.parser._type_parser import GenericTypeParser
from jambo.types.type_parser_options import TypeParserOptions

from pydantic import Field, AfterValidator
from typing_extensions import Annotated, Union, Unpack, Any


class OneOfTypeParser(GenericTypeParser):
    mapped_type = Union

    json_schema_type = "oneOf"

    def from_properties_impl(
            self, name, properties, **kwargs: Unpack[TypeParserOptions]
    ):
        if "oneOf" not in properties:
            raise ValueError(f"Invalid JSON Schema: {properties}")

        if not isinstance(properties["oneOf"], list):
            raise ValueError(f"Invalid JSON Schema: {properties['oneOf']}")

        mapped_properties = self.mappings_properties_builder(properties, **kwargs)

        sub_properties = properties["oneOf"]

        sub_types = [
            GenericTypeParser.type_from_properties(name, subProperty, **kwargs)
            for subProperty in sub_properties
        ]

        if not kwargs.get("required", False):
            mapped_properties["default"] = mapped_properties.get("default")

        field_types = [
            Annotated[t, Field(**v)] if self._has_meaningful_constraints(v) else t
            for t, v in sub_types
        ]

        def validate_one_of(value: Any) -> Any:
            valid_count = 0
            last_valid_value = None

            for field_type in field_types:
                try:
                    adapter = TypeAdapter(field_type)
                    validated_value = adapter.validate_python(value)
                    valid_count += 1
                    last_valid_value = validated_value
                except ValidationError:
                    continue

            if valid_count == 0:
                raise ValueError(f"Value {value} does not match any of the oneOf schemas")
            elif valid_count > 1:
                raise ValueError(f"Value {value} matches more than one oneOf schema (exactly one required)")

            return last_valid_value

        # Apply the oneOf validator to the Union type
        union_type = Union[(*field_types,)]
        validated_type = Annotated[union_type, AfterValidator(validate_one_of)]

        return validated_type, mapped_properties
