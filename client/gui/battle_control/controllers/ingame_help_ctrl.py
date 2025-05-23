# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/ingame_help_ctrl.py
import typing
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKey
from gui.battle_control import event_dispatcher as gui_event_dispatcher
from skeletons.gui.app_loader import IAppLoader
from helpers import dependency
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.controllers.interfaces import IBattleController
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import GameEvent
from gui.shared.system_factory import collectIngameHelpPagesBuilders, collectIngameHelpPagesFilters
if typing.TYPE_CHECKING:
    from Vehicle import Vehicle

class IngameHelpController(IBattleController):
    __slots__ = ('__arenaVisitor', '__currentHintContext')
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, setup):
        super(IngameHelpController, self).__init__()
        self.__arenaVisitor = setup.arenaVisitor
        self.__currentHintContext = None
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.INGAME_HELP_CTRL

    def startControl(self, *args):
        g_eventBus.addListener(GameEvent.SHOW_BTN_HINT, self.__onShowBtnHint, scope=EVENT_BUS_SCOPE.GLOBAL)
        g_eventBus.addListener(GameEvent.HIDE_BTN_HINT, self.__onHideBtnHint, scope=EVENT_BUS_SCOPE.GLOBAL)

    def stopControl(self):
        g_eventBus.removeListener(GameEvent.SHOW_BTN_HINT, self.__onShowBtnHint, scope=EVENT_BUS_SCOPE.GLOBAL)
        g_eventBus.removeListener(GameEvent.HIDE_BTN_HINT, self.__onHideBtnHint, scope=EVENT_BUS_SCOPE.GLOBAL)
        self.__currentHintContext = self.__arenaVisitor = None
        return

    def showIngameHelp(self, vehicle):
        ctx = {'vehName': vehicle.typeDescriptor.type.userString if vehicle is not None else None}
        builders = collectIngameHelpPagesBuilders()
        buildFilters = collectIngameHelpPagesFilters(self.__arenaVisitor.getArenaGuiType())
        for buildFilter in buildFilters:
            builders = buildFilter.filter(builders)

        hasDetailedHelpScreen = any([ builder.collectHelpCtx(ctx, self.__arenaVisitor, vehicle) for builder in builders ])
        if hasDetailedHelpScreen:
            ctx['currentHintCtx'] = self.__currentHintContext
            ctx['builders'] = builders
            gui_event_dispatcher.toggleHelpDetailed(ctx)
        else:
            gui_event_dispatcher.toggleHelp()
        gui_event_dispatcher.toggleFullStats(False)
        return hasDetailedHelpScreen

    def canShow(self):
        battleApp = self.__appLoader.getDefBattleApp()
        return False if battleApp is None else not bool(battleApp.containerManager.getViewByKey(ViewKey(VIEW_ALIAS.INGAME_MENU)))

    def __onShowBtnHint(self, event):
        self.__currentHintContext = event.ctx.get('hintCtx')

    def __onHideBtnHint(self, _):
        self.__currentHintContext = None
        return
