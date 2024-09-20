from sys import platform

if 'linux' in platform:

  # Linux
  m_hPawn = 0x794
  dwLocalPlayerPawn = 0x388C760
  dwEntityList = 0x36F6AC8
  m_iIDEntIndex = 0x1350
  m_iTeamNum = 0x5FC # uint8
  m_iHealth = 0x49C # int32
  m_vecAbsVelocity = 0x548 # Vector3
  m_vecVelocity = 0x558 # CNetworkVelocityVector
  m_flSpeed = 0x534 # float
  dwViewMatrix = 0x388CFC0
  m_vOldOrigin = 0x121C # Vector3
  m_modelState = 0x170 # CModelState
  m_pGameSceneNode = 0x480 # CGameSceneNode