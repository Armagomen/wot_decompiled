# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/hangar_presets/__init__.py
from constants import QUEUE_TYPE
from gui.hangar_presets.hangar_presets_reader import DefaultPresetReader, SpecBattlePresetReader
from gui.hangar_presets.hangar_presets_getters import DefaultPresetsGetter, EventPresetsGetter, RankedPresetsGetter, MapboxPresetsGetter, MapsTrainingPresetsGetter, WinbackPresetsGetter, RandomNP2PresetsGetter, SpecBattlePresetsGetter, RandomPresetsGetter
from gui.shared.system_factory import registerHangarPresetsReader, registerHangarPresetGetter
registerHangarPresetsReader(DefaultPresetReader)
registerHangarPresetsReader(SpecBattlePresetReader)
registerHangarPresetGetter(QUEUE_TYPE.RANDOMS, RandomPresetsGetter)
registerHangarPresetGetter(QUEUE_TYPE.EVENT_BATTLES, EventPresetsGetter)
registerHangarPresetGetter(QUEUE_TYPE.RANKED, RankedPresetsGetter)
registerHangarPresetGetter(QUEUE_TYPE.MAPBOX, MapboxPresetsGetter)
registerHangarPresetGetter(QUEUE_TYPE.MAPS_TRAINING, MapsTrainingPresetsGetter)
registerHangarPresetGetter(QUEUE_TYPE.WINBACK, WinbackPresetsGetter)
registerHangarPresetGetter(QUEUE_TYPE.RANDOM_NP2, RandomNP2PresetsGetter)
registerHangarPresetGetter(QUEUE_TYPE.SPEC_BATTLE, SpecBattlePresetsGetter)
