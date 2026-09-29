
from farmer_base import agent as _farmer_parent
from shop_overlay import GodModeShopOverlay

_CONTROLLER = GodModeShopOverlay(_farmer_parent)

def agent(observation, configuration=None):
    return _CONTROLLER(observation, configuration)

agent.telemetry = _CONTROLLER.telemetry
