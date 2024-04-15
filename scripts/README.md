Scripts
=====

Scripts are code that performs automated tasks to NPPS4 itself.

To run the scripts directly like ordinary Python scripts, run this once in virtual environment:
```
pip install -e .
```

Then you can run them like ordinary scripts (e.g. `python script.py ...`)

If you don't want to do `pip install -e .`, then to run script, you must run it like this:
```
python -m npps4.script script.py ...
```

Will run `script.py` in the working directory.
