from django.apps import AppConfig
from django.db.models import JSONField


class DjangoJsonPathConfig(AppConfig):
    name = "django_jsonpath"

    def ready(self):
        from django_jsonpath.lookup import (
            JsonPathExactLookup,
            JsonPathGteLookup,
            JsonPathGtLookup,
            JsonPathLteLookup,
            JsonPathLtLookup,
        )
        from django_jsonpath.transform import (
            JsonPathAnyTransform,
            JSONPathField,
            JsonPathTransform,
        )

        JSONField.register_lookup(JsonPathTransform)

        JSONPathField.register_lookup(JsonPathExactLookup)
        JSONPathField.register_lookup(JsonPathGteLookup)
        JSONPathField.register_lookup(JsonPathGtLookup)
        JSONPathField.register_lookup(JsonPathLteLookup)
        JSONPathField.register_lookup(JsonPathLtLookup)

        JSONPathField.register_lookup(JsonPathAnyTransform)
