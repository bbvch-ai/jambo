from jambo import SchemaConverter


def test_oneof_basic():
    schema = {
        "title": "Person",
        "description": "A person with an ID that can be either an integer or a formatted string",
        "type": "object",
        "properties": {
            "id": {
                "oneOf": [
                    {"type": "integer", "minimum": 1},
                    {"type": "string", "pattern": "^[A-Z]{2}[0-9]{4}$"},
                ]
            },
        },
        "required": ["id"],
    }

    Model = SchemaConverter.build(schema)


    obj1 = Model(id=123)
    obj2 = Model(id="AB1234")

    try:
        # Invalid: negative integer (doesn't match minimum requirement)
        Model(id=-5)
    except ValueError as e:
        print(f"Negative integer rejected: {e}")

    try:
        # Invalid: string doesn't match pattern
        Model(id="invalid")
    except ValueError as e:
        print(f"Invalid string pattern rejected: {e}")

    try:
        # Invalid: float (doesn't match either schema exactly)
        Model(id=123.45)
    except ValueError as e:
        print(f"Float rejected: {e}")


def test_oneof_with_conflicting_schemas():
    """Test oneOf with potentially conflicting schemas."""
    schema = {
        "title": "Value",
        "type": "object",
        "properties": {
            "data": {
                "oneOf": [
                    {"type": "number", "multipleOf": 2},  # Even numbers
                    {"type": "number", "multipleOf": 3},  # Multiples of 3
                ]
            },
        },
        "required": ["data"],
    }

    Model = SchemaConverter.build(schema)

    print("\n=== Conflicting Schemas Test ===")

    # Valid: only matches first schema (even but not multiple of 3)
    obj1 = Model(data=4)
    print(f"Even number (4): {obj1}")

    # Valid: only matches second schema (multiple of 3 but not even)
    obj2 = Model(data=9)
    print(f"Multiple of 3 (9): {obj2}")

    try:
        # Invalid: matches both schemas (6 is both even and multiple of 3)
        Model(data=6)
    except ValueError as e:
        print(f"Ambiguous value (6) rejected: {e}")

    try:
        # Invalid: matches neither schema
        Model(data=5)
    except ValueError as e:
        print(f"No match value (5) rejected: {e}")


def test_oneof_with_objects():
    """Test oneOf with different object schemas."""
    schema = {
        "title": "Contact",
        "type": "object",
        "properties": {
            "contact_info": {
                "oneOf": [
                    {
                        "type": "object",
                        "properties": {
                            "email": {"type": "string", "format": "email"}
                        },
                        "required": ["email"],
                        "additionalProperties": False
                    },
                    {
                        "type": "object",
                        "properties": {
                            "phone": {"type": "string", "pattern": "^[0-9-]+$"}
                        },
                        "required": ["phone"],
                        "additionalProperties": False
                    }
                ]
            },
        },
        "required": ["contact_info"],
    }

    Model = SchemaConverter.build(schema)

    print("\n=== Object OneOf Test ===")

    # Valid: email contact
    obj1 = Model(contact_info={"email": "user@example.com"})
    print(f"Email contact: {obj1}")

    # Valid: phone contact
    obj2 = Model(contact_info={"phone": "123-456-7890"})
    print(f"Phone contact: {obj2}")

    try:
        # Invalid: has both email and phone (would match both schemas)
        Model(contact_info={"email": "user@example.com", "phone": "123-456-7890"})
    except ValueError as e:
        print(f"Both email and phone rejected: {e}")


if __name__ == "__main__":
    test_oneof_basic()
    test_oneof_with_conflicting_schemas()
    test_oneof_with_objects()
    print("\nAll tests completed!")