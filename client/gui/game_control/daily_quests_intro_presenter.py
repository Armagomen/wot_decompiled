# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/daily_quests_intro_presenter.py
from account_helpers.AccountSettings import Winback
from frameworks.wulf import ViewStatus
from gui.impl.gen import R
from gui.shared import event_dispatcher
from gui.winback.winback_helpers import getWinbackSetting, setWinbackSetting
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IBattlePassController, IDailyQuestIntroPresenter, IWinbackController
from skeletons.gui.impl import IGuiLoader

class DailyQuestsIntroPresenter(IDailyQuestIntroPresenter):
    __slots__ = ()
    __settingsCore = dependency.descriptor(ISettingsCore)
    __guiLoader = dependency.descriptor(IGuiLoader)
    __winbackController = dependency.descriptor(IWinbackController)
    __battlePassController = dependency.descriptor(IBattlePassController)

    @property
    def parentViewLayoutID(self):
        return R.views.lobby.missions.Daily()

    def onLobbyStarted(self, *_):
        self.__addListeners()
        self.__update()

    def onAccountBecomeNonPlayer(self):
        self.__clearListeners()

    def fini(self):
        self.__clearListeners()

    def __addListeners(self):
        if self.__guiLoader.windowsManager is not None:
            self.__guiLoader.windowsManager.onViewStatusChanged += self.__onViewStatusChanged
        return

    def __clearListeners(self):
        if self.__guiLoader.windowsManager is not None:
            self.__guiLoader.windowsManager.onViewStatusChanged -= self.__onViewStatusChanged
        return

    def __onViewStatusChanged(self, uniqueID, newStatus):
        if newStatus == ViewStatus.LOADED:
            if self.__guiLoader.windowsManager.getView(uniqueID).layoutID == self.parentViewLayoutID:
                self.__update()

    def __update(self, *_):
        needToShowWinback = self.__isDailyQuestView() and self.__winbackController.isProgressionAvailable() and not self.__isWinbackIntroShown()
        if needToShowWinback:
            self.__showWinbackIntroScreen()

    def __isDailyQuestView(self):
        return self.__guiLoader.windowsManager.getViewByLayoutID(self.parentViewLayoutID) is not None

    def __isWinbackIntroShown(self):
        return getWinbackSetting(Winback.INTRO_SHOWN)

    def __showWinbackIntroScreen(self):
        event_dispatcher.showWinbackIntroView()
        setWinbackSetting(Winback.INTRO_SHOWN, True)
