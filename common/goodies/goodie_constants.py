# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/goodies/goodie_constants.py
from enum import Enum
MAX_ACTIVE_PERSONAL_BOOSTERS = 3
MAX_ACTIVE_EVENT_BOOSTERS = 1
MAX_ACTIVE_BOOSTERS = MAX_ACTIVE_PERSONAL_BOOSTERS + MAX_ACTIVE_EVENT_BOOSTERS

class GOODIE_STATE:
    INACTIVE = 0
    ACTIVE = 1
    USED = 2


class GOODIE_VARIETY:
    DISCOUNT = 0
    BOOSTER = 1
    DEMOUNT_KIT = 2
    RECERTIFICATION_FORM = 3
    DISCOUNT_NAME = 'discount'
    BOOSTER_NAME = 'booster'
    DEMOUNT_KIT_NAME = 'demountKit'
    RECERTIFICATION_FORM_NAME = 'recertificationForm'
    NAME_TO_ID = {DISCOUNT_NAME: DISCOUNT,
     BOOSTER_NAME: BOOSTER,
     DEMOUNT_KIT_NAME: DEMOUNT_KIT,
     RECERTIFICATION_FORM_NAME: RECERTIFICATION_FORM}
    DISCOUNT_LIKE = (DISCOUNT, DEMOUNT_KIT, RECERTIFICATION_FORM)


class GOODIE_TARGET_TYPE:
    ON_BUY_PREMIUM = 1
    ON_BUY_SLOT = 2
    ON_POST_BATTLE = 3
    ON_BUY_GOLD_TANKMEN = 4
    ON_FREE_XP_CONVERSION = 5
    ON_BUY_VEHICLE = 6
    ON_EPIC_META = 7
    ON_DEMOUNT_OPTIONAL_DEVICE = 8
    EPIC_POST_BATTLE = 9
    ON_DROP_SKILL = 10


class GOODIE_CONDITION_TYPE:
    MAX_VEHICLE_LEVEL = 1


class GOODIE_RESOURCE_TYPE:
    GOLD = 10
    CREDITS = 20
    XP = 30
    CREW_XP = 40
    FREE_XP = 50
    FL_XP = 60
    FREE_XP_CREW_XP = 70
    FREE_XP_MAIN_XP = 80


class GOODIE_NOTIFICATION_TYPE:
    EMPTY = 1
    REMOVED = 3
    DISABLED = 4
    ENABLED = 5


class PR2BoosterIDs(object):
    XP = 121001
    CRED = 121003
    XP_CREW_FREE = 121005
    XP_DEF = 121000
    CRED_DEF = 121002
    XP_CREW_FREE_DEF = 121004
    ITEMS = (XP_DEF, CRED_DEF, XP_CREW_FREE_DEF)
    ADVANCED_ITEMS = (XP, CRED, XP_CREW_FREE)
    ALL_ITEMS = ITEMS + ADVANCED_ITEMS


class BoosterCategory(Enum):
    PERSONAL = 'personal'
    CLAN = 'clan'
    EVENT = 'event'
