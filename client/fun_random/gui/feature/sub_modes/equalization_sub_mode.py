# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/feature/sub_modes/equalization_sub_mode.py
from battle_modifiers.gui.feature.modifiers_data_provider import ModifiersDataProvider
from fun_random.gui.feature.sub_modes.base_sub_mode import FunBaseSubMode
EQUALIZATION = 'equalization'

class EqualizationModifiersDataProvider(ModifiersDataProvider):

    def getDomains(self):
        return (EQUALIZATION,) + super(EqualizationModifiersDataProvider, self).getDomains()


class FunEqualizationSubMode(FunBaseSubMode):

    def __init__(self, subModeSettings):
        super(FunEqualizationSubMode, self).__init__(subModeSettings)
        self._modifiersDataProvider = EqualizationModifiersDataProvider(subModeSettings.client.battleModifiersDescr)

    def _updateSettings(self, subModeSettings):
        super(FunEqualizationSubMode, self)._updateSettings(subModeSettings)
        self._modifiersDataProvider = EqualizationModifiersDataProvider(subModeSettings.client.battleModifiersDescr)
        return True
