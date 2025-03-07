# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/crew_helpers/model_setters.py
import math
from collections import defaultdict
from itertools import chain
from typing import TYPE_CHECKING
from constants import NEW_PERK_SYSTEM as NPS
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.common.crew_skill_list_model import CrewSkillListModel
from gui.impl.gen.view_models.views.lobby.crew.common.crew_skill_model import CrewSkillModel
from gui.impl.gen.view_models.views.lobby.crew.common.skill.skill_progression_model import SkillProgressionModel
from gui.impl.gen.view_models.views.lobby.crew.crew_constants import CrewConstants
from gui.impl.gen.view_models.views.lobby.crew.tankman_model import TankmanCardState, TankmanKind, TankmanLocation, TankmanRole
from gui.impl.lobby.crew.crew_helpers.skill_helpers import getTmanNewSkillCount
from gui.impl.lobby.crew.crew_helpers.skill_model_setup import skillModelSetup
from gui.impl.lobby.crew.dialogs.recruit_window.recruit_dialog_utils import getIconBackground
from gui.shared.gui_items.Tankman import SKILL_EFFICIENCY_UNTRAINED
from gui.shared.gui_items.tankman_skill import getTankmanSkill
from helpers import dependency, time_utils
from items.tankmen import MAX_SKILLS_EFFICIENCY, MAX_SKILL_LEVEL
from skeletons.gui.game_control import ISpecialSoundCtrl
from skeletons.gui.shared import IItemsCache
from skill_formatters import SkillLvlFormatter
if TYPE_CHECKING:
    from typing import Optional, List
    from frameworks.wulf import Array
    from gui.shared.gui_items.Tankman import Tankman
BARRACK_RECRUIT_BG_DYN = R.images.gui.maps.icons.tankmen.windows.recruits.barracks

def setTankmanModel(tm, tman, tmanNativeVeh, tmanVeh=None):
    if tman is None:
        return
    else:
        tdescr = tman.descriptor
        tm.setTankmanID(tman.invID)
        tm.setIconName(tman.getExtensionLessIconWithSkin())
        tm.setRole(TankmanRole(tdescr.role))
        tm.setFullUserName(tman.getFullUserNameWithSkin())
        tm.setTankmanKind(TankmanKind.TANKMAN)
        tm.setHasPostProgression(tdescr.isMaxSkillXp())
        tm.setIsInSkin(tman.isInSkin)
        tm.setLocation(TankmanLocation.DISMISSED if tman.isDismissed else (TankmanLocation.INTANK if tman.isInTank else TankmanLocation.INBARRACKS))
        tm.setIsMainActionDisabled(tman.isLockedByVehicle())
        newSkillsCount, lastNewSkillLvl = getTmanNewSkillCount(tman)
        lastSkillLvl = CrewConstants.DONT_SHOW_LEVEL
        if newSkillsCount > 0:
            lastSkillLvl = lastNewSkillLvl.intSkillLvl
        elif tman.earnedSkillsCount > 0:
            lastSkillLvl = tdescr.lastSkillLevel
        tm.setLastSkillLevel(lastSkillLvl)
        if tmanVeh:
            if tmanVeh.isInBattle or tmanVeh.isDisabled or tmanVeh.isInPrebattle:
                tm.setCardState(TankmanCardState.DISABLED)
            if tmanVeh.isInBattle or tmanVeh.isDisabled:
                tm.setDisableIcon(R.images.gui.maps.icons.vehicleStates.battle())
                tm.setDisableReason(R.strings.crew.common.inBattle())
            elif tmanVeh.isInPrebattle:
                tm.setDisableIcon(R.images.gui.maps.icons.vehicleStates.inPrebattle())
                tm.setDisableReason(R.strings.crew.common.inPrebattle())
            fillVehicleInfo(tm.vehicleInfo, tmanVeh)
        if tmanNativeVeh:
            fillVehicleInfo(tm.tankmanVehicleInfo, tmanNativeVeh, separateIGRTag=True)
        return


