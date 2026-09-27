from django.db.models import Lookup


class JsonPathTerminalLookup(Lookup):
    jsonpath_operator: str

    def as_postgresql(self, compiler, connection, **extra_context):
        from django_jsonpath.compiler import JsonPathSQLCompiler

        return JsonPathSQLCompiler(compiler).compile(self)


class JsonPathGtLookup(JsonPathTerminalLookup):
    lookup_name = "gt"
    jsonpath_operator = ">"
