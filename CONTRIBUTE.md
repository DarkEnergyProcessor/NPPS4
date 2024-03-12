Contribute
=====

Code Style
-----

Python code must be formated using [`black`](https://github.com/psf/black) with maximum line length of 120 characters
(`-l 120`). All Python files submitted for PR MUST be formatted with `black` formatter. It's STRONGLY RECOMMENDED to
configure your text editor/IDE of your choice to reformat the Python code when saving using `black`.

There are certain rules for `import` rules, which are:

1. The order of imports are: Python standard library (`typing` has specialized rules, see (7)), 3rd-party libraries,
current project relative import, and `typing` classes. Separated by empty lines.

2. For Python standard library and 3rd-party libraries, the only accepted notation is `import ...`.
`from ... import ...` is strongly prohibited even if this means increasing the column length significantly.

3. For current project relative import, if the Python file reside inside the project, then use `from ... import ...`
notation. If the Python file is outside the project, but still part of the project (e.g. Python scripts in
`external/`), then the standard `import ...` notation is used.

4. When using `from ... import ...` notation (only for current project relative import), it's not allowed to import
the individual variable, function, and/or classes. Always import the whole module directly.

5. On name conflicts with import, use `as` keyword to rename the import module or try to prevent name conflicts when
possible. An example for this situation can be seen in `npps4/game/lbonus.py`.

6. The order of each imports in their respective category are in lexicographic order. For `from ... import ...`
notation, it first ordered by the `from ...` then the `import ...`. See below for valid example.

7. `typing` module is specialized in this rule.
   * For type hint classes, import the needed classes or function directly using `from typing import ...` notation.
     As per (1), `typing` import goes last after everything else.
   * When using the introspection function such as `get_args`, the `typing` module is treated as Python standard
     library. Note that `overload` and `cast` are not introspection functions.

8. Functions parameters must be type-annotated properly. While it's currently not enforced at runtime, this may
change in the future. Function return value may be type-annotated if your IDE or text editor cannot infer the return
type.

9. Type-annotate variables when your IDE or text editor cannot infer them correctly. Example on this one is having
variable that may contain list of integers (`list[int]`) but initialized as empty list (`[]`) to be populated later.

# Examples `import`

This is an example of well-formed imports.

```py
# Python standard library
import dataclasses
import json

# 3rd-party library
import pydantic
import sqlalchemy

# Current project relative import
from . import idol
from .config import config
from .system import background

# typing
from typing import Any, TypeVar, cast
```

Database Migration
-----

When changing the main database tables, run migration:

```
alembic revision --autogenerate -m "your message revision here"
```

If your changes alter the database fields/tables, please state them in the Pull Request and don't send the alembic
migration file. If by accident you sent the alembic migration file, then they'll be deleted or altered significantly
on next commit.
