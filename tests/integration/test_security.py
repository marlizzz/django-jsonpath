from django.test import TestCase

from tests.models import Product


class TestRHSEscaping(TestCase):

    def test_rhs_can_not_inject_sql(self):
        Product.objects.create(
            payload={"items": {"catalog": [{"price": 15}]}}
        )
        result = Product.objects.filter(
            payload__jsonpath__items__catalog__name__gt="1000)'OR TRUE --"
        )
        assert result.count() == 0

    def test_rhs_can_not_inject_jsonpath(self):
        Product.objects.create(
            payload={"items": {"catalog": [{"price": 15}]}}
        )
        result = Product.objects.filter(
            payload__jsonpath__items__catalog__name__gt="1 || 1 == 1"
        )
        assert result.count() == 0