def setTmanSkillsModel(sm, tman, useOnlyFull=False, possibleSkillsLevels=None, fillBonusSkills=True, isRecruit=False, compVeh=None, customCrewName=''):
    if tman is None:
        sm.setSkillsEfficiency(0)
        sm.getMajorSkills().clear()
        sm.getBonusSkills().clear()
    else:
        if compVeh:
            isTrained = tman.descriptor.isOwnVehicleOrPremium(compVeh)
            sm.setSkillsEfficiency(tman.descriptor.skillsEfficiency if isTrained else SKILL_EFFICIENCY_UNTRAINED)
        elif isRecruit:
            sm.setSkillsEfficiency(MAX_SKILLS_EFFICIENCY)
        else:
            sm.setSkillsEfficiency(tman.currentVehicleSkillsEfficiency)
        setTmanMajorSkillsModel(sm.getMajorSkills(), tman, useOnlyFull, possibleSkillsLevels, customCrewName, isRecruit)
        if fillBonusSkills:
            setTmanBonusSkillsModel(sm.getBonusSkills(), tman)
        if possibleSkillsLevels is None:
            return
        _, possCnt, _, possLvl = possibleSkillsLevels
        if possCnt >= 0:
            possibleTotalMajorSkillProgress = tman.freeSkillsCount * MAX_SKILL_LEVEL + (possCnt - 1) * MAX_SKILL_LEVEL + possLvl.intSkillLvl
            possibleBonusSkillsProgress = possibleTotalMajorSkillProgress / NPS.BONUS_SKILL_ENABLING_FREQUENCY
            lastBonusSkillLvl = math.ceil(possibleBonusSkillsProgress % MAX_SKILL_LEVEL)
            possibleFullBonusSkillsCount, possibleLastBonusSkillLvl = int(possibleBonusSkillsProgress) / MAX_SKILL_LEVEL, MAX_SKILL_LEVEL if MAX_SKILL_LEVEL - lastBonusSkillLvl < 1 else int(lastBonusSkillLvl)
            possibleBonusSkillsLvl = [MAX_SKILL_LEVEL] * possibleFullBonusSkillsCount + [possibleLastBonusSkillLvl]
            possibleBonusSkillsLvl = possibleBonusSkillsLvl[:NPS.MAX_BONUS_SKILLS_PER_ROLE]
        else:
            possibleBonusSkillsLvl = None
        if fillBonusSkills:
            setTmanBonusSkillsModel(sm.getBonusSkills(), tman, bonusSlotsLevels=possibleBonusSkillsLvl)
    return


def setTmanMajorSkillsModel(listVM, tman, useOnlyFull=False, possibleSkillsLevels=None, customCrewName='', isRecruit=False):
    listVM.clear()
    notFullEarnedSkillMdl = None
    for skill in tman.skills:
        if customCrewName:
            skill = getTankmanSkill(skill.name, tman.role, tman, level=skill.level, customCrewName=customCrewName)
        skillVM = getCrewWidgetTmanSkillModelNPS(tman, skill, tman.role)
        if isRecruit:
            skillVM.setIsIrrelevant(False)
        if skill.isMaxLevel:
            listVM.addViewModel(skillVM)
        notFullEarnedSkillMdl = skillVM

    for _ in xrange(tman.newFreeSkillsCount):
        listVM.addViewModel(getNewSkillCrewWidgetTmanSkillModelNPS(MAX_SKILL_LEVEL, True))

    if notFullEarnedSkillMdl:
        listVM.addViewModel(notFullEarnedSkillMdl)
    else:
        newSkillsCount, lastNewSkillLevel = getTmanNewSkillCount(tman, useOnlyFull)
        for index in xrange(newSkillsCount):
            lvl = 100.0 if index < newSkillsCount - 1 else lastNewSkillLevel.intSkillLvl
            listVM.addViewModel(getNewSkillCrewWidgetTmanSkillModelNPS(level=lvl))

    if possibleSkillsLevels is not None:
        currSkillsCount, possibleSkillsCount, _, possibleLastSkillLevel = possibleSkillsLevels
        if possibleSkillsCount > currSkillsCount:
            listVM.getValue(len(listVM) - 1).setLevel(100)
            newSkillsCount = possibleSkillsCount - currSkillsCount
            for index in xrange(newSkillsCount):
                lvl = 100.0 if index < newSkillsCount - 1 else possibleLastSkillLevel.formattedSkillLvl
                listVM.addViewModel(getNewSkillCrewWidgetTmanSkillModelNPS(level=lvl))

        elif possibleLastSkillLevel.realSkillLvl != -1:
            listVM.getValue(len(listVM) - 1).setLevel(possibleLastSkillLevel.formattedSkillLvl)
    return


