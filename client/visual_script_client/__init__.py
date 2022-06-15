# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/__init__.py
from constants import IS_EDITOR, IS_VS_EDITOR
from visual_script.misc import ASPECT
from visual_script.registrar import VSBlockRegistrar
from contexts.sound_notifications_context import SoundNotificationsContext
from contexts.cgf_context import CGFGameObjectContext
if not IS_EDITOR:
    import arena_blocks
    import vehicle_blocks
    import scene_blocks
    import event_platform_blocks
    import triggers_blocks
    import hint_blocks
    import marker_blocks
    import player_blocks
    import sound_blocks
    import game_settings_blocks
    import hangar_blocks
    import battle_hud_block
    import cgf_blocks
g_blockRegistrar = VSBlockRegistrar(ASPECT.CLIENT)
if not IS_EDITOR:
    g_blockRegistrar.regBlocksFromModule(event_platform_blocks)
    g_blockRegistrar.regBlocksFromModule(arena_blocks)
    g_blockRegistrar.regBlocksFromModule(vehicle_blocks)
    g_blockRegistrar.regBlocksFromModule(scene_blocks)
    g_blockRegistrar.regBlocksFromModule(triggers_blocks)
    g_blockRegistrar.regBlocksFromModule(hint_blocks)
    g_blockRegistrar.regBlocksFromModule(marker_blocks)
    g_blockRegistrar.regBlocksFromModule(player_blocks)
    g_blockRegistrar.regBlocksFromModule(sound_blocks)
    g_blockRegistrar.regBlocksFromModule(game_settings_blocks)
    g_blockRegistrar.regBlocksFromModule(battle_hud_block)
    g_blockRegistrar.regBlocksFromModule(cgf_blocks)
g_blockRegistrar.regContext(SoundNotificationsContext)
g_blockRegistrar.regContext(CGFGameObjectContext)
if not IS_VS_EDITOR:
    from visual_script_client import client_perk_blocks
    g_blockRegistrar.regBlocksFromModule(client_perk_blocks)
g_hangarBlockRegistrar = VSBlockRegistrar(ASPECT.HANGAR)
if not IS_EDITOR:
    g_hangarBlockRegistrar.regBlocksFromModule(hangar_blocks)
    g_hangarBlockRegistrar.regBlocksFromModule(hint_blocks)
