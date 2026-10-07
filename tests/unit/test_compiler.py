from django.db.models import JSONField, Value
from django.test import SimpleTestCase
from django_jsonpath.compiler import JsonPathSQLCompiler
from psycopg.types.json import Jsonb

from tests.models import Product


class TestJsonPathSQL(SimpleTestCase):
    def test_preserves_root_params(self):
        qs = Product.objects.annotate(
            document=Value(
                {"items": [{"price": 150}]},
                output_field=JSONField(),
            )
        ).filter(
            document__jsonpath__items__any__price__gt=100,
        )

        params: tuple[Jsonb, Jsonb, str]
        _, params = qs.query.sql_with_params()

        assert len(params) == 3, "Root params were dropped"

        assert isinstance(params[0], Jsonb)
        assert params[0].obj == {"items": [{"price": 150}]}

        assert isinstance(params[1], Jsonb)
        assert params[1].obj == {"items": [{"price": 150}]}

        assert isinstance(params[2], str)
        assert params[2] == '$."items"[*]?(@."price" > 100)'


class TestJsonPathLiteralCompilation(SimpleTestCase):
    def test_unsupported_type_raises(self):
        compiler = JsonPathSQLCompiler(object())

        with self.assertRaisesRegex(TypeError, "Unsupported JSONPath literal type: dict"):
            compiler.compile_jsonpath_literal({"value": 50})

    def test_non_finite_float_raises(self):
        compiler = JsonPathSQLCompiler(object())
        value_type_exception_msg = "JSONPath numeric value must be finite"

        with (
            self.subTest("NaN"),
            self.assertRaisesMessage(ValueError, value_type_exception_msg),
        ):
            compiler.compile_jsonpath_literal(float("nan"))

        with (
            self.subTest("Infinity"),
            self.assertRaisesMessage(ValueError, value_type_exception_msg),
        ):
            compiler.compile_jsonpath_literal(float("inf"))

        with (
            self.subTest("Negative Infinity"),
            self.assertRaisesMessage(ValueError, value_type_exception_msg),
        ):
            compiler.compile_jsonpath_literal(float("-inf"))
