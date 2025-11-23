from jambo.parser._type_parser import GenericTypeParser
from jambo.types.json_schema_type import JSONSchema
from jambo.types.type_parser_options import TypeParserOptions

from pydantic import BaseModel, ConfigDict, Field, create_model
from pydantic.fields import FieldInfo
from typing_extensions import Unpack


class ObjectTypeParser(GenericTypeParser):
    mapped_type = object

    json_schema_type = "type:object"

    def from_properties_impl(
        self, name: str, properties: JSONSchema, **kwargs: Unpack[TypeParserOptions]
    ) -> tuple[type[BaseModel], dict]:
        type_parsing = self.to_model(
            name,
            properties.get("properties", {}),
            properties.get("required", []),
            **kwargs,
        )
        type_properties = self.mappings_properties_builder(properties, **kwargs)

        if (default_value := type_properties.get("default")) is not None:
            type_properties["default_factory"] = lambda: type_parsing.model_validate(
                default_value
            )

        if (example_values := type_properties.get("examples")) is not None:
            type_properties["examples"] = [
                type_parsing.model_validate(example) for example in example_values
            ]

        return type_parsing, type_properties

    @classmethod
    def to_model(
        cls,
        name: str,
        properties: dict[str, JSONSchema],
        required_keys: list[str],
        **kwargs: Unpack[TypeParserOptions],
    ) -> type[BaseModel]:
        """
        Converts JSON Schema object properties to a Pydantic model.
        :param name: The name of the model.
        :param properties: The properties of the JSON Schema object.
        :param required_keys: List of required keys in the schema.
        :return: A Pydantic model class.
        """
        model_config = ConfigDict(validate_assignment=True)
        fields = cls._parse_properties(properties, required_keys, **kwargs)

        return create_model(name, __config__=model_config, **fields)  # type: ignore

    @classmethod
    def _parse_properties(
        cls,
        properties: dict[str, JSONSchema],
        required_keys: list[str],
        **kwargs: Unpack[TypeParserOptions],
    ) -> dict[str, tuple[type, FieldInfo]]:
        required_keys = required_keys or []

        fields = {}
        for name, prop in properties.items():
            sub_property: TypeParserOptions = kwargs.copy()
            sub_property["required"] = name in required_keys

            parsed_type, parsed_properties = GenericTypeParser.type_from_properties(
                name,
                prop,
                **sub_property,  # type: ignore
            )
            fields[name] = (parsed_type, Field(**parsed_properties))

        return fields
