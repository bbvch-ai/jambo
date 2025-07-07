from jambo.parser._type_parser import GenericTypeParser
from jambo.types.type_parser_options import TypeParserOptions

from pydantic import EmailStr, HttpUrl, IPvAnyAddress
from typing_extensions import Unpack

from datetime import date, datetime, time


class StringTypeParser(GenericTypeParser):
    mapped_type = str

    json_schema_type = "type:string"

    type_mappings = {
        "maxLength": "max_length",
        "minLength": "min_length",
        "pattern": "pattern",
    }

    format_type_mapping = {
        "email": EmailStr,
        "uri": HttpUrl,
        "ipv4": IPvAnyAddress,
        "ipv6": IPvAnyAddress,
        "hostname": str,
        "date": date,
        "time": time,
        "date-time": datetime,
    }

    format_pattern_mapping = {
        "hostname": r"^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$",
    }

    def from_properties_impl(
        self, name, properties, **kwargs: Unpack[TypeParserOptions]
    ):
        mapped_properties = self.mappings_properties_builder(
            properties, **kwargs
        )

        format_type = properties.get("format")
        if not format_type:
            return str, mapped_properties

        if format_type not in self.format_type_mapping:
            raise ValueError(f"Unsupported string format: {format_type}")

        mapped_type = self.format_type_mapping[format_type]
        if format_type in self.format_pattern_mapping:
            mapped_properties["pattern"] = self.format_pattern_mapping[format_type]

        if "json_schema_extra" not in mapped_properties:
            mapped_properties["json_schema_extra"] = {}
        mapped_properties["json_schema_extra"]["format"] = format_type

        return mapped_type, mapped_properties
