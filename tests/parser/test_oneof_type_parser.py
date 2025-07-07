from jambo import SchemaConverter

from unittest import TestCase


class TestOneOfTypeParser(TestCase):
    def test_oneof_basic_integer_and_string(self):
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
        self.assertEqual(obj1.id, 123)

        obj2 = Model(id="AB1234")
        self.assertEqual(obj2.id, "AB1234")

    def test_oneof_validation_failures(self):
        schema = {
            "title": "Person",
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

        with self.assertRaises(ValueError):
            Model(id=-5)

        with self.assertRaises(ValueError):
            Model(id="invalid")

        with self.assertRaises(ValueError):
            Model(id=123.45)

    def test_oneof_with_conflicting_schemas(self):
        schema = {
            "title": "Value",
            "type": "object",
            "properties": {
                "data": {
                    "oneOf": [
                        {"type": "number", "multipleOf": 2},
                        {"type": "number", "multipleOf": 3},
                    ]
                },
            },
            "required": ["data"],
        }

        Model = SchemaConverter.build(schema)

        obj1 = Model(data=4)
        self.assertEqual(obj1.data, 4)

        obj2 = Model(data=9)
        self.assertEqual(obj2.data, 9)

        with self.assertRaises(ValueError) as cm:
            Model(data=6)
        self.assertIn("matches multiple oneOf schemas", str(cm.exception))

        with self.assertRaises(ValueError):
            Model(data=5)

    def test_oneof_with_objects(self):
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

        obj1 = Model(contact_info={"email": "user@example.com"})
        self.assertEqual(obj1.contact_info.email, "user@example.com")

        obj2 = Model(contact_info={"phone": "123-456-7890"})
        self.assertEqual(obj2.contact_info.phone, "123-456-7890")

        with self.assertRaises(ValueError):
            Model(contact_info={"email": "user@example.com", "phone": "123-456-7890"})

    def test_oneof_with_discriminator_basic(self):
        schema = {
            "title": "Pet",
            "type": "object",
            "properties": {
                "pet": {
                    "oneOf": [
                        {
                            "type": "object",
                            "properties": {
                                "type": {"const": "cat"},
                                "meows": {"type": "boolean"}
                            },
                            "required": ["type", "meows"]
                        },
                        {
                            "type": "object",
                            "properties": {
                                "type": {"const": "dog"},
                                "barks": {"type": "boolean"}
                            },
                            "required": ["type", "barks"]
                        }
                    ],
                    "discriminator": {
                        "propertyName": "type"
                    }
                }
            },
            "required": ["pet"]
        }

        Model = SchemaConverter.build(schema)

        cat = Model(pet={"type": "cat", "meows": True})
        self.assertEqual(cat.pet.type, "cat")
        self.assertEqual(cat.pet.meows, True)

        dog = Model(pet={"type": "dog", "barks": False})
        self.assertEqual(dog.pet.type, "dog")
        self.assertEqual(dog.pet.barks, False)

        with self.assertRaises(ValueError):
            Model(pet={"type": "cat", "barks": True})

        with self.assertRaises(ValueError):
            Model(pet={"type": "bird", "flies": True})

    def test_oneof_with_discriminator_mapping(self):
        schema = {
            "title": "Vehicle",
            "type": "object",
            "properties": {
                "vehicle": {
                    "oneOf": [
                        {
                            "type": "object",
                            "properties": {
                                "vehicle_type": {"const": "car"},
                                "doors": {"type": "integer", "minimum": 2, "maximum": 4}
                            },
                            "required": ["vehicle_type", "doors"]
                        },
                        {
                            "type": "object",
                            "properties": {
                                "vehicle_type": {"const": "motorcycle"},
                                "engine_size": {"type": "number", "minimum": 125}
                            },
                            "required": ["vehicle_type", "engine_size"]
                        }
                    ],
                    "discriminator": {
                        "propertyName": "vehicle_type",
                        "mapping": {
                            "car": "#/properties/vehicle/oneOf/0",
                            "motorcycle": "#/properties/vehicle/oneOf/1"
                        }
                    }
                }
            },
            "required": ["vehicle"]
        }

        Model = SchemaConverter.build(schema)

        car = Model(vehicle={"vehicle_type": "car", "doors": 4})
        self.assertEqual(car.vehicle.vehicle_type, "car")
        self.assertEqual(car.vehicle.doors, 4)

        motorcycle = Model(vehicle={"vehicle_type": "motorcycle", "engine_size": 600.0})
        self.assertEqual(motorcycle.vehicle.vehicle_type, "motorcycle")
        self.assertEqual(motorcycle.vehicle.engine_size, 600.0)

    def test_oneof_with_discriminator_invalid_values(self):
        schema = {
            "title": "Shape",
            "type": "object",
            "properties": {
                "shape": {
                    "oneOf": [
                        {
                            "type": "object",
                            "properties": {
                                "type": {"const": "circle"},
                                "radius": {"type": "number", "minimum": 0}
                            },
                            "required": ["type", "radius"]
                        },
                        {
                            "type": "object",
                            "properties": {
                                "type": {"const": "square"},
                                "side": {"type": "number", "minimum": 0}
                            },
                            "required": ["type", "side"]
                        }
                    ],
                    "discriminator": {
                        "propertyName": "type"
                    }
                }
            },
            "required": ["shape"]
        }

        Model = SchemaConverter.build(schema)

        with self.assertRaises(ValueError):
            Model(shape={"type": "triangle", "base": 5, "height": 3})

        with self.assertRaises(ValueError):
            Model(shape={"type": "circle", "side": 5})

        with self.assertRaises(ValueError):
            Model(shape={"radius": 5})

    def test_oneof_missing_properties(self):
        schema = {
            "title": "Test",
            "type": "object",
            "properties": {
                "value": {
                    "notOneOf": [
                        {"type": "string"},
                        {"type": "integer"},
                    ]
                },
            },
        }

        with self.assertRaises(ValueError):
            SchemaConverter.build(schema)

    def test_oneof_invalid_properties(self):
        schema = {
            "title": "Test",
            "type": "object",
            "properties": {
                "value": {
                    "oneOf": None
                },
            },
        }

        with self.assertRaises(ValueError):
            SchemaConverter.build(schema)

    def test_oneof_with_default_value(self):
        schema = {
            "title": "Test",
            "type": "object",
            "properties": {
                "value": {
                    "oneOf": [
                        {"type": "string"},
                        {"type": "integer"},
                    ],
                    "default": "test"
                },
            },
        }

        Model = SchemaConverter.build(schema)
        obj = Model()
        self.assertEqual(obj.value, "test")

    def test_oneof_with_invalid_default_value(self):
        schema = {
            "title": "Test",
            "type": "object",
            "properties": {
                "value": {
                    "oneOf": [
                        {"type": "string", "minLength": 5},
                        {"type": "integer", "minimum": 10},
                    ],
                    "default": "hi"
                },
            },
        }

        with self.assertRaises(ValueError):
            SchemaConverter.build(schema)

    def test_oneof_discriminator_without_property_name(self):
        schema = {
            "title": "Test",
            "type": "object",
            "properties": {
                "value": {
                    "oneOf": [
                        {
                            "type": "object",
                            "properties": {
                                "type": {"const": "a"},
                                "value": {"type": "string"}
                            }
                        },
                        {
                            "type": "object",
                            "properties": {
                                "type": {"const": "b"},
                                "value": {"type": "integer"}
                            }
                        }
                    ],
                    "discriminator": {}  # discriminator without propertyName
                }
            }
        }

        Model = SchemaConverter.build(schema)

        # Should succeed because input matches exactly one schema (the first one)
        # The first schema matches: type="a" matches const("a"), value="test" is a string
        # The second schema doesn't match: type="a" does not match const("b")
        obj = Model(value={"type": "a", "value": "test", "extra": "invalid"})
        self.assertEqual(obj.value.type, "a")
        self.assertEqual(obj.value.value, "test")

        # Test with input that matches the second schema
        obj2 = Model(value={"type": "b", "value": 42})
        self.assertEqual(obj2.value.type, "b")
        self.assertEqual(obj2.value.value, 42)

        # Test with input that matches neither schema (should fail)
        with self.assertRaises(ValueError) as cm:
            Model(value={"type": "c", "value": "test"})
        self.assertIn("does not match any of the oneOf schemas", str(cm.exception))

    def test_oneof_multiple_matches_without_discriminator(self):
        """Test case where input genuinely matches multiple oneOf schemas"""
        schema = {
            "title": "Test",
            "type": "object",
            "properties": {
                "value": {
                    "oneOf": [
                        {
                            "type": "object",
                            "properties": {
                                "data": {"type": "string"}
                            }
                        },
                        {
                            "type": "object",
                            "properties": {
                                "data": {"type": "string"},
                                "optional": {"type": "string"}
                            }
                        }
                    ],
                    "discriminator": {}  # discriminator without propertyName
                }
            }
        }

        Model = SchemaConverter.build(schema)

        # This input matches both schemas since both accept data as string
        # and neither requires specific additional properties
        with self.assertRaises(ValueError) as cm:
            Model(value={"data": "test"})
        self.assertIn("matches multiple oneOf schemas", str(cm.exception))