# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_loading/state_machine/states/init_client/client_loading.py
import typing
import game_loading_bindings
from frameworks.state_machine import StateFlags
from gui.game_loading import loggers
from gui.game_loading.state_machine.const import GameLoadingStates, TickingMode
from gui.game_loading.state_machine.models import ImageViewSettingsModel
from gui.game_loading.state_machine.states.base import BaseGroupTickingStates
from gui.game_loading.state_machine.states.components.progress_bar import ProgressBarStateComponent
from gui.game_loading.state_machine.states.components.status_text import MilestoneStatusTextStateComponent
from gui.game_loading.state_machine.states.slide import SlideState
if typing.TYPE_CHECKING:
    from gui.game_loading.resources.cdn.images import CdnImagesResources
    from gui.game_loading.preferences import GameLoadingPreferences
    from gui.game_loading.state_machine.models import ProgressSettingsModel as PSM
_logger = loggers.getStatesLogger()

class ClientLoadingSlideState(SlideState):
    __slots__ = ()

    def __init__(self, images, viewSettings):
        super(ClientLoadingSlideState, self).__init__(stateID=GameLoadingStates.CLIENT_INIT_LOADING_SLIDE.value, flags=StateFlags.UNDEFINED, images=images, imageViewSettings=viewSettings, tickingMode=TickingMode.BOTH, onCompleteEvent=None)
        return


class ClientLoadingProgressStateComponent(ProgressBarStateComponent):
    __slots__ = ('_stepsBegin',)

    def __init__(self, preferences, progressSettings):
        super(ClientLoadingProgressStateComponent, self).__init__(stateID=GameLoadingStates.CLIENT_INIT_LOADING_PROGRESS.value, flags=StateFlags.UNDEFINED, settings=progressSettings, preferences=preferences, tickingMode=TickingMode.BOTH, onCompleteEvent=None)
        self._stepsBegin = 0
        return

    def _increaseTicks(self):
        super(ClientLoadingProgressStateComponent, self)._increaseTicks()
        if self._stepsBegin == 0 and self._stepNumber != 0:
            self._stepsBegin = self._stepNumber
        self._ticks = max(self._stepNumber - self._stepsBegin, self._ticks)

    def _increaseProgress(self):
        percents = 100 * self._ticks / float(self._progressMax)
        self._setProgress(self._calcProgress(percents))


class ClientLoadingStatusTextStateComponent(MilestoneStatusTextStateComponent):
    __slots__ = ()

    def __init__(self, milestonesSettings):
        super(ClientLoadingStatusTextStateComponent, self).__init__(stateID=GameLoadingStates.CLIENT_INIT_LOADING_STATUS.value, flags=StateFlags.UNDEFINED, milestonesSettings=milestonesSettings, tickingMode=TickingMode.BOTH, onCompleteEvent=None)
        return


class ClientLoadingState(BaseGroupTickingStates):
    __slots__ = ()

    def __init__(self):
        super(ClientLoadingState, self).__init__(stateID=GameLoadingStates.CLIENT_INIT_LOADING.value, flags=StateFlags.PARALLEL | StateFlags.UNDEFINED)

    @property
    def mainState(self):
        return self.getChildByIndex(0)

    def configure(self, preferences, images, milestonesSettings, progressSetting, viewSettings):
        clientLoadingSlideState = ClientLoadingSlideState(images=images, viewSettings=viewSettings)
        clientLoadingProgressComponent = ClientLoadingProgressStateComponent(preferences=preferences, progressSettings=progressSetting)
        clientLoadingStatusTextComponent = ClientLoadingStatusTextStateComponent(milestonesSettings=milestonesSettings)
        clientLoadingSlideState.configure()
        clientLoadingProgressComponent.configure()
        clientLoadingStatusTextComponent.configure()
        self.addChildState(clientLoadingSlideState)
        self.addChildState(clientLoadingProgressComponent)
        self.addChildState(clientLoadingStatusTextComponent)

    def _onEntered(self):
        super(ClientLoadingState, self)._onEntered()
        game_loading_bindings.bringLoadingViewToTop()
