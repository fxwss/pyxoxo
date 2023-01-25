import requests

from dataclasses import dataclass


@dataclass(eq=True, frozen=True)
class Offsets:
    anim_overlays: int
    clientstate_choked_commands: int
    clientstate_delta_ticks: int
    clientstate_last_outgoing_command: int
    clientstate_net_channel: int
    convar_name_hash_table: int
    dwClientState: int
    dwClientState_GetLocalPlayer: int
    dwClientState_IsHLTV: int
    dwClientState_Map: int
    dwClientState_MapDirectory: int
    dwClientState_MaxPlayer: int
    dwClientState_PlayerInfo: int
    dwClientState_State: int
    dwClientState_ViewAngles: int
    dwEntityList: int
    dwForceAttack: int
    dwForceAttack2: int
    dwForceBackward: int
    dwForceForward: int
    dwForceJump: int
    dwForceLeft: int
    dwForceRight: int
    dwGameDir: int
    dwGameRulesProxy: int
    dwGetAllClasses: int
    dwGlobalVars: int
    dwGlowObjectManager: int
    dwInput: int
    dwInterfaceLinkList: int
    dwLocalPlayer: int
    dwMouseEnable: int
    dwMouseEnablePtr: int
    dwPlayerResource: int
    dwRadarBase: int
    dwSensitivity: int
    dwSensitivityPtr: int
    dwSetClanTag: int
    dwViewMatrix: int
    dwWeaponTable: int
    dwWeaponTableIndex: int
    dwYawPtr: int
    dwZoomSensitivityRatioPtr: int
    dwbSendPackets: int
    dwppDirect3DDevice9: int
    find_hud_element: int
    force_update_spectator_glow: int
    interface_engine_cvar: int
    is_c4_owner: int
    m_bDormant: int
    m_bIsLocalPlayer: int
    m_flSpawnTime: int
    m_pStudioHdr: int
    m_pitchClassPtr: int
    m_yawClassPtr: int
    model_ambient_min: int
    set_abs_angles: int
    set_abs_origin: int
    cs_gamerules_data: int
    m_ArmorValue: int
    m_Collision: int
    m_CollisionGroup: int
    m_Local: int
    m_MoveType: int
    m_OriginalOwnerXuidHigh: int
    m_OriginalOwnerXuidLow: int
    m_SurvivalGameRuleDecisionTypes: int
    m_SurvivalRules: int
    m_aimPunchAngle: int
    m_aimPunchAngleVel: int
    m_angEyeAnglesX: int
    m_angEyeAnglesY: int
    m_bBombDefused: int
    m_bBombPlanted: int
    m_bBombTicking: int
    m_bFreezePeriod: int
    m_bGunGameImmunity: int
    m_bHasDefuser: int
    m_bHasHelmet: int
    m_bInReload: int
    m_bIsDefusing: int
    m_bIsQueuedMatchmaking: int
    m_bIsScoped: int
    m_bIsValveDS: int
    m_bSpotted: int
    m_bSpottedByMask: int
    m_bStartedArming: int
    m_bUseCustomAutoExposureMax: int
    m_bUseCustomAutoExposureMin: int
    m_bUseCustomBloomScale: int
    m_clrRender: int
    m_dwBoneMatrix: int
    m_fAccuracyPenalty: int
    m_fFlags: int
    m_flC4Blow: int
    m_flCustomAutoExposureMax: int
    m_flCustomAutoExposureMin: int
    m_flCustomBloomScale: int
    m_flDefuseCountDown: int
    m_flDefuseLength: int
    m_flFallbackWear: int
    m_flFlashDuration: int
    m_flFlashMaxAlpha: int
    m_flLastBoneSetupTime: int
    m_flLowerBodyYawTarget: int
    m_flNextAttack: int
    m_flNextPrimaryAttack: int
    m_flSimulationTime: int
    m_flTimerLength: int
    m_hActiveWeapon: int
    m_hBombDefuser: int
    m_hMyWeapons: int
    m_hObserverTarget: int
    m_hOwner: int
    m_hOwnerEntity: int
    m_hViewModel: int
    m_iAccountID: int
    m_iClip1: int
    m_iCompetitiveRanking: int
    m_iCompetitiveWins: int
    m_iCrosshairId: int
    m_iDefaultFOV: int
    m_iEntityQuality: int
    m_iFOV: int
    m_iFOVStart: int
    m_iGlowIndex: int
    m_iHealth: int
    m_iItemDefinitionIndex: int
    m_iItemIDHigh: int
    m_iMostRecentModelBoneCounter: int
    m_iObserverMode: int
    m_iShotsFired: int
    m_iState: int
    m_iTeamNum: int
    m_lifeState: int
    m_nBombSite: int
    m_nFallbackPaintKit: int
    m_nFallbackSeed: int
    m_nFallbackStatTrak: int
    m_nForceBone: int
    m_nModelIndex: int
    m_nTickBase: int
    m_nViewModelIndex: int
    m_rgflCoordinateFrame: int
    m_szCustomName: int
    m_szLastPlaceName: int
    m_thirdPersonViewAngles: int
    m_vecOrigin: int
    m_vecVelocity: int
    m_vecViewOffset: int
    m_viewPunchAngle: int
    m_zoomLevel: int


def __get_offset_json_from_github() -> dict:
    return requests.get("https://raw.githubusercontent.com/frk1/hazedumper/master/csgo.json").json()


__memoized_offsets = None


def get():
    global __memoized_offsets

    if __memoized_offsets is not None:
        return __memoized_offsets

    json = __get_offset_json_from_github()

    signatures = json["signatures"]
    netvars = json["netvars"]

    # parse the json to the Offsets dataclass
    offsets = Offsets(
        **signatures,
        **netvars
    )

    __memoized_offsets = offsets

    return offsets
