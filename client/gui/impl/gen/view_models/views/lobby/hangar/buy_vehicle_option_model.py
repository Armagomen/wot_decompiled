# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/hangar/buy_vehicle_option_model.py
from enum import Enum
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.hangar.buy_vehicle_price_model import BuyVehiclePriceModel
from gui.impl.gen.view_models.views.lobby.hangar.buy_vehicle_simple_tooltip_model import BuyVehicleSimpleTooltipModel

class OptionState(Enum):
    DEFAULT = 'default'
    WARNING = 'warning'
    SELECTED = 'selected'
    DISABLED = 'disabled'


class BuyVehicleOptionModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(BuyVehicleOptionModel, self).__init__(properties=properties, commands=commands)

    @property
    def price(self):
        return self._getViewModel(0)

    @staticmethod
    def getPriceType():
        return BuyVehiclePriceModel

    @property
    def tooltip(self):
        return self._getViewModel(1)

    @staticmethod
    def getTooltipType():
        return BuyVehicleSimpleTooltipModel

    def getName(self):
        return self._getString(2)

    def setName(self, value):
        self._setString(2, value)

    def getOptionState(self):
        return OptionState(self._getString(3))

    def setOptionState(self, value):
        self._setString(3, value.value)

    def getIcon(self):
        return self._getResource(4)

    def setIcon(self, value):
        self._setResource(4, value)

    def getTitle(self):
        return self._getString(5)

    def setTitle(self, value):
        self._setString(5, value)

    def getIsPriceVisible(self):
        return self._getBool(6)

    def setIsPriceVisible(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(BuyVehicleOptionModel, self)._initialize()
        self._addViewModelProperty('price', BuyVehiclePriceModel())
        self._addViewModelProperty('tooltip', BuyVehicleSimpleTooltipModel())
        self._addStringProperty('name', '')
        self._addStringProperty('optionState')
        self._addResourceProperty('icon', R.invalid())
        self._addStringProperty('title', '')
        self._addBoolProperty('isPriceVisible', False)
