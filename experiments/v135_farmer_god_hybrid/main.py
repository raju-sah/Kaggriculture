"""V135 Hybrid Sovereign: Farmer John 1010 Fixed-Point Engine + God's Mode Shop Overlay."""

from base_agent import agent as _farmer_parent
from shop_overlay import GodModeShopOverlay

_CONTROLLER = GodModeShopOverlay(_farmer_parent)

def agent(observation, configuration=None):
    return _CONTROLLER(observation, configuration)

agent.telemetry = _CONTROLLER.telemetry
