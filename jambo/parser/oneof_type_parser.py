from jambo.parser._type_parser import GenericTypeParser
from jambo.types.type_parser_options import TypeParserOptions

from pydantic import Field, BeforeValidator, TypeAdapter, ValidationError
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

        union_type = Union[(*field_types,)]

        discriminator = properties.get("discriminator")
        if discriminator and isinstance(discriminator, dict):
            property_name = discriminator.get("propertyName")
            if property_name:
                validated_type = Annotated[union_type, Field(discriminator=property_name)]
                return validated_type, mapped_properties

        def validate_one_of(value: Any) -> Any:
            matched_count = 0
            validation_errors = []

            for field_type in field_types:
                try:
                    adapter = TypeAdapter(field_type)
                    adapter.validate_python(value)
                    matched_count += 1
                except ValidationError as e:
                    validation_errors.append(str(e))
                    continue

            if matched_count == 0:
                raise ValueError(f"Value does not match any of the oneOf schemas")
            elif matched_count > 1:
                raise ValueError(f"Value matches multiple oneOf schemas, exactly one expected")

            return value

        validated_type = Annotated[union_type, BeforeValidator(validate_one_of)]
        return validated_type, mapped_properties
