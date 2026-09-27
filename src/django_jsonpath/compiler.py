import json

from django_jsonpath.lookup import JsonPathTerminalLookup
from django_jsonpath.transform import (
    JsonPathAnyTransform,
    JsonPathKeyTransform,
    JsonPathTransform,
)


class JsonPathSQLCompiler:
    def __init__(self, compiler):
        self.compiler = compiler

    def split_expression(self, node) -> tuple[list, object]:
        n = node
        predicate = []
        while n.lhs:
            if not isinstance(n, (JsonPathKeyTransform, JsonPathTerminalLookup)):
                break

            predicate.append(n)
            n = n.lhs

        return predicate, n

    def compile_path(self, node) -> str | None:
        if isinstance(node, JsonPathAnyTransform):
            return f"{self.compile_path(node.lhs)}[*]"

        if isinstance(node, JsonPathKeyTransform):
            return f"{self.compile_path(node.lhs)}.{json.dumps(node.key_name)}"

        if isinstance(node, JsonPathTransform):
            return "$"

    def get_root_node(self, node):
        if isinstance(node, JsonPathTransform):
            return node.lhs
        elif hasattr(node, 'lhs'):
            return self.get_root_node(node.lhs)
        else:
            raise ValueError("Cannot determine root node.")

    def compile_predicates(self, nodes) -> str:
        sql = ""
        for node in nodes:

            if isinstance(node, JsonPathKeyTransform):
                sql = f".{json.dumps(node.key_name)}{sql}"

            if isinstance(node, JsonPathTerminalLookup):
                rhs = self.compile_jsonpath_literal(node.rhs)
                sql = f"{sql} {node.jsonpath_operator} {rhs}"

        return f"@{sql}"

    def compile_jsonpath_literal(self, value):
        if value is None:
            return "null"

        if isinstance(value, bool):
            return "true" if value else "false"

        if isinstance(value, (int, str, float)):
            return json.dumps(value)

        raise TypeError(
            f"Unsupported JSONPath literal type: {type(value).__name__}"
        )

    def compile(self, end_node):
        predicates, path = self.split_expression(end_node)

        predicate_expr = self.compile_predicates(predicates)
        path_expr = self.compile_path(path)

        root = self.get_root_node(end_node)
        root_node_sql, root_params = self.compiler.compile(root)

        jsonpath = f"{path_expr}?({predicate_expr})"
        return f"{root_node_sql} @? %s::jsonpath", (*root_params, jsonpath)
