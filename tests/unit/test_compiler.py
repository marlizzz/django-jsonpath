from django.db.models import JSONField, Value
from django.test import SimpleTestCase
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