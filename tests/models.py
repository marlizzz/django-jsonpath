from django.db.models import JSONField, Model


class Product(Model):
    payload = JSONField()

    class Meta:
        app_label = "tests"
