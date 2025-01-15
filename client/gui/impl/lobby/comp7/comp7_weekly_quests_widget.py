# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/comp7_weekly_quests_widget.py
import logging
import typing
from shared_utils import findFirst
from account_helpers import AccountSettings
from account_helpers.AccountSettings import COMP7_UI_SECTION, COMP7_WEEKLY_QUEST_WIDGET_PROGRESS, COMP7_WEEKLY_QUEST_IN_WIDGET_ID, COMP7_WEEKLY_QUEST_IN_WIDGET_STATE
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.comp7.enums import MetaRootViews
from gui.impl.gen.view_models.views.lobby.missions.widget.comp7_daily_quest_model import State
from gui.impl.lobby.comp7.comp7_quest_helpers import hasAvailableWeeklyQuestsOfferGiftTokens
from gui.impl.lobby.comp7.tooltips.weekly_quest_tooltip import WeeklyQuestTooltip
from gui.impl.lobby.missions.daily_quests_widget_view import DailyQuestsWidgetView
from gui.shared import event_dispatcher
from gui.shared.missions.packers.events import Comp7WeeklyQuestPacker
from helpers import dependency
from skeletons.gui.game_control import IComp7WeeklyQuestsController
if typing.TYPE_CHECKING:
    from typing import Optional
    from frameworks.wulf import ViewEvent, View
    from gui.game_control.comp7_weekly_quests_controller import _Comp7WeeklyQuests
    from gui.impl.gen.view_models.views.lobby.missions.widget.comp7_daily_quest_model import Comp7DailyQuestModel
    from gui.impl.gen.view_models.views.lobby.missions.widget.daily_quests_widget_view_model import DailyQuestsWidgetViewModel
    from gui.impl.gen.view_models.views.lobby.missions.widget.widget_quest_model import WidgetQuestModel
_logger = logging.getLogger(__name__)

