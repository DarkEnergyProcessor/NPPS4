import pydantic


class MuseumParameterData(pydantic.BaseModel):
    smile: int = 0  # TODO
    pure: int = 0  # TODO
    cool: int = 0  # TODO


class MuseumInfoData(pydantic.BaseModel):
    parameter: MuseumParameterData
    contents_id_list: list[int]
