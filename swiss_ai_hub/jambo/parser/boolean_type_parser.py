from swiss_ai_hub.jambo.exceptions import InvalidSchemaException
from swiss_ai_hub.jambo.parser._type_parser import GenericTypeParser
from swiss_ai_hub.jambo.types.type_parser_options import TypeParserOptions

from typing_extensions import Unpack


class BooleanTypeParser(GenericTypeParser):
    mapped_type = bool

    json_schema_type = "type:boolean"

    type_mappings = {
        "default": "default",
    }

    def from_properties_impl(
        self, name, properties, **kwargs: Unpack[TypeParserOptions]
    ):
        mapped_properties = self.mappings_properties_builder(properties, **kwargs)

        default_value = properties.get("default")
        if default_value is not None and not isinstance(default_value, bool):
            raise InvalidSchemaException(
                f"Default value for {name} must be a boolean.",
                invalid_field="default",
            )

        return bool, mapped_properties
