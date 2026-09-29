from django.db.models import Field, Transform


class JSONPathField(Field):

    def get_transform(self, lookup_name):
        transform = super().get_transform(lookup_name)
        if transform:
            return transform

        if lookup_name.isnumeric():
            return JsonPathIndexTransformFactory(lookup_name)

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


class JsonPathIndexTransform(Transform):
    output_field = JSONPathField()

    def __init__(self, key_name, *args, **kwargs):
        self.key_name = key_name
        super().__init__(*args, **kwargs)


class JsonPathIndexTransformFactory:
    def __init__(self, key_name):
        self.key_name = key_name

    def __call__(self, *args, **kwargs):
        return JsonPathIndexTransform(self.key_name, *args, **kwargs)


class JsonPathAnyTransform(Transform):
    lookup_name = 'any'
    output_field = JSONPathField()


class JsonPathTransform(Transform):
    lookup_name = 'jsonpath'
    output_field = JSONPathField()