def setTmanBonusSkillsModel(listVM, tman, bonusSlotsLevels=None, selectedRole=None, selectedSkills=None):
    selected = defaultdict(list)
    empty = defaultdict(list)
    bonusSlotsLevels = bonusSlotsLevels or tman.bonusSlotsLevels
    selectedSkillIndex = 0
    for role, skills in tman.bonusSkills.iteritems():
        for skill, lvl in zip(skills, bonusSlotsLevels):
            if lvl is None:
                continue
            if skill is None and selectedRole and role == selectedRole and selectedSkillIndex < len(selectedSkills):
                skillName = selectedSkills[selectedSkillIndex]
                skillVM = CrewSkillModel()
                skillVM.setName(selectedSkills[selectedSkillIndex])
                skillVM.setIconName(selectedSkills[selectedSkillIndex])
                skillVM.setLevel(lvl)
                selectedSkillIndex += 1
            else:
                skillName = skill.name if skill else None
                if skill is None:
                    skillVM = getNewSkillCrewWidgetTmanSkillModelNPS(level=lvl)
                else:
                    skillVM = getCrewWidgetTmanSkillModelNPS(tman, skill, role, level=lvl)
            key = 'full' if lvl == MAX_SKILL_LEVEL else 'notfull'
            if skillName:
                selected[key].append(skillVM)
            empty[key].append(skillVM)

    listVM.clear()
    skillModels = list(chain(selected['full'], empty['full'], selected['notfull'], empty['notfull']))
    for skillVM in skillModels:
        listVM.addViewModel(skillVM)

    return


def getCrewWidgetTmanSkillModelNPS(tman, skill, role, level=None):
    skillVM = CrewSkillModel()
    skillLevel = level if level and level > skill.level else skill.level
    skillModelSetup(skillVM, skill=skill, role=role, tankman=tman, skillLevel=skillLevel)
    skillVM.setCustomName(skill.crewCustomName)
    return skillVM


def getNewSkillCrewWidgetTmanSkillModelNPS(level=None, isZero=False):
    skillVM = CrewSkillModel()
    skillVM.setName(CrewConstants.NEW_SKILL)
    skillVM.setIconName(CrewConstants.NEW_SKILL)
    skillVM.setIsZero(isZero)
    if level:
        skillVM.setLevel(level)
    return skillVM


def setReplacedTankmanModel(tm, tman, tmanNativeVeh):
    if tman is None:
        return
    else:
        tm.setFullUserName(tman.getFullUserNameWithSkin())
        tm.setRole(TankmanRole(tman.role))
        if tmanNativeVeh:
            tm.tankmanVehicleInfo.setVehicleName(tmanNativeVeh.descriptor.type.userString)
        return


