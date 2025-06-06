# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/battle_results/composer.py
from functools import partial
from logging import getLogger
import BigWorld
from gui.battle_results.stats_ctrl import IBattleResultStatsCtrl
from gui.battle_results.settings import PLAYER_TEAM_RESULT
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from story_mode.gui.battle_results.templates import STORY_MODE_RESULTS_BLOCK
from story_mode.gui.shared.event_dispatcher import showEpilogueWindow, showOnboardingBattleResultWindow, showPrebattleAndGoToQueue, showBattleResultWindow, showOutroVideo
from story_mode.skeletons.story_mode_controller import IStoryModeController
from story_mode_common.story_mode_constants import LOGGER_NAME
_logger = getLogger(LOGGER_NAME)

class StoryModeStatsComposer(IBattleResultStatsCtrl):
    _storyModeCtrl = dependency.descriptor(IStoryModeController)
    _lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, _):
        super(StoryModeStatsComposer, self).__init__()
        self._block = STORY_MODE_RESULTS_BLOCK.clone()

    def clear(self):
        self._block.clear()

    def setResults(self, results, reusable):
        self._block.setRecord(results, reusable)

    def getVO(self):
        return self._block.getVO()

    @staticmethod
    def onShowResults(arenaUniqueID):
        pass

    def onResultsPosted(self, arenaUniqueID):
        resultVO = self._block.getVO()
        if resultVO['isForceOnboarding']:
            if not self._storyModeCtrl.isEnabled():
                self._storyModeCtrl.quitBattle()
                return
            BigWorld.callback(0, partial(self._processOnboardingResults, resultVO))
        else:
            ctx = self._lobbyContext.getGuiCtx()
            if ctx.get('skipHangar', False) and ctx.get('showOutroVideo', False):
                showOutroVideo(resultVO['missionId'], arenaUniqueID)
            else:
                showBattleResultWindow(arenaUniqueID)

    def _processOnboardingResults(self, resultVO):
        missionId = resultVO['missionId']
        if resultVO['finishResult'] == PLAYER_TEAM_RESULT.WIN:
            nextMission = self._storyModeCtrl.getNextMission(missionId)
            if missionId == self._storyModeCtrl.missions.onboardingLastMissionId or nextMission is None:
                showEpilogueWindow()
            else:
                showPrebattleAndGoToQueue(missionId=nextMission.missionId)
        else:
            showOnboardingBattleResultWindow(finishReason=resultVO['finishReason'], missionId=missionId)
        return
