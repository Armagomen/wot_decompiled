# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/vehicle_compare/skills_panel.py
import typing
from frameworks.wulf import ViewSettings, ViewFlags
from gui.Scaleform.daapi.view.lobby.vehicle_compare import cmp_helpers
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.common.skill.skill_simple_model import SkillSimpleModel
from gui.impl.gen.view_models.views.lobby.crew.common.tooltip_constants import TooltipConstants
from gui.impl.gen.view_models.views.lobby.vehicle_compare.compare_skills_panel_view_model import CompareSkillsPanelViewModel
from gui.impl.lobby.crew.crew_helpers.skill_helpers import getRoleBySkillName
from gui.impl.lobby.crew.crew_helpers.skill_model_setup import skillSimpleModelSetup, ModelProps
from gui.impl.lobby.crew.tooltips.veh_cmp_skills_tooltip import VehCmpSkillsTooltip
from gui.impl.pub import ViewImpl
from gui.shared.event_dispatcher import showSkillSelectWindow
from gui.shared.gui_items.Tankman import crewMemberRealSkillLevel
from helpers import dependency
from items.components.skills_constants import SKILL_INDICES_ORDERED
from skeletons.gui.app_loader import IAppLoader
if typing.TYPE_CHECKING:
    from gui.Scaleform.daapi.view.lobby.vehicle_compare.cmp_configurator_view import CrewSkillsManager, VehicleCompareConfiguratorMain

def compareIconGetter(skillName, **__):
    return skillName


def compareLevelGetter(vehicle, skillName, **__):
    skillLevel = round(crewMemberRealSkillLevel(vehicle, skillName), 2)
    return skillLevel


propsGetters = {ModelProps.NAME: None,
 ModelProps.ICON_NAME: compareIconGetter,
 ModelProps.LEVEL: compareLevelGetter,
 ModelProps.ROLE_NAME: getRoleBySkillName}

class CompareSkillsPanelView(ViewImpl):
    __slots__ = ('__toolTipMgr', '__cmpConf')
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.vehicle_compare.CompareSkillsPanelView())
        settings.flags = ViewFlags.VIEW
        settings.model = CompareSkillsPanelViewModel()
        self.__toolTipMgr = self.__appLoader.getApp().getToolTipMgr()
        self.__cmpConf = cmp_helpers.getCmpConfiguratorMainView()
        super(CompareSkillsPanelView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(CompareSkillsPanelView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId == TooltipConstants.SKILL:
                args = [str(event.getArgument('skillName')),
                 event.getArgument('roleName'),
                 None,
                 event.getArgument('level')]
                self.__toolTipMgr.onCreateWulfTooltip(TOOLTIPS_CONSTANTS.CREW_PERK_GF, args, event.mouse.positionX, event.mouse.positionY, parent=self.getParentWindow())
                return TOOLTIPS_CONSTANTS.CREW_PERK_GF
        return super(CompareSkillsPanelView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        return VehCmpSkillsTooltip() if contentID == R.views.lobby.crew.tooltips.VehCmpSkillsTooltip() else None

    def onCrewSkillUpdated(self):
        self._fillViewModel()

    def _onLoading(self, *args, **kwargs):
        super(CompareSkillsPanelView, self)._onLoading(*args, **kwargs)
        self._fillViewModel()

    def _fillViewModel(self):
        crewSkillsManager = self.__cmpConf.getCrewSkillsManager()
        selectedSkills = crewSkillsManager.getSelectedSkills()
        vehicle = crewSkillsManager.getVehicle()
        skillsToShow = {skill for _, roleSkills in selectedSkills.values() for skill in roleSkills}
        skillsToShow = sorted(skillsToShow, key=lambda x: SKILL_INDICES_ORDERED.get(x, -1))
        with self.viewModel.transaction() as vm:
            skills = vm.getSkills()
            skills.clear()
            for skillName in skillsToShow:
                compareSkillVM = SkillSimpleModel()
                skillSimpleModelSetup(compareSkillVM, propsGetters, vehicle=vehicle, skillName=skillName)
                skills.addViewModel(compareSkillVM)

            skills.invalidate()

    def _getEvents(self):
        return ((self.viewModel.onClick, self.__onClick), (self.viewModel.onReset, self.__onReset))

    def _finalize(self):
        self.__toolTipMgr = None
        self.__cmpConf = None
        super(CompareSkillsPanelView, self)._finalize()
        return

    @staticmethod
    def __onClick():
        showSkillSelectWindow()

    def __onReset(self):
        self.__cmpConf.resetCrewSkills()
