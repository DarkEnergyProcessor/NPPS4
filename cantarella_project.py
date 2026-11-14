import csv
import io
import pathlib

import aiosqlite

import cantarella.api  # type: ignore


def _addfile(project: cantarella.api.Project, file: str) -> str | None:
    path: pathlib.Path = project.resolve(file)
    if path.is_file():
        return path.read_text(encoding="utf-8")

    return None


@cantarella.api.prefill(0)
def add_agents_md(project: cantarella.api.Project) -> str | None:
    return _addfile(project, "AGENTS.md")


@cantarella.api.prefill(0)
def add_code_style(project: cantarella.api.Project) -> str | None:
    return _addfile(project, "CONTRIBUTE.md")


npps4_tools = cantarella.api.define_tool_group("npps4", title="NPPS4", description="NPPS4-Specific Tools")


@cantarella.api.define_tool(group=npps4_tools, side_effects="none")
async def npps4_query_gamedb(project: cantarella.api.Project, gamedbname: str, query: str) -> tuple[bool, str]:
    """
    Run SQLite3 query `query` on the specified game database `gamedbname` and return the result as CSV. `gamedbname`
    requires only the name, no fullpath, with or without `.db_` extension. Only returns if the query has result
    (e.g. SELECT).

    Database is opened in read-only mode.
    """

    if gamedbname.endswith(".db_"):
        gamedbname = gamedbname[:-4]
    dbfile: pathlib.Path = project.resolve(f"data/db/59.4/{gamedbname}.db_").resolve()
    if not dbfile.is_file():
        return False, f"Database {gamedbname} not found. Put decrypted DB in data/db/59.4"

    async with aiosqlite.connect(f"{dbfile.as_uri()}?mode=ro", uri=True) as db:
        async with await db.execute(query) as cursor:
            if cursor.description is not None:
                columns = [col[0] for col in cursor.description]
                with io.StringIO(newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(columns)
                    async for row in cursor:
                        writer.writerow(row)

                    return True, f.getvalue()

    return False, "Query has no result set."
