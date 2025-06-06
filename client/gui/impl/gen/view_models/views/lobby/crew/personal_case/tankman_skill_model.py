# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/personal_case/tankman_skill_model.py
from enum import Enum
from gui.impl.gen.view_models.views.lobby.crew.common.skill.skill_extended_model import SkillExtendedModel

class AnimationType(Enum):
    NONE = 'none'
    UNLOCKED = 'unlocked'
    SELECTED = 'selected'


class TankmanSkillModel(SkillExtendedModel):
    __slots__ = ()

    def __init__(self, properties=13, commands=0):
        super(TankmanSkillModel, self).__init__(properties=properties, commands=commands)

    def getIsDisabled(self):
        return self._getBool(9)

    def setIsDisabled(self, value):
        self._setBool(9, value)

    def getIsLocked(self):
        return self._getBool(10)

    def setIsLocked(self, value):
        self._setBool(10, value)

    def getWotPlusAssistHintCandidate(self):
        return self._getBool(11)

    def setWotPlusAssistHintCandidate(self, value):
        self._setBool(11, value)

    def getAnimationType(self):
        return AnimationType(self._getString(12))

    def setAnimationType(self, value):
        self._setString(12, value.value)

    def _initialize(self):
        super(TankmanSkillModel, self)._initialize()
        self._addBoolProperty('isDisabled', False)
        self._addBoolProperty('isLocked', False)
        self._addBoolProperty('wotPlusAssistHintCandidate', False)
        self._addStringProperty('animationType', AnimationType.NONE.value)