@dependency.replace_none_kwargs(specialSoundCtrl=ISpecialSoundCtrl)
def setRecruitTankmanModel(tm, recruitInfo, specialSoundCtrl=None, useOnlyFullSkills=True):
    tm.setRecruitID(str(recruitInfo.getRecruitID()))
    if len(recruitInfo.getRoles()) > 1:
        tm.setRole(TankmanRole.ANY)
    elif recruitInfo.getRoles():
        tm.setRole(TankmanRole(recruitInfo.getRoles()[0]))
    tm.setFullUserName(recruitInfo.getFullUserName())
    iconName = recruitInfo.getDynIconName()
    tm.setIconName(iconName)
    tm.setRecruitGlowImage(getIconBackground(recruitInfo.getSourceID(), iconName, BARRACK_RECRUIT_BG_DYN))
    tm.setTankmanKind(TankmanKind.RECRUIT)
    tm.setHasVoiceover(bool(recruitInfo.getSpecialVoiceTag(specialSoundCtrl)))
    tm.setLocation(TankmanLocation.INBARRACKS)
    tman = recruitInfo.getFakeTankman()
    customCrewName = recruitInfo.getCrewCustomName()
    skills = tm.skills
    setTmanSkillsModel(skills, tman, useOnlyFull=useOnlyFullSkills, isRecruit=True, customCrewName=customCrewName)
    newSkillsCount, lastSkillLevel = getTmanNewSkillCount(tman, useOnlyFull=useOnlyFullSkills)
    if tman.earnedSkillsCount + newSkillsCount <= 0:
        lastSkillLevel = SkillLvlFormatter()
    tm.setLastSkillLevel(lastSkillLevel.intSkillLvl)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def setTankmanRestoreInfo(vm, itemsCache=None):
    tankmenRestoreConfig = itemsCache.items.shop.tankmenRestoreConfig
    freeDays = tankmenRestoreConfig.freeDuration / time_utils.ONE_DAY
    billableDays = tankmenRestoreConfig.billableDuration / time_utils.ONE_DAY - freeDays
    restoreCost = tankmenRestoreConfig.cost
    restoreLimit = tankmenRestoreConfig.limit
    vm.setFreePeriod(freeDays)
    vm.setPaidPeriod(billableDays)
    vm.setRecoverPrice(restoreCost.get(restoreCost.getCurrency(), 0))
    vm.setMembersBuffer(restoreLimit)


def ifWGMAvailableButtonUpdate(vm, itemsCache, button, checkIsPriceSelected):
    isWGMAvailable = itemsCache.items.stats.mayConsumeWalletResources
    priceSelected = vm.getIsPriceSelected() if checkIsPriceSelected else True
    button.isDisabled = not (priceSelected and isWGMAvailable)
    vm.getButtons().invalidate()


def setSkillProgressionModel(vm, tankman, skillIndex, isZero):
    currentXp = 0
    discountXpCost = 0
    fullPriceXpCost = 0
    isLocked = False
    skillProgress = MAX_SKILL_LEVEL if isZero else 0
    tankmanDescriptor = tankman.descriptor
    if not isZero:
        levelIndex = skillIndex - tankman.freeSkillsCount
        discountXpCost = tankmanDescriptor.skillUpXpCost(levelIndex + 1)
        fullPriceXpCost = tankmanDescriptor.skillUpXpCost(skillIndex + 1)
        prevSkillFullXpCost = 0 if not levelIndex else tankmanDescriptor.getXpCostForSkillsLevels(MAX_SKILL_LEVEL, levelIndex)
        currSkillFullXpCost = tankmanDescriptor.getXpCostForSkillsLevels(MAX_SKILL_LEVEL, levelIndex + 1)
        if 0 <= skillIndex < len(tankman.skillsLevels):
            skillProgress = tankman.skillsLevels[skillIndex]
        else:
            isLocked = True
        tankmanTotalXp = tankmanDescriptor.totalXP()
        if not isLocked and tankmanTotalXp > 0:
            currentXp = discountXpCost
            if tankmanTotalXp < currSkillFullXpCost:
                currentXp = tankmanTotalXp - prevSkillFullXpCost
    vm.setCurrentXpValue(currentXp)
    vm.setTotalXpValue(fullPriceXpCost)
    vm.setSkillProgress(skillProgress)
    vm.setDiscountValue(discountXpCost)
    vm.setZeroSkillsCount(tankman.freeSkillsCount)
    vm.setIsLocked(isLocked)
    vm.setIsMaxSkillLevel(skillProgress == MAX_SKILL_LEVEL)
