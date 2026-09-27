from django.db.models import Field, Transform


class JSONPathField(Field):

    def get_transform(self, lookup_name):
        transform = super().get_transform(lookup_name)
        if transform:
            return transform
        return JsonPathKeyTransformFactory(lookup_name)


class JsonPathKeyTransform(Transform):
    output_field = JSONPathField()

    def __init__(self, key_name, *args, **kwargs):
        self.key_name = key_name
        super().__init__(*args, **kwargs)


class JsonPathKeyTransformFactory:
    def __init__(self, key_name):
        self.key_name = key_name

    def __call__(self, *args, **kwargs):
        return JsonPathKeyTransform(self.key_name, *args, **kwargs)


class JsonPathAnyTransform(Transform):
    lookup_name = 'any'
    output_field = JSONPathField()


class JsonPathTransform(Transform):
    lookup_name = 'jsonpath'
    output_field = JSONPathField()
