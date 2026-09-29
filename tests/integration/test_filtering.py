from django.test import TestCase

from tests.models import Product


class TestGt(TestCase):

    def test_basic(self):
        Product.objects.create(
            payload={"items": [{"price": 50}, {"price": 150}]}
        )
        Product.objects.create(
            payload={"items": [{"price": 20}, {"price": 80}]}
        )

        assert Product.objects.filter(
            payload__jsonpath__items__any__price__gt=100
        ).count() == 1

        assert Product.objects.filter(
            payload__jsonpath__items__any__price__gt=200
        ).count() == 0

        assert Product.objects.filter(
            payload__jsonpath__items__any__price__gt=70
        ).count() == 2

        assert Product.objects.filter(
            payload__jsonpath__items__any__price__gt=30
        ).count() == 2

    def test_nested(self):
        Product.objects.create(
            payload={"items": {"catalog": [{"price": 15}]}}
        )
        assert Product.objects.filter(
            payload__jsonpath__items__catalog__any__price__gt=15
        ).count() == 0
        assert Product.objects.filter(
            payload__jsonpath__items__catalog__any__price__gt=14
        ).count() == 1
        assert Product.objects.filter(
            payload__jsonpath__items__any__price__gt=14
        ).count() == 0

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

        assert Product.objects.filter(
            payload__jsonpath__items__0__price__gt=100
        ).count() == 0

        assert Product.objects.filter(
            payload__jsonpath__items__0__price__gt=30
        ).count() == 1

        assert Product.objects.filter(
            payload__jsonpath__items__0__price__gt=10
        ).count() == 2

        assert Product.objects.filter(
            payload__jsonpath__items__1__price__gt=100
        ).count() == 1
        assert Product.objects.filter(
            payload__jsonpath__items__1__price__gt=200
        ).count() == 0

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

        assert Product.objects.filter(
            payload__jsonpath__items__0__groups__1__price__gt=175
        ).count() == 1
        assert Product.objects.filter(
            payload__jsonpath__items__0__groups__1__price__gt=200
        ).count() == 0
        assert Product.objects.filter(
            payload__jsonpath__items__0__groups__1__price__gt=100
        ).count() == 2

        assert Product.objects.filter(
            payload__jsonpath__items__1__groups__0__price__gt=50
        ).count() == 1
        assert Product.objects.filter(
            payload__jsonpath__items__1__groups__0__price__gt=70
        ).count() == 0
