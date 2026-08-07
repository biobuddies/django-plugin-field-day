# Todo

## `__like` lookup

Pass a `LIKE` pattern through untouched, leaving `%` and `_` meaningful:

```python
Book.objects.filter(title__like='The % of _ %')
```

`__contains`, `__startswith`, and `__endswith` escape the wildcards, so they reach only three of
the shapes `LIKE` expresses; anything else falls back to `RawSQL` or `extra()`. Add `__ilike` as
the case-insensitive twin, `ILIKE` on PostgreSQL and `LIKE` on the collation-insensitive
databases.

## `update` from `VALUES` find/replace pairs

Apply many substitutions in one statement rather than one `UPDATE` per pair:

```python
Book.objects.update_from(title=[('Colour', 'Color'), ('Grey', 'Gray')])
```

```sql
UPDATE book SET title = REPLACE(book.title, pairs.find, pairs.replace)
FROM (VALUES ('Colour', 'Color'), ('Grey', 'Gray')) AS pairs (find, replace)
WHERE book.title LIKE '%' || pairs.find || '%';
```

Chaining `Replace()` inside a single `update()` also avoids the 1 + N statements but rewrites
every row, and the SQL grows quadratically with the pair count. Joining against `VALUES` touches
only matching rows and keeps the pairs as data. Needs a fallback for databases without
`UPDATE ... FROM`.
