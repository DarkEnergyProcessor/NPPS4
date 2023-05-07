from .. import idol
from .. import util

import pydantic


class RemovableSkillInfoResponse(pydantic.BaseModel):
    owning_info: list
    equipment_info: list


class SupporterInfoResponse(pydantic.BaseModel):
    unit_support_list: list


class UnitInfoResponse(pydantic.BaseModel):
    active: list
    waiting: list


@idol.register("/unit/deckInfo")
def unit_deckinfo(context: idol.SchoolIdolUserParams):
    # TODO
    util.log("STUB /unit/deckInfo", severity=util.logging.WARNING)
    return pydantic.BaseModel()


@idol.register("/unit/removableSkillInfo")
def unit_removableskillinfo(context: idol.SchoolIdolUserParams) -> RemovableSkillInfoResponse:
    # TODO
    util.log("STUB /unit/removableSkillInfo", severity=util.logging.WARNING)
    return RemovableSkillInfoResponse(owning_info=[], equipment_info=[])


@idol.register("/unit/supporterAll")
def unit_supporterall(context: idol.SchoolIdolUserParams) -> SupporterInfoResponse:
    # TODO
    util.log("STUB /unit/supporterAll", severity=util.logging.WARNING)
    return SupporterInfoResponse(unit_support_list=[])


def unit_unitall(context: idol.SchoolIdolUserParams) -> UnitInfoResponse:
    # TODO
    util.log("STUB /unit/unitAll", severity=util.logging.WARNING)
    return UnitInfoResponse(active=[], waiting=[])
