OneOf Type
=================

The OneOf type is used to specify that an object must conform to exactly one of the specified schemas. Unlike AnyOf which allows matching multiple schemas, OneOf enforces that the data matches one and only one of the provided schemas.


Examples
-----------------


.. code-block:: python

    from jambo import SchemaConverter


    schema = {
        "title": "Person",
        "description": "A person",
        "type": "object",
        "properties": {
            "id": {
                "oneOf": [
                    {"type": "integer", "minimum": 1},
                    {"type": "string", "pattern": "^[A-Z]{2}[0-9]{4}$"},
                ]
            },
        },
    }

    Model = SchemaConverter.build(schema)

    # Valid: matches the integer schema
    obj1 = Model(id=123)
    print(obj1)  # Output: Person(id=123)

    # Valid: matches the string pattern schema
    obj2 = Model(id="AB1234")
    print(obj2)  # Output: Person(id='AB1234')

    try:
        # Invalid: matches neither schema (negative integer)
        obj3 = Model(id=-5)
    except ValueError as e:
        print("Validation fails as expected:", e)

    try:
        # Invalid: string doesn't match pattern
        obj4 = Model(id="invalid")
    except ValueError as e:
        print("Validation fails as expected:", e)

    try:
        # Invalid: matches both schemas (this would fail if both schemas could match the same value)
        # In this example, the schemas are mutually exclusive by design
        pass