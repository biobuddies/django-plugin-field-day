# WARNING: Aspirational: Under Construction

# django-plugin-field-day

[![PyPI](https://img.shields.io/pypi/v/django-plugin-field-day.svg)](https://pypi.org/project/django-plugin-field-day/)
[![License](https://img.shields.io/badge/license-BSD%203--Clause-blue.svg)](https://github.com/covingtron/django-plugin-field-day/blob/main/LICENSE)

Additional and improved fields for Django

## Installation

First configure your Django project [to use DJP](https://djp.readthedocs.io/en/latest/installing_plugins.html).

Then install this plugin in the same environment as your Django application.
<!--pytest.mark.skip -->
```bash
uv pip install django-plugin-field-day
```
## Usage

### Negative Left and Right

Negative values passed to `Left` or `Right` measure from the opposite
end. This shines when the head of a string is variable-length but the
tail has a fixed structure. Below, a random dollar-amount prefix
(`$1.00`&nbsp;–&nbsp;`$1000.00`) sits in front of an ISO&nbsp;8601 timestamp so
that no fixed offset can reach the datetime — but the six-character
timezone offset at the right edge is always reachable.

Python — a negative index counts from the right edge regardless of
how long the prefix happens to be:

```python
from datetime import datetime, timezone
from random import randint

iso_8601 = f'${randint(1, 1000)}.{randint(0, 99):02d} {datetime.now(timezone.utc).isoformat()}'
print(iso_8601)

print(
    f'{iso_8601[:-32]}{iso_8601[-32:-22]} {iso_8601[-21:-16]}{iso_8601[-6:]}'.replace(
        '+00:00', ' Z'
    )
)
```

PostgreSQL — `LEFT` and `RIGHT` both accept negative&nbsp;`n`:
`LEFT(s, -6)` returns all but the last six characters and
`RIGHT(s, 6)` returns the last six:

```sql
WITH source (iso_8601) AS (
    SELECT '$' || (random() * 999 + 1)::int::text || '.'
        || lpad((random() * 99)::int::text, 2, '0')
        || ' ' || replace(now()::text, ' ', 'T')
)
SELECT
    iso_8601,
    LEFT(iso_8601, -32)
    || LEFT(RIGHT(iso_8601, 32), 10)
    || ' '
    || LEFT(RIGHT(iso_8601, 21), 5)
    || REPLACE(RIGHT(iso_8601, 6), '+00:00', ' Z') AS rfc_3339
FROM source;
```
```console
iso_8601                                | rfc_3339
----------------------------------------+--------------------------
$720.26 2026-05-14T12:47:32.208036+00:00 | $720.26 2026-05-14 12:47 Z
```

Django ORM — `Left` and `Right` accept the same negative lengths.
The `iso_8601` string is built on the fly with `annotate()`, mirroring
the Python and SQL examples:

```python
from django.contrib.auth.models import User
from django.db.models import CharField, F, IntegerField, Value
from django.db.models.functions import Cast, Concat, Replace
from django.db.models.functions.datetime import Now
from django.db.models.functions.math import Random
from django.db.models.functions.text import LPad
from django_plugin_field_day import Left, Right, StrFTime

qs = User.objects.annotate(
    iso_8601=Concat(
        Value('$'),
        Cast(Cast(Random() * 999 + 1, output_field=IntegerField()), output_field=CharField()),
        Value('.'),
        LPad(
            Cast(Cast(Random() * 99, output_field=IntegerField()), output_field=CharField()),
            2,
            Value('0'),
        ),
        Value(' '),
        StrFTime(Now(), '%Y-%m-%dT%H:%M:%f%z'),
    )
).annotate(
    rfc_3339=Replace(
        Concat(
            Left(F('iso_8601'), -32),
            Left(Right(F('iso_8601'), 32), 10),
            Value(' '),
            Left(Right(F('iso_8601'), 21), 5),
            Right(F('iso_8601'), 6),
        ),
        Value('Z'),
        Value(' Z'),
    )
)
```

Both approaches anchor on the timezone offset (always six characters
wide at the right edge), so the variable-length dollar prefix is
irrelevant — they never need to know where the datetime begins.

That said, negative values aren't strictly required. The same
conversion can be done with `len` / `substring` measured from the left,
though it demands one extra arithmetic step.

Python — `len()` replaces the negative index:

```python
from datetime import datetime, timezone
from random import randint

iso_8601 = f'${randint(1, 1000)}.{randint(0, 99):02d} {datetime.now(timezone.utc).isoformat()}'
print(iso_8601)

end = len(iso_8601)
print(
    (
        f'{iso_8601[: end - 32]}'
        f'{iso_8601[end - 32 : end - 22]} '
        f'{iso_8601[end - 21 : end - 16]}'
        f'{iso_8601[end - 6 :]}'
    ).replace('+00:00', ' Z')
)
```

PostgreSQL — `substring` with `length()` replaces both `LEFT` and
`RIGHT`:

```sql
WITH source (iso_8601) AS (
    SELECT '$' || (random() * 999 + 1)::int::text || '.'
        || lpad((random() * 99)::int::text, 2, '0')
        || ' ' || replace(now()::text, ' ', 'T')
)
SELECT
    substring(iso_8601 FROM 1 FOR end - 32)
    || substring(iso_8601 FROM end - 31 FOR 10)
    || ' '
    || substring(iso_8601 FROM end - 20 FOR 5)
    || replace(substring(iso_8601 FROM end - 5 FOR 6), '+00:00', ' Z')
FROM (
    SELECT *, length(iso_8601) AS end FROM source
) AS variables;
```

Django ORM — `Substr` and `Length` need explicit offsets:

```python
from django.contrib.auth.models import User
from django.db.models import CharField, F, IntegerField, Value
from django.db.models.functions import Cast, Concat, Length, Replace, Substr
from django.db.models.functions.datetime import Now
from django.db.models.functions.math import Random
from django.db.models.functions.text import LPad
from django_plugin_field_day import StrFTime

qs = (
    User.objects
    .annotate(
        iso_8601=Concat(
            Value('$'),
            Cast(Cast(Random() * 999 + 1, output_field=IntegerField()), output_field=CharField()),
            Value('.'),
            LPad(
                Cast(Cast(Random() * 99, output_field=IntegerField()), output_field=CharField()),
                2,
                Value('0'),
            ),
            Value(' '),
            StrFTime(Now(), '%Y-%m-%dT%H:%M:%f%z'),
        )
    )
    .annotate(end=Length(F('iso_8601')))
    .annotate(
        rfc_3339=Replace(
            Concat(
                Substr(F('iso_8601'), 1, F('end') - 32),
                Substr(F('iso_8601'), F('end') - 31, 10),
                Value(' '),
                Substr(F('iso_8601'), F('end') - 20, 5),
                Substr(F('iso_8601'), F('end') - 5, 6),
            ),
            Value('Z'),
            Value(' Z'),
        )
    )
)
```
