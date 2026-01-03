import npps4.script_dummy  # isort:skip

import argparse
import collections.abc
import dataclasses
import os.path
import runpy

import sqlalchemy

import npps4.db.achievement
import npps4.db.effort
import npps4.db.exchange
import npps4.db.game_mater
import npps4.db.item
import npps4.db.live
import npps4.db.main
import npps4.db.museum
import npps4.db.scenario
import npps4.db.subscenario
import npps4.db.unit
import npps4.idol

from typing import Callable, TypedDict, cast

SCRIPT_DIR = os.path.dirname(__file__)
FIXES_DIR = os.path.join(SCRIPT_DIR, "migrations")


class FixesModule(TypedDict):
    revision: str
    prev_revision: str | None
    main: Callable[[npps4.idol.BasicSchoolIdolContext], collections.abc.Awaitable[None]]


@dataclasses.dataclass(kw_only=True)
class ScriptInfo:
    module: FixesModule
    previous: "ScriptInfo | None"
    next: "ScriptInfo | None"


def load_fixes_script():
    result: dict[str, ScriptInfo] = {}

    # Load revisions
    for info in os.scandir(FIXES_DIR):
        if not info.is_file():
            continue

        _, ext = os.path.splitext(info.name)
        ext = ext.lower()
        if ext != ".py" or ext != ".pyc":
            continue

        module = runpy.run_path(info.path)
        for key in FixesModule.__required_keys__:
            if key not in module:
                raise KeyError(f"File '{info.path}' has missing key '{key}'")

        module_typed: FixesModule = cast(FixesModule, module)
        if module_typed["revision"] in result:
            raise ValueError(f"Revision '{module_typed['revision']}' already exist")

        sinfo = ScriptInfo(module=module_typed, previous=None, next=None)
        result[module_typed["revision"]] = sinfo

    # Link graph
    for rev, sinfo in result.items():
        if sinfo.module["prev_revision"] is not None:
            prev = result.get(sinfo.module["prev_revision"])

            if prev is None:
                raise KeyError(f"Revision '{rev}' points to undefined revision '{sinfo.module["prev_revision"]}'")

            if prev.next is not None:
                raise KeyError(
                    f"Revision '{sinfo.module["prev_revision"]}' has multiple branches: '{prev.next.module["revision"]}' and '{rev}'"
                )

            prev.next = sinfo
            sinfo.previous = prev

    return result


async def run_apply(revisions: dict[str, ScriptInfo], echo: bool):
    # Find first None target (this does not verify if there are multiple dangling revision)
    current_target = await get_starting_revision(revisions)
    if current_target is None:
        return

    for module in (
        npps4.db.achievement,
        npps4.db.effort,
        npps4.db.exchange,
        npps4.db.game_mater,
        npps4.db.item,
        npps4.db.live,
        npps4.db.main,
        npps4.db.museum,
        npps4.db.scenario,
        npps4.db.subscenario,
        npps4.db.unit,
    ):
        module.engine.echo = echo

    async with npps4.idol.BasicSchoolIdolContext(lang=npps4.idol.Language.en) as context:
        q = sqlalchemy.select(npps4.db.main.MigrationFixes).limit(1)
        result = await context.db.main.execute(q)
        fixes = result.scalar()

        if fixes is None:
            # Run first revision
            print(f"Applying '{current_target.module["revision"]}")
            await current_target.module["main"](context)
            fixes = npps4.db.main.MigrationFixes(revision=current_target.module["revision"])
            context.db.main.add(fixes)
            current_target = current_target.next
        else:
            if fixes.revision not in revisions:
                raise RuntimeError(f"Fixes revision is at '{fixes.revision}' but it's unknown")

            current_target = revisions[fixes.revision].next

        while current_target is not None:
            print(f"Applying '{current_target.module["revision"]}")
            await current_target.module["main"](context)
            fixes.revision = current_target.module["revision"]
            current_target = current_target.next


async def get_starting_revision(revisions: dict[str, ScriptInfo]):
    if not revisions:
        return None

    # Find starting revision
    starting_revisions = [r for r in revisions.values() if r.previous is None]

    match len(starting_revisions):
        case 0:
            raise RuntimeError("Fully cyclic revision")
        case 1:
            pass
        case _:
            raise RuntimeError(
                "Multiple starting or disjointed revisions detected: "
                + ", ".join(r.module["revision"] for r in starting_revisions)
            )

    ending_revisions = [r for r in revisions.values() if r.next is None]

    match len(ending_revisions):
        case 0:
            raise RuntimeError("Fully cyclic revision")
        case 1:
            pass
        case _:
            raise RuntimeError(
                "Multiple ending or disjointed revisions detected: "
                + ", ".join(r.module["revision"] for r in ending_revisions)
            )

    return starting_revisions[0]


async def run_script(arg: list[str]):
    parser = argparse.ArgumentParser(__file__)
    parser.add_argument("--echo", action="store_true", help="Emit SQLAlchemy statements")

    args = parser.parse_args(arg)
    revisions = load_fixes_script()

    await run_apply(revisions, args.echo)


if __name__ == "__main__":
    import npps4.scriptutils.boot

    npps4.scriptutils.boot.start(run_script)
