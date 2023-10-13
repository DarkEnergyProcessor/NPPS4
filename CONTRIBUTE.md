Contribute
=====

Code Style
-----

Python code is formated using [`black`](https://github.com/psf/black). Install `black` and set it to format on save
with maximum line length of 120 characters (`-l 120`).

There are additional rules for contributors:

* Order of the imports are: Python stdlib, 3rd-party lib, then relative imports. Separated by empty lines.

* Never use `from ... import ...` both for Python standard library and 3rd-party library. Some might argue that this will
increase the line column length significantly but this makes it clear which module is used when reading the code.

* Only use `from ... import ...` for relative imports. Even in this case, it's not allowed to import function directly. Thus,
`from ... import some.func` is also not allowed under any circumstances. **Import the module directly!**

* 3 above `import` rules doesn't apply to `typing` module, unless you want to use helper function (e.g. `get_args`) for it. `from typing import ...` is always the last imports!

* Annotate variables and function as good as possible. When using VS Code with Python extension, consider activating basic type checking.

Database Migration
-----

When changing the main database tables, run migration:

```
alembic revision --autogenerate -m "your message revision here"
```
