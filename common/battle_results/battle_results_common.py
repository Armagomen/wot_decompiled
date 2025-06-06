# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/battle_results/battle_results_common.py
from battle_results_constants import BATTLE_RESULT_ENTRY_TYPE as ENTRY_TYPE
from constants import FLAG_ACTION
from DictPackers import DictPacker, MergeDictPacker, SimpleDictPacker, DeltaPacker, ValueReplayPacker, roundToInt
from items.vehicles import VEHICLE_DEVICE_TYPE_NAMES, VEHICLE_TANKMAN_TYPE_NAMES
from items.badges_common import BadgesCommon
BATTLE_RESULTS = [('health',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_ALL),
 ('maxHealth',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_ALL),
 ('credits',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('xp',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('xp/attack',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('xp/assist',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('xp/other',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('xpPenalty',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('achievementCredits',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_ALL),
 ('achievementXP',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_ALL),
 ('achievementFreeXP',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_ALL),
 ('shots',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('directHits',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('directEnemyHits',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('directTeamHits',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('explosionHits',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('piercings',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('piercingEnemyHits',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('damageDealt',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('sniperDamageDealt',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('artilleryFortEquipDamageDealt',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('equipmentDamageDealt',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('damageAssistedRadio',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('damageAssistedTrack',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('damageAssistedStun',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('damageAssistedSmoke',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('damageAssistedInspire',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('stunNum',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('stunDuration',
  float,
  0.0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('damageReceived',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('damageReceivedFromInvisibles',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('damageBlockedByArmor',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('directHitsReceived',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('noDamageDirectHitsReceived',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('explosionHitsReceived',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('piercingsReceived',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('tdamageDealt',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('tdestroyedModules',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('tkills',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('isTeamKiller',
  bool,
  False,
  None,
  'max',
  ENTRY_TYPE.VEHICLE_ALL),
 ('capturePoints',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('capturingBase',
  None,
  None,
  None,
  'any',
  ENTRY_TYPE.VEHICLE_ALL),
 ('droppedCapturePoints',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('mileage',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('lifeTime',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('killerID',
  int,
  0,
  None,
  'any',
  ENTRY_TYPE.VEHICLE_ALL),
 ('achievements',
  list,
  [],
  None,
  'extend',
  ENTRY_TYPE.VEHICLE_ALL),
 ('inBattleAchievements',
  list,
  [],
  None,
  'extend',
  ENTRY_TYPE.VEHICLE_ALL),
 ('potentialDamageReceived',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('rolloutsCount',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('deathCount',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('flagActions',
  list,
  [0] * len(FLAG_ACTION.RANGE),
  None,
  'sumInEachPos',
  ENTRY_TYPE.VEHICLE_ALL),
 ('soloFlagCapture',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('flagCapture',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('winPoints',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('resourceAbsorbed',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('stopRespawn',
  bool,
  False,
  None,
  'max',
  ENTRY_TYPE.VEHICLE_ALL),
 ('numRecovered',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('vehicleNumCaptured',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('destructiblesNumDestroyed',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('destructiblesDamageDealt',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('destructiblesHits',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('destructibleDeaths',
  list,
  [],
  None,
  'extend',
  ENTRY_TYPE.VEHICLE_ALL),
 ('numDefended',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('accountDBID',
  int,
  0,
  None,
  'any',
  ENTRY_TYPE.VEHICLE_ALL),
 ('typeCompDescr',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_ALL),
 ('index',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_ALL),
 ('deathReason',
  int,
  -1,
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_ALL),
 ('team',
  int,
  1,
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_ALL),
 ('kills',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('spotted',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('damaged',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('damagedHp',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('stunned',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_ALL),
 ('marksOnGun',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_ALL),
 ('repair',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('freeXP',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('details',
  None,
  None,
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('creditsPenalty',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('creditsContributionIn',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('creditsContributionOut',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('originalCreditsToDraw',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('creditsToDraw',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('damageBeforeTeamWasDamaged',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('killsBeforeTeamWasDamaged',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('percentFromTotalTeamDamage',
  float,
  0.0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('winAloneAgainstVehicleCount',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('percentFromSecondBestDamage',
  float,
  0.0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('killedAndDamagedByAllSquadmates',
  int,
  0,
  None,
  'any',
  ENTRY_TYPE.VEHICLE_SELF),
 ('damagedWhileMoving',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('damagedWhileEnemyMoving',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('committedSuicide',
  bool,
  False,
  None,
  'max',
  ENTRY_TYPE.VEHICLE_SELF),
 ('crystal',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('eventCoin',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('bpcoin',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('equipCoin',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('piggyBank',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('eventCredits',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('eventXP',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('eventFreeXP',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('eventTMenXP',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('eventGold',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('eventCrystal',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('eventEventCoin',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('eventBpcoin',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('eventEquipCoin',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('originalCredits',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('creditsReplay',
  str,
  '',
  ValueReplayPacker(),
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('originalXP',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('pureXP',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.SERVER),
 ('xpReplay',
  str,
  '',
  ValueReplayPacker(),
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('originalFreeXP',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('freeXPReplay',
  str,
  '',
  ValueReplayPacker(),
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('originalTMenXP',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('tmenXPReplay',
  str,
  '',
  ValueReplayPacker(),
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('tmenXP',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('originalGold',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('goldReplay',
  str,
  '',
  ValueReplayPacker(),
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('gold',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('originalCrystal',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('crystalReplay',
  str,
  '',
  ValueReplayPacker(),
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('originalEventCoin',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('originalBpcoin',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('originalEquipCoin',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('eventCoinReplay',
  str,
  '',
  ValueReplayPacker(),
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('bpcoinReplay',
  str,
  '',
  ValueReplayPacker(),
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('equipCoinReplay',
  str,
  '',
  ValueReplayPacker(),
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('factualXP',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('factualFreeXP',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('factualCredits',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('subtotalCredits',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('subtotalXP',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('subtotalFreeXP',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('subtotalTMenXP',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('subtotalGold',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('subtotalCrystal',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('subtotalEventCoin',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('subtotalBpcoin',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('subtotalEquipCoin',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('eventCreditsList',
  list,
  [],
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('eventXPList',
  list,
  [],
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('eventFreeXPList',
  list,
  [],
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('eventTMenXPList',
  list,
  [],
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('eventGoldList',
  list,
  [],
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('eventCrystalList',
  list,
  [],
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('eventEventCoinList',
  list,
  [],
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('eventBpcoinList',
  list,
  [],
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('eventEquipCoinList',
  list,
  [],
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('eventCreditsFactor100List',
  list,
  [],
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('eventXPFactor100List',
  list,
  [],
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('eventFreeXPFactor100List',
  list,
  [],
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('eventTMenXPFactor100List',
  list,
  [],
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('eventGoldFactor100List',
  list,
  [],
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('originalXPPenalty',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('originalCreditsPenalty',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('originalCreditsContributionIn',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('originalCreditsContributionOut',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('premiumVehicleXP',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('premiumVehicleXPFactor100',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('squadXP',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('squadXPFactor100',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('isWoTPlus',
  bool,
  False,
  None,
  'any',
  ENTRY_TYPE.VEHICLE_SELF),
 ('wotPlusCredits',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('wotPlusCreditsFactor100',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('wotPlusXP',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('wotPlusXPFactor100',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('wotPlusCrewXP',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('wotPlusCrewXPFactor100',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('wotPlusFreeXP',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('wotPlusFreeXPFactor100',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('referral20XP',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('referral20XPFactor100',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('referral20Credits',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('referral20CreditsFactor100',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('premiumXPFactor100',
  int,
  0,
  None,
  'any',
  ENTRY_TYPE.VEHICLE_SELF),
 ('premiumPlusXPFactor100',
  int,
  0,
  None,
  'any',
  ENTRY_TYPE.VEHICLE_SELF),
 ('appliedPremiumXPFactor100',
  int,
  0,
  None,
  'any',
  ENTRY_TYPE.VEHICLE_SELF),
 ('premiumTmenXPFactor100',
  int,
  0,
  None,
  'any',
  ENTRY_TYPE.VEHICLE_SELF),
 ('premiumPlusTmenXPFactor100',
  int,
  0,
  None,
  'any',
  ENTRY_TYPE.VEHICLE_SELF),
 ('appliedPremiumTmenXPFactor100',
  int,
  0,
  None,
  'any',
  ENTRY_TYPE.VEHICLE_SELF),
 ('premiumCreditsFactor100',
  int,
  0,
  None,
  'any',
  ENTRY_TYPE.VEHICLE_SELF),
 ('premiumPlusCreditsFactor100',
  int,
  0,
  None,
  'any',
  ENTRY_TYPE.VEHICLE_SELF),
 ('appliedPremiumCreditsFactor100',
  int,
  0,
  None,
  'any',
  ENTRY_TYPE.VEHICLE_SELF),
 ('premSquadCreditsFactor100',
  int,
  0,
  None,
  'any',
  ENTRY_TYPE.VEHICLE_SELF),
 ('originalPremSquadCredits',
  int,
  0,
  None,
  'any',
  ENTRY_TYPE.VEHICLE_SELF),
 ('premSquadCredits',
  int,
  0,
  None,
  'any',
  ENTRY_TYPE.VEHICLE_SELF),
 ('dailyXPFactor10',
  int,
  0,
  None,
  'max',
  ENTRY_TYPE.VEHICLE_SELF),
 ('additionalXPFactor10',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('igrXPFactor10',
  int,
  0,
  None,
  'max',
  ENTRY_TYPE.VEHICLE_SELF),
 ('aogasFactor10',
  int,
  0,
  None,
  'max',
  ENTRY_TYPE.VEHICLE_SELF),
 ('refSystemXPFactor10',
  int,
  0,
  None,
  'any',
  ENTRY_TYPE.VEHICLE_SELF),
 ('fairplayFactor10',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('orderCredits',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('orderXP',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('orderFreeXP',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('orderTMenXP',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('orderCreditsFactor100',
  int,
  0,
  None,
  'any',
  ENTRY_TYPE.VEHICLE_SELF),
 ('orderXPFactor100',
  int,
  0,
  None,
  'any',
  ENTRY_TYPE.VEHICLE_SELF),
 ('orderFreeXPFactor100',
  int,
  0,
  None,
  'any',
  ENTRY_TYPE.VEHICLE_SELF),
 ('orderTMenXPFactor100',
  int,
  0,
  None,
  'any',
  ENTRY_TYPE.VEHICLE_SELF),
 ('boosterCredits',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('boosterXP',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('boosterFreeXP',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('boosterTMenXP',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('boosterCreditsFactor100',
  int,
  0,
  None,
  'any',
  ENTRY_TYPE.VEHICLE_SELF),
 ('boosterXPFactor100',
  int,
  0,
  None,
  'any',
  ENTRY_TYPE.VEHICLE_SELF),
 ('boosterFreeXPFactor100',
  int,
  0,
  None,
  'any',
  ENTRY_TYPE.VEHICLE_SELF),
 ('boosterTMenXPFactor100',
  int,
  0,
  None,
  'any',
  ENTRY_TYPE.VEHICLE_SELF),
 ('playerRankXP',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('playerRankXPFactor100',
  int,
  0,
  None,
  'any',
  ENTRY_TYPE.VEHICLE_SELF),
 ('isPremium',
  bool,
  False,
  None,
  'any',
  ENTRY_TYPE.VEHICLE_SELF),
 ('premMask',
  int,
  0,
  None,
  'any',
  ENTRY_TYPE.VEHICLE_SELF),
 ('xpByTmen',
  list,
  [],
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('autoRepairCost',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('autoLoadCost',
  tuple,
  (0, 0),
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('autoEquipCost',
  tuple,
  (0, 0, 0),
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('autoEquipBoostersCost',
  tuple,
  (0, 0, 0),
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('prevMarkOfMastery',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('markOfMastery',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('dossierPopUps',
  list,
  [],
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('dossierLogRecords',
  list,
  [],
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('vehTypeLockTime',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('serviceProviderID',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('movingAvgDamage',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('damageRating',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('battleNum',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('questsProgress',
  dict,
  {},
  None,
  'joinDicts',
  ENTRY_TYPE.VEHICLE_SELF),
 ('questTokensCount',
  dict,
  {},
  None,
  'skip',
  ENTRY_TYPE.ACCOUNT_SELF),
 ('c11nProgress',
  dict,
  {},
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('originalCreditsToDrawSquad',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('originalCreditsPenaltySquad',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('originalCreditsContributionInSquad',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('originalCreditsContributionOutSquad',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.VEHICLE_SELF),
 ('avatarDamageDealt',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.ACCOUNT_ALL),
 ('avatarKills',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.ACCOUNT_ALL),
 ('avatarDamaged',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.ACCOUNT_ALL),
 ('totalDamaged',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.ACCOUNT_ALL),
 ('fairplayViolations',
  tuple,
  (0, 0, 0),
  None,
  'skip',
  ENTRY_TYPE.ACCOUNT_ALL),
 ('badges',
  tuple,
  BadgesCommon.selectedBadgesEmpty(),
  None,
  'skip',
  ENTRY_TYPE.ACCOUNT_ALL),
 ('rankChange',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.ACCOUNT_SELF),
 ('avatarAmmo',
  list,
  [],
  None,
  'skip',
  ENTRY_TYPE.ACCOUNT_SELF),
 ('avatarDamageEventList',
  set,
  set(),
  None,
  'skip',
  ENTRY_TYPE.ACCOUNT_SELF),
 ('accountDBID',
  int,
  0,
  None,
  'any',
  ENTRY_TYPE.ACCOUNT_SELF),
 ('team',
  int,
  1,
  None,
  'skip',
  ENTRY_TYPE.ACCOUNT_SELF),
 ('clanDBID',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.ACCOUNT_SELF),
 ('fortClanDBIDs',
  list,
  [],
  None,
  'skip',
  ENTRY_TYPE.ACCOUNT_SELF),
 ('winnerIfDraw',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.ACCOUNT_SELF),
 ('isPrematureLeave',
  bool,
  False,
  None,
  'skip',
  ENTRY_TYPE.ACCOUNT_SELF),
 ('watchedBattleToTheEnd',
  bool,
  False,
  None,
  'skip',
  ENTRY_TYPE.ACCOUNT_SELF),
 ('vseBattleResults',
  dict,
  {},
  None,
  'skip',
  ENTRY_TYPE.ACCOUNT_SELF),
 ('squadBonusInfo',
  None,
  None,
  None,
  'skip',
  ENTRY_TYPE.ACCOUNT_SELF),
 ('progressiveReward',
  None,
  None,
  None,
  'skip',
  ENTRY_TYPE.ACCOUNT_SELF),
 ('eligibleForCrystalRewards',
  bool,
  False,
  None,
  'skip',
  ENTRY_TYPE.ACCOUNT_SELF),
 ('activeRents',
  dict,
  {},
  None,
  'skip',
  ENTRY_TYPE.ACCOUNT_SELF),
 ('recruitsIDs',
  list,
  [],
  None,
  'skip',
  ENTRY_TYPE.ACCOUNT_SELF),
 ('recruiterID',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.ACCOUNT_SELF),
 ('referralBonusVehicles',
  list,
  [],
  None,
  'skip',
  ENTRY_TYPE.ACCOUNT_SELF),
 ('fareTeamXPPosition',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.ACCOUNT_SELF),
 ('questsProgress',
  dict,
  {},
  None,
  'joinDicts',
  ENTRY_TYPE.ACCOUNT_SELF),
 ('PM2Progress',
  dict,
  {},
  None,
  'skip',
  ENTRY_TYPE.ACCOUNT_SELF),
 ('dogTags',
  dict,
  {},
  None,
  'skip',
  ENTRY_TYPE.ACCOUNT_SELF),
 ('eventCredits',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.ACCOUNT_SELF),
 ('eventXP',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.ACCOUNT_SELF),
 ('eventFreeXP',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.ACCOUNT_SELF),
 ('eventTMenXP',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.ACCOUNT_SELF),
 ('eventGold',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.ACCOUNT_SELF),
 ('eventCrystal',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.ACCOUNT_SELF),
 ('eventEventCoin',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.ACCOUNT_SELF),
 ('eventBpcoin',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.ACCOUNT_SELF),
 ('eventEquipCoin',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.ACCOUNT_SELF),
 ('credits',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.ACCOUNT_SELF),
 ('xp',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.ACCOUNT_SELF),
 ('freeXP',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.ACCOUNT_SELF),
 ('crystal',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.ACCOUNT_SELF),
 ('name',
  str,
  '',
  None,
  'skip',
  ENTRY_TYPE.PLAYER_INFO),
 ('realName',
  str,
  '',
  None,
  'skip',
  ENTRY_TYPE.PLAYER_INFO),
 ('clanDBID',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.PLAYER_INFO),
 ('clanAbbrev',
  str,
  '',
  None,
  'skip',
  ENTRY_TYPE.PLAYER_INFO),
 ('prebattleID',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.PLAYER_INFO),
 ('team',
  int,
  1,
  None,
  'skip',
  ENTRY_TYPE.PLAYER_INFO),
 ('igrType',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.PLAYER_INFO),
 ('arenaTypeID',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.COMMON),
 ('arenaCreateTime',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.COMMON),
 ('winnerTeam',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.COMMON),
 ('finishReason',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.COMMON),
 ('gasAttackWinnerTeam',
  int,
  -1,
  None,
  'skip',
  ENTRY_TYPE.COMMON),
 ('duration',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.COMMON),
 ('bonusType',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.COMMON),
 ('guiType',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.COMMON),
 ('vehLockMode',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.COMMON),
 ('division',
  None,
  None,
  None,
  'skip',
  ENTRY_TYPE.COMMON),
 ('bots',
  dict,
  {},
  None,
  'skip',
  ENTRY_TYPE.COMMON),
 ('commonNumStarted',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.COMMON),
 ('commonNumDestroyed',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.COMMON),
 ('commonNumDefended',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.COMMON),
 ('commonNumCaptured',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.COMMON),
 ('accountCompDescr',
  dict,
  {},
  None,
  'skip',
  ENTRY_TYPE.COMMON),
 ('teamHealth',
  dict,
  {},
  None,
  'skip',
  ENTRY_TYPE.COMMON),
 ('battleModifiersDescr',
  tuple,
  (),
  None,
  'skip',
  ENTRY_TYPE.COMMON),
 ('bonusCapsOverrides',
  dict,
  {},
  None,
  'skip',
  ENTRY_TYPE.COMMON),
 ('canStun',
  bool,
  False,
  None,
  'any',
  ENTRY_TYPE.SERVER),
 ('potentialDamageDealt',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.SERVER),
 ('soloHitsAssisted',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.SERVER),
 ('isEnemyBaseCaptured',
  bool,
  False,
  None,
  'max',
  ENTRY_TYPE.SERVER),
 ('stucks',
  list,
  [],
  DeltaPacker(roundToInt),
  'extend',
  ENTRY_TYPE.SERVER),
 ('autoAimedShots',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.SERVER),
 ('presenceTime',
  int,
  0,
  None,
  'max',
  ENTRY_TYPE.SERVER),
 ('spotList',
  list,
  [],
  None,
  'extend',
  ENTRY_TYPE.SERVER),
 ('ammo',
  list,
  [],
  None,
  'skip',
  ENTRY_TYPE.SERVER),
 ('crewActivityFlags',
  list,
  [],
  None,
  'skip',
  ENTRY_TYPE.SERVER),
 ('series',
  dict,
  {},
  None,
  'skip',
  ENTRY_TYPE.SERVER),
 ('tkillRating',
  float,
  0.0,
  None,
  'sum',
  ENTRY_TYPE.SERVER),
 ('thitPenalties',
  dict,
  {},
  None,
  'joinTHitPenalties',
  ENTRY_TYPE.SERVER),
 ('destroyedObjects',
  dict,
  {},
  None,
  'sumByEackKey',
  ENTRY_TYPE.SERVER),
 ('discloseShots',
  list,
  [],
  DeltaPacker(),
  'extend',
  ENTRY_TYPE.SERVER),
 ('critsCount',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.SERVER),
 ('aimerSeries',
  int,
  0,
  None,
  'max',
  ENTRY_TYPE.SERVER),
 ('observedByEnemyTime',
  int,
  -1,
  None,
  'any',
  ENTRY_TYPE.SERVER),
 ('critsByType',
  dict,
  {},
  DictPacker(('destroyed',
   dict,
   {},
   SimpleDictPacker(int, VEHICLE_DEVICE_TYPE_NAMES),
   'skip'), ('critical',
   dict,
   {},
   SimpleDictPacker(int, VEHICLE_DEVICE_TYPE_NAMES),
   'skip'), ('tankman',
   dict,
   {},
   SimpleDictPacker(int, VEHICLE_TANKMAN_TYPE_NAMES),
   'skip')),
  'joinCritsByType',
  ENTRY_TYPE.SERVER),
 ('innerModuleCritCount',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.SERVER),
 ('innerModuleDestrCount',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.SERVER),
 ('isAnyOurCrittedInnerModules',
  int,
  0,
  None,
  'max',
  ENTRY_TYPE.SERVER),
 ('killsAssistedTrack',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.SERVER),
 ('killsAssistedRadio',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.SERVER),
 ('killsAssistedStun',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.SERVER),
 ('damagedVehicleCntAssistedTrack',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.SERVER),
 ('damagedVehicleCntAssistedRadio',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.SERVER),
 ('damagedVehicleCntAssistedStun',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.SERVER),
 ('isNotSpotted',
  bool,
  True,
  None,
  'max',
  ENTRY_TYPE.SERVER),
 ('isAnyHitReceivedWhileCapturing',
  bool,
  False,
  None,
  'max',
  ENTRY_TYPE.SERVER),
 ('damageAssistedRadioWhileInvisible',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.SERVER),
 ('damageAssistedTrackWhileInvisible',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.SERVER),
 ('damageAssistedStunWhileInvisible',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.SERVER),
 ('damageEventList',
  dict,
  {},
  None,
  'joinTargetEventLists',
  ENTRY_TYPE.SERVER),
 ('stunEventList',
  dict,
  {},
  None,
  'joinTargetEventLists',
  ENTRY_TYPE.SERVER),
 ('assistEventList',
  dict,
  {},
  None,
  'joinTargetEventLists',
  ENTRY_TYPE.SERVER),
 ('damageFromEnemiesEventList',
  dict,
  {},
  None,
  'joinTargetEventLists',
  ENTRY_TYPE.SERVER),
 ('multiDamageEvents',
  dict,
  {},
  None,
  'joinDicts',
  ENTRY_TYPE.SERVER),
 ('multiStunEvents',
  dict,
  {},
  None,
  'joinDicts',
  ENTRY_TYPE.SERVER),
 ('inBattleMaxSniperSeries',
  int,
  0,
  None,
  'max',
  ENTRY_TYPE.SERVER),
 ('inBattleMaxKillingSeries',
  int,
  0,
  None,
  'max',
  ENTRY_TYPE.SERVER),
 ('inBattleMaxPiercingSeries',
  int,
  0,
  None,
  'max',
  ENTRY_TYPE.SERVER),
 ('firstDamageTime',
  int,
  0,
  None,
  'min',
  ENTRY_TYPE.SERVER),
 ('consumedAmmo',
  None,
  None,
  None,
  'skip',
  ENTRY_TYPE.SERVER),
 ('ironShieldDamage',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.SERVER),
 ('occupyingForceDestruction',
  bool,
  False,
  None,
  'max',
  ENTRY_TYPE.SERVER),
 ('occupyingForceBasePoints',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.SERVER),
 ('directEnemyHits',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.SERVER),
 ('explosionEnemyHits',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.SERVER),
 ('piercingEnemyHits',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.SERVER),
 ('indirectEnemyHits',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.SERVER),
 ('enemyHits',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.SERVER),
 ('spottedBeforeWeBecameSpotted',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.SERVER),
 ('spottedAndDamagedSPG',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.SERVER),
 ('damageList',
  list,
  [],
  None,
  'extend',
  ENTRY_TYPE.SERVER),
 ('killList',
  list,
  [],
  None,
  'extend',
  ENTRY_TYPE.SERVER),
 ('vehLockTimeFactor',
  float,
  0.0,
  None,
  'skip',
  ENTRY_TYPE.SERVER),
 ('misc',
  dict,
  {},
  None,
  'any',
  ENTRY_TYPE.SERVER),
 ('vehsByClass',
  dict,
  {},
  None,
  'any',
  ENTRY_TYPE.SERVER),
 ('avatarAmmoEquipped',
  set,
  set(),
  None,
  'skip',
  ENTRY_TYPE.SERVER),
 ('vehRankRaised',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.SERVER),
 ('eventGoldByEventID',
  dict,
  {},
  None,
  'skip',
  ENTRY_TYPE.SERVER),
 ('playerRank',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.ACCOUNT_ALL),
 ('quickShellChangerUsageCount',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.SERVER),
 ('goldBankGain',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.ACCOUNT_SELF),
 ('setupsIndexes',
  dict,
  {},
  None,
  'any',
  ENTRY_TYPE.VEHICLE_SELF),
 ('startAmmo',
  list,
  [],
  None,
  'skip',
  ENTRY_TYPE.SERVER),
 ('initialVehicleAmmo',
  list,
  [],
  None,
  'skip',
  ENTRY_TYPE.SERVER),
 ('replayURL',
  str,
  '',
  None,
  'skip',
  ENTRY_TYPE.ACCOUNT_SELF),
 ('currencies',
  dict,
  {},
  MergeDictPacker(),
  'joinByEachPacker',
  ENTRY_TYPE.VEHICLE_SELF),
 ('entityCaptured',
  dict,
  {},
  None,
  'any',
  ENTRY_TYPE.VEHICLE_ALL),
 ('poiCapturedByOwnTeam',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_ALL),
 ('isFirstBlood',
  bool,
  False,
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_ALL),
 ('finishAllPlayersLeft',
  bool,
  False,
  None,
  'skip',
  ENTRY_TYPE.COMMON),
 ('originalBattlePassPoints',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.ACCOUNT_SELF),
 ('battlePassPointsReplay',
  str,
  '',
  ValueReplayPacker(),
  'skip',
  ENTRY_TYPE.ACCOUNT_SELF),
 ('battlePassPoints',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.ACCOUNT_SELF),
 ('eventBattlePassPointsList',
  list,
  [],
  None,
  'skip',
  ENTRY_TYPE.ACCOUNT_SELF),
 ('eventBattlePassPoints',
  int,
  0,
  None,
  'sum',
  ENTRY_TYPE.ACCOUNT_SELF),
 ('prestigeResults',
  dict,
  {},
  None,
  'skip',
  ENTRY_TYPE.VEHICLE_SELF),
 ('finalVehInfo',
  dict,
  {},
  None,
  'skip',
  ENTRY_TYPE.SERVER),
 ('commendationsReceived',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.ACCOUNT_SELF),
 ('commendationsSent',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.ACCOUNT_SELF)]
BATTLE_PASS_RESULTS = [('bpChaptersInfo',
  dict,
  {},
  None,
  'skip',
  ENTRY_TYPE.ACCOUNT_ALL),
 ('bpTopPoints',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.ACCOUNT_ALL),
 ('bpBonusPoints',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.ACCOUNT_ALL),
 ('bpNonChapterPointsDiff',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.ACCOUNT_ALL),
 ('hasBattlePass',
  bool,
  False,
  None,
  'skip',
  ENTRY_TYPE.ACCOUNT_ALL),
 ('battlePassComplete',
  bool,
  False,
  None,
  'skip',
  ENTRY_TYPE.ACCOUNT_ALL),
 ('availablePoints',
  int,
  0,
  None,
  'skip',
  ENTRY_TYPE.ACCOUNT_ALL)]
