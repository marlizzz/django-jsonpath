# django-jsonpath
Django-native JSONPath support for queries through the ORM.

## Installation

Install the library with:
```bash
pip install git+https://github.com/marlizzz/django-jsonpath.git
```

Then add django-jsonpath to INSTALLED_APPS to your settings:
```python
INSTALLED_APPS = [
    "django_jsonpath",
    # ...
]

```
At this point jsonpath query expressions should be ready to use, just as regular Django query expressions.

## Quick Start

This library adds a `__jsonpath` transform, which switches all the following transforms and lookups to jsonpath ones, not the regular json key transforms or terminal lookups.

Use Django JSONPath lookup syntax for JSON fields:
```python
Product.objects.filter(
    payload__jsonpath__items__any__price__gt=100
)
```

Any stands for [*] in JSONPath, so the above query translates roughly to
```sql
SELECT id, payload
FROM prototype_product
WHERE payload @? '$."items"[*]?(@."price" > 100)'::jsonpath
```

Index transforms are also supported:

```python
Product.objects.filter(
    payload__jsonpath__items__1__price__gt=100
)
```

### Supported lookups
* exact (can be used as implicit one, i.e. `payload__jsonpath__number=5` and `payload__jsonpath__number__exact=5` are the same)
* gt
* gte
* lt
* lte

## Path and predicate semantics
The borderline between path expression and predicate expression lies at the point where `any` or index (`__0`) transform is used the last time, i.e. the rightmost usage of such a transform. In case no such transform is used, the boundary shifts left towards the column, e.g.:
```python
Product.objects.filter(
    payload__jsonpath__item__position__price__gt=100
)
```

Becomes

```sql
SELECT id, payload
FROM prototype_product
WHERE payload @? '$?(@."item"."position"."price" > 100)'::jsonpath
```

## Limitations
* `any` is a reserved word for `[*]` transform. A JSON object key named `"any"` cannot currently be addressed through the DSL.
* Integer transforms `__0` mean an array index, so key `"0"`, for example, would not be found
* Supported versions of Django are 4.2, 5.0, 5.1, 5.2, 6.0, 6.1.
* At this point, this library supports only PostgreSQL 12+ database.


## License
This project is licensed under the BSD License. See the [LICENSE](LICENSE) file for details.
