from django.db.models import Lookup


class JsonPathTerminalLookup(Lookup):
    jsonpath_operator: str

    def as_postgresql(self, compiler, connection, **extra_context):
        from django_jsonpath.compiler import JsonPathSQLCompiler
        return JsonPathSQLCompiler(compiler).compile(self)


class JsonPathExactLookup(JsonPathTerminalLookup):
    lookup_name = "exact"
    jsonpath_operator = "=="


class JsonPathGtLookup(JsonPathTerminalLookup):
    lookup_name = "gt"
    jsonpath_operator = ">"


class JsonPathGteLookup(JsonPathTerminalLookup):
    lookup_name = "gte"
    jsonpath_operator = ">="


class JsonPathLtLookup(JsonPathTerminalLookup):
    lookup_name = "lt"
    jsonpath_operator = "<"


class JsonPathLteLookup(JsonPathTerminalLookup):
    lookup_name = "lte"
    jsonpath_operator = "<="