class Comp7WeeklyQuestsWidgetView(DailyQuestsWidgetView):
    __comp7WeeklyQuestsCtrl = dependency.descriptor(IComp7WeeklyQuestsController)

    def _onLoading(self, *args, **kwargs):
        self._updateViewModel(True)
        self.__addListeners()

    def _finalize(self):
        super(Comp7WeeklyQuestsWidgetView, self)._finalize()
        self.__removeListeners()

    def createToolTipContent(self, event, contentID):
        return WeeklyQuestTooltip() if contentID == R.views.lobby.comp7.tooltips.WeeklyQuestTooltip() else super(Comp7WeeklyQuestsWidgetView, self).createToolTipContent(event, contentID)

    def setVisible(self, value):
        super(Comp7WeeklyQuestsWidgetView, self).setVisible(value)
        if not value:
            with self.getViewModel().transaction() as tx:
                questsArray = tx.getQuests()
                for questModel in questsArray:
                    questModel.setCompleted(True)

    def _updateViewModel(self, onLoading=False):
        super(Comp7WeeklyQuestsWidgetView, self)._updateViewModel()
        self.viewModel.setIsComp7Hangar(True)
        self.__updateWeeklyQuest(onLoading)

    def __updateWeeklyQuest(self, onLoading=False):
        with self.getViewModel().transaction() as tx:
            model = tx.comp7DailyQuest
            weeklyQuests = self.__comp7WeeklyQuestsCtrl.getQuests()
            model.setState(weeklyQuests.newQuestState)
            if weeklyQuests.newQuestState == State.HIDE:
                return
            model.setQuestsCompleted(weeklyQuests.numCompletedBattleQuests)
            model.setTotalQuestsCount(weeklyQuests.numBattleQuests)
            model.setTimeLeftToNewQuests(weeklyQuests.getTimeToNewQuests())
            if onLoading:
                self.__setInitQuestModelData(model)
            else:
                self.__setQuestModelData(model)

    def __setQuestModelData(self, model):
        quest = self.__comp7WeeklyQuestsCtrl.getQuests().newQuest
        state = self.__comp7WeeklyQuestsCtrl.getQuests().newQuestState
        icon, currentProgress, totalProgress, description = Comp7WeeklyQuestPacker.getData(quest)
        model.setIcon(icon)
        model.setCurrentProgress(currentProgress)
        model.setTotalProgress(totalProgress)
        model.setDescription(description)
        if quest:
            model.setId(quest.getID())
            model.setCompleted(quest.isCompleted())
            prevId, prevProgress, _ = self.__getSettingsData()
            questId = quest.getID()
            if questId and prevId == questId:
                earned = currentProgress - prevProgress
            else:
                earned = currentProgress
            model.setEarned(earned)
            self.__setSettingsData(questId, currentProgress, state)
        else:
            emptyId = ''
            model.setId(emptyId)
            self.__setSettingsData(emptyId, 0, state)

    def __setInitQuestModelData(self, model):
        questId, progress, state = self.__getSettingsData()
        if not questId:
            self.__setQuestModelData(model)
            return
        else:
            quests = self.__comp7WeeklyQuestsCtrl.getQuests().sortedBattleQuests
            questData = findFirst(lambda qData: qData[1].getID() == questId, quests) if quests else None
            if not questData:
                _logger.warning('No quest for saved comp7 questID found')
                return
            _, quest = questData
            icon, _, totalProgress, description = Comp7WeeklyQuestPacker.getData(quest)
            model.setId(quest.getID())
            model.setIcon(icon)
            model.setDescription(description)
            model.setCurrentProgress(progress)
            model.setTotalProgress(totalProgress)
            model.setEarned(progress)
            model.setCompleted(progress >= totalProgress)
            model.setState(state)
            if quest.isCompleted():
                model.setQuestsCompleted(self.__comp7WeeklyQuestsCtrl.getQuests().numCompletedBattleQuests - 1)
            return

    def __addListeners(self):
        self.__comp7WeeklyQuestsCtrl.onWeeklyQuestsUpdated += self.__onWeeklyQuestsUpdated
        self.getViewModel().comp7DailyQuest.onViewLoaded += self.__onWidgetLoaded
        self.getViewModel().comp7DailyQuest.onClick += self.__onComp7QuestClicked

    def __removeListeners(self):
        self.__comp7WeeklyQuestsCtrl.onWeeklyQuestsUpdated -= self.__onWeeklyQuestsUpdated
        self.getViewModel().comp7DailyQuest.onViewLoaded -= self.__onWidgetLoaded
        self.getViewModel().comp7DailyQuest.onClick -= self.__onComp7QuestClicked

    def __onWidgetLoaded(self):
        self.__updateWeeklyQuest()

    @staticmethod
    def __onComp7QuestClicked():
        if hasAvailableWeeklyQuestsOfferGiftTokens():
            event_dispatcher.showComp7WeeklyQuestsRewardsSelectionWindow()
        else:
            event_dispatcher.showComp7MetaRootView(MetaRootViews.WEEKLYQUESTS)

    def __onWeeklyQuestsUpdated(self, _):
        self.__updateWeeklyQuest()

    def __getSettingsData(self):
        settings = AccountSettings.getUIFlag(COMP7_UI_SECTION)
        questId = settings.get(COMP7_WEEKLY_QUEST_IN_WIDGET_ID, '')
        progress = settings.get(COMP7_WEEKLY_QUEST_WIDGET_PROGRESS, 0)
        stateStr = settings.get(COMP7_WEEKLY_QUEST_IN_WIDGET_STATE, '')
        state = State(stateStr) if stateStr else State.ACTIVE
        return (questId, progress, state)

    def __setSettingsData(self, questId, progress, state):
        settings = AccountSettings.getUIFlag(COMP7_UI_SECTION)
        settings[COMP7_WEEKLY_QUEST_IN_WIDGET_ID] = questId
        settings[COMP7_WEEKLY_QUEST_WIDGET_PROGRESS] = progress
        settings[COMP7_WEEKLY_QUEST_IN_WIDGET_STATE] = state.value
        AccountSettings.setUIFlag(COMP7_UI_SECTION, settings)
