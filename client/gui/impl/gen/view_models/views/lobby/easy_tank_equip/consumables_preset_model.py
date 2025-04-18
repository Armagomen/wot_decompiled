# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/easy_tank_equip/consumables_preset_model.py
from enum import Enum
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.easy_tank_equip.common.preset_model import PresetModel
from gui.impl.gen.view_models.views.lobby.easy_tank_equip.consumables_preset_slot_model import ConsumablesPresetSlotModel

class ConsumablesPresetType(Enum):
    STANDARD = 'standard'
    ADVANCED = 'advanced'
    IMPROVED = 'improved'


class ConsumablesPresetModel(PresetModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(ConsumablesPresetModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return ConsumablesPresetType(self._getString(5))

    def setType(self, value):
        self._setString(5, value.value)

    def getItems(self):
        return self._getArray(6)

    def setItems(self, value):
        self._setArray(6, value)

    @staticmethod
    def getItemsType():
        return ConsumablesPresetSlotModel

    def _initialize(self):
        super(ConsumablesPresetModel, self)._initialize()
        self._addStringProperty('type')
        self._addArrayProperty('items', Array())
