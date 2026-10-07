from django.test import TestCase

from tests.models import Product


class ProductJSONPathFilterTestCase(TestCase):
    def assert_filter_counts(self, cases):
        for lookup, value, expected_count in cases:
            count = Product.objects.filter(**{lookup: value}).count()
            self.assertEqual(count, expected_count)


class TestExact(ProductJSONPathFilterTestCase):

    def test_basic(self):
        Product.objects.create(
            payload={"items": [{"price": 50}, {"price": 100}]}
        )
        Product.objects.create(
            payload={"items": [{"price": 20}, {"price": 50}]}
        )

        cases = [
            ("payload__jsonpath__items__any__price", 100, 1),
            ("payload__jsonpath__items__any__price", 101, 0),
            ("payload__jsonpath__items__any__price", 50, 2),
        ]
        self.assert_filter_counts(cases)

    def test_explicit_exact(self):
        Product.objects.create(
            payload={"items": [{"price": 50}, {"price": 100}]}
        )

        cases = [
            ("payload__jsonpath__items__any__price__exact", 100, 1),
            ("payload__jsonpath__items__any__price__exact", 101, 0),
        ]
        self.assert_filter_counts(cases)


class TestGt(ProductJSONPathFilterTestCase):

    def test_basic(self):
        Product.objects.bulk_create([
            Product(payload={"items": [{"price": 50}, {"price": 150}]}),
            Product(payload={"items": [{"price": 20}, {"price": 80}]}),
        ])

        cases = [
            ("payload__jsonpath__items__any__price__gt", 100, 1),
            ("payload__jsonpath__items__any__price__gt", 200, 0),
            ("payload__jsonpath__items__any__price__gt", 70, 2),
            ("payload__jsonpath__items__any__price__gt", 30, 2),
        ]
        self.assert_filter_counts(cases)

    def test_nested(self):
        Product.objects.create(
            payload={"items": {"catalog": [{"price": 15}]}}
        )
        cases = [
            ("payload__jsonpath__items__catalog__any__price__gt", 15, 0),
            ("payload__jsonpath__items__catalog__any__price__gt", 14, 1),
            ("payload__jsonpath__items__any__price__gt", 14, 0),
        ]
        self.assert_filter_counts(cases)

    def test_key_with_dot(self):
        Product.objects.create(
            payload={
                "items": [
                    {
                        "product.price": 15,
                    }
                ]
            }
        )

        assert Product.objects.filter(
            **{
                "payload__jsonpath__items__product.price__gt": 10,
            }
        ).count() == 1

    def test_index_transform(self):
        Product.objects.bulk_create([
            Product(payload={"items": [{"price": 50}, {"price": 150}]}),
            Product(payload={"items": [{"price": 20}, {"price": 80}]}),
        ])

        cases = [
            ("payload__jsonpath__items__0__price__gt", 100, 0),
            ("payload__jsonpath__items__0__price__gt", 30, 1),
            ("payload__jsonpath__items__0__price__gt", 10, 2),
            ("payload__jsonpath__items__1__price__gt", 100, 1),
            ("payload__jsonpath__items__1__price__gt", 200, 0),
        ]
        self.assert_filter_counts(cases)

        Product.objects.bulk_create([
            Product(
                payload={
                    "items": [
                        {"groups": [{"price": 50}, {"price": 150}]},
                        {"groups": [{"price": 70}, {"price": 10}]},
                    ]
                }
            ),
            Product(
                payload={
                    "items": [
                        {"groups": [{"price": 40}, {"price": 200}]},
                        {"groups": [{"price": 10}, {"price": 30}]},
                    ]
                }
            ),
        ])

        cases = [
            ("payload__jsonpath__items__0__groups__1__price__gt", 175, 1),
            ("payload__jsonpath__items__0__groups__1__price__gt", 200, 0),
            ("payload__jsonpath__items__0__groups__1__price__gt", 100, 2),
            ("payload__jsonpath__items__1__groups__0__price__gt", 50, 1),
            ("payload__jsonpath__items__1__groups__0__price__gt", 70, 0),
        ]
        self.assert_filter_counts(cases)


class TestGte(ProductJSONPathFilterTestCase):
    def test_basic(self):
        Product.objects.bulk_create([
            Product(payload={"items": [{"price": 50}, {"price": 150}]}),
            Product(payload={"items": [{"price": 20}, {"price": 80}]}),
        ])

        cases = [
            ("payload__jsonpath__items__any__price__gte", 150, 1),
            ("payload__jsonpath__items__any__price__gte", 151, 0),
            ("payload__jsonpath__items__any__price__gte", 50, 2),
        ]
        self.assert_filter_counts(cases)


class TestLt(ProductJSONPathFilterTestCase):
    def test_basic(self):
        Product.objects.bulk_create([
            Product(payload={"items": [{"price": 50}, {"price": 150}]}),
            Product(payload={"items": [{"price": 20}, {"price": 80}]}),
        ])

        cases = [
            ("payload__jsonpath__items__any__price__lt", 20, 0),
            ("payload__jsonpath__items__any__price__lt", 21, 1),
            ("payload__jsonpath__items__any__price__lt", 50, 1),
        ]
        self.assert_filter_counts(cases)


class TestLte(ProductJSONPathFilterTestCase):
    def test_basic(self):
        Product.objects.bulk_create([
            Product(payload={"items": [{"price": 50}, {"price": 150}]}),
            Product(payload={"items": [{"price": 20}, {"price": 80}]}),
        ])

        cases = [
            ("payload__jsonpath__items__any__price__lte", 20, 1),
            ("payload__jsonpath__items__any__price__lte", 19, 0),
            ("payload__jsonpath__items__any__price__lte", 50, 2),
        ]
        self.assert_filter_counts(cases)


class TestFloat(TestCase):
    def test_nan_raises(self):
        Product.objects.create(payload={"item": {"price": 50}})

        with self.assertRaises(ValueError) as exc:
            Product.objects.filter(
                payload__jsonpath__item__price__gt=float("nan")
            ).count()

        self.assertEqual(
            str(exc.exception),
            "JSONPath numeric value must be finite",
        )
