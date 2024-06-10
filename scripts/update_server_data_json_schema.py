import json

import npps4.script_dummy  # Must be first
import npps4.data.schema


async def run_script(args: list[str]):
    schema = npps4.data.schema.SerializedServerData.model_json_schema()
    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    with open("npps4/server_data_schema.json", "w", encoding="utf-8", newline="") as f:
        json.dump(schema, f, indent="\t")


if __name__ == "__main__":
    import npps4.scriptutils.boot

    npps4.scriptutils.boot.start(run_script)
