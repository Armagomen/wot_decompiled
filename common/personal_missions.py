# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/personal_missions.py
import typing
import potapov_quests
import persistent_data_cache_common as pdc
from quest_xml_source import QuestValidationSerializer
g_cache = None
g_operationsCache = None
g_campaignsCache = None
PERSONAL_MISSIONS_XML_PATH = potapov_quests.POTAPOV_QUEST_XML_PATH

class PM_BRANCH(potapov_quests.PQ_BRANCH):
    ACTIVE_BRANCHES = (potapov_quests.PQ_BRANCH.REGULAR, potapov_quests.PQ_BRANCH.PERSONAL_MISSION_2)


def isPersonalMissionsEnabled(gameParams, branch):
    return not potapov_quests.isPotapovQuestBranchEnabled(gameParams, branch)


class PM_STATE(potapov_quests.PQ_STATE):
    pass


class PM_FLAG(potapov_quests.PQ_FLAG):
    pass


PM_BRANCH_TO_FREE_TOKEN_NAME = potapov_quests.PM_BRANCH_TO_FREE_TOKEN_NAME
PM_BRANCH_TO_FINAL_PAWN_COST = potapov_quests.PM_BRANCH_TO_FINAL_PAWN_COST
PM_REWARD_BY_DEMAND = potapov_quests.PQ_REWARD_BY_DEMAND

def _createPMCache():
    auxData = {}
    return (PMCache(auxData), auxData)


def init():
    global g_cache
    global g_campaignsCache
    global g_operationsCache
    potapov_quests.g_seasonCache = pdc.load('personal_missions_season_cache', potapov_quests.SeasonCache)
    potapov_quests.g_tileCache = pdc.load('personal_missions_tile_cache', potapov_quests.TileCache)
    g_campaignsCache = pdc.load('personal_missions_campaigns_cache', CampaignsCache)
    g_operationsCache = pdc.load('personal_missions_operations_cache', OperationsCache)
    g_cache, _ = pdc.load('personal_missions_cache', _createPMCache, QuestValidationSerializer())


class CampaignsCache(potapov_quests.SeasonCache):

    def getCampaignInfo(self, campaignID):
        return self.getSeasonInfo(campaignID)


class OperationsCache(potapov_quests.TileCache):

    def getOperationInfo(self, operationID):
        return self.getTileInfo(operationID)


class PMCache(potapov_quests.PQCache):

    def questByPersonalMissionID(self, missionID):
        return self.questByPotapovQuestID(missionID)

    def hasMission(self, missionID):
        return self.hasPotapovQuest(missionID)

    def isPersonalMission(self, uniqueQuestID):
        return self.isPotapovQuest(uniqueQuestID)

    def questListByOperationIDChainID(self, tileID, chainID):
        return self.questListByTileIDChainID(tileID, chainID)

    def finalMissionIDByOperationIDChainID(self, tileID, chainID):
        return self.finalPotapovQuestIDByTileIDChainID(tileID, chainID)

    def initialMissionQuestIDByOperationIDChainID(self, tileID, chainID):
        return self.initialPotapovQuestIDByTileIDChainID(tileID, chainID)

    def getPersonalMissionIDByUniqueID(self, uniqueQuestID):
        return self.getPotapovQuestIDByUniqueID(uniqueQuestID)

    def branchByMissionID(self, potapovQuestID):
        return self.branchByPotapovQuestID(potapovQuestID)


class PMStorage(potapov_quests.PQStorage):
    pass
