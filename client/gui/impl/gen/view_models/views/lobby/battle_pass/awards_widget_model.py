# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/awards_widget_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.collection_entry_point_view_model import CollectionEntryPointViewModel

class AwardsWidgetModel(ViewModel):
    __slots__ = ('onBpcoinClick', 'onTakeRewardsClick', 'showTankmen', 'showTickets', 'showTalers')

    def __init__(self, properties=10, commands=5):
        super(AwardsWidgetModel, self).__init__(properties=properties, commands=commands)

    @property
    def collectionEntryPoint(self):
        return self._getViewModel(0)

    @staticmethod
    def getCollectionEntryPointType():
        return CollectionEntryPointViewModel

    def getTalerCount(self):
        return self._getNumber(1)

    def setTalerCount(self, value):
        self._setNumber(1, value)

    def getNotChosenRewardCount(self):
        return self._getNumber(2)

    def setNotChosenRewardCount(self, value):
        self._setNumber(2, value)

    def getBpcoinCount(self):
        return self._getNumber(3)

    def setBpcoinCount(self, value):
        self._setNumber(3, value)

    def getTicketsCount(self):
        return self._getNumber(4)

    def setTicketsCount(self, value):
        self._setNumber(4, value)

    def getIsChooseRewardsEnabled(self):
        return self._getBool(5)

    def setIsChooseRewardsEnabled(self, value):
        self._setBool(5, value)

    def getIsSpecialVoiceTankmenEnabled(self):
        return self._getBool(6)

    def setIsSpecialVoiceTankmenEnabled(self, value):
        self._setBool(6, value)

    def getIsTalerEnabled(self):
        return self._getBool(7)

    def setIsTalerEnabled(self, value):
        self._setBool(7, value)

    def getIsBpCoinEnabled(self):
        return self._getBool(8)

    def setIsBpCoinEnabled(self, value):
        self._setBool(8, value)

    def getIsTicketsEnabled(self):
        return self._getBool(9)

    def setIsTicketsEnabled(self, value):
        self._setBool(9, value)

    def _initialize(self):
        super(AwardsWidgetModel, self)._initialize()
        self._addViewModelProperty('collectionEntryPoint', CollectionEntryPointViewModel())
        self._addNumberProperty('talerCount', 0)
        self._addNumberProperty('notChosenRewardCount', 0)
        self._addNumberProperty('bpcoinCount', 0)
        self._addNumberProperty('ticketsCount', 0)
        self._addBoolProperty('isChooseRewardsEnabled', True)
        self._addBoolProperty('isSpecialVoiceTankmenEnabled', False)
        self._addBoolProperty('isTalerEnabled', False)
        self._addBoolProperty('isBpCoinEnabled', False)
        self._addBoolProperty('isTicketsEnabled', False)
        self.onBpcoinClick = self._addCommand('onBpcoinClick')
        self.onTakeRewardsClick = self._addCommand('onTakeRewardsClick')
        self.showTankmen = self._addCommand('showTankmen')
        self.showTickets = self._addCommand('showTickets')
        self.showTalers = self._addCommand('showTalers')
