import pydantic

from . import item_model
from .. import const


class AdditionalScenarioStatus(pydantic.BaseModel):
    scenario_id: int
    status: int = 1


class ScenarioItem(item_model.Item):
    add_type: const.ADD_TYPE = const.ADD_TYPE.SCENARIO
    amount: int = 1

    @pydantic.computed_field
    @property
    def additional_scenario_status(self) -> AdditionalScenarioStatus:
        return AdditionalScenarioStatus(scenario_id=self.item_id)
