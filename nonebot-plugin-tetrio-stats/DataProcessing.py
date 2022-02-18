import aiohttp
from nonebot.log import logger

#获取用户数据
async def getUserData(userName: str) -> dict:
    userName = userName.lower()
    userDataUrl = f'https://ch.tetr.io/api/users/{userName}'
    userData: dict = {}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(userDataUrl) as resp:
                if resp.status != 200:
                    userData['Status'] = False
                else:
                    userData['Status'] = True
                    userData['Success'] = (await resp.json())['success']
                    userData['Data'] = await resp.json()
    except aiohttp.client_exceptions.ClientConnectorError:
        userData['Status'] = False
        logger.error('用户数据获取失败')
    return userData

#获取用户ID
async def getUserID(userData: dict) -> str:
    userID: str = userData['Data']['data']['user']['_id']
    return userID

#获取排位统计数据
async def getLeagueStats(userData: dict) -> dict:
    league = userData['Data']['data']['user']['league']
    leagueStats: dict = {}
    if league['gamesplayed'] == 0:
        leagueStats['Played'] = False
    else:
        leagueStats['Played'] = True
        leagueStats['PPS'] = league['pps']
        leagueStats['APM'] = league['apm']
        if not league['vs']:
            leagueStats['VS'] = 0
        else:
            leagueStats['VS'] = league['vs']
        if league['rank'] == 'z':
            leagueStats['Rank'] = False
        else:
            leagueStats['Rank'] = league['rank'].upper()
        leagueStats['Rating'] = "%.2f" % league['rating']
        leagueStats['Glicko'] = "%.2f" % league['glicko']
        leagueStats['RD'] = "%.2f" % league['rd']
        leagueStats['Standing'] = league['standing']
        leagueStats['LPM'] = float("%.2f" % (league['pps'] * 24))
        leagueStats['APL'] = float("%.2f" % (leagueStats['APM'] / leagueStats['LPM']))
        leagueStats['ADPM'] = float("%.2f" % (leagueStats['VS'] * 0.6))
        leagueStats['ADPL'] = float("%.2f" % (leagueStats['ADPM'] / leagueStats['LPM']))
    return leagueStats

#获取Blitz数据
async def getBlitzData(userID: str) -> dict:
    userBlitzUrl = f'https://ch.tetr.io/api/streams/blitz_userbest_{userID}'
    blitzData: dict = {}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(userBlitzUrl) as resp:
                if resp.status != 200:
                    blitzData['Status'] = False
                else:
                    blitzData['Status'] = True
                    blitzData['Data'] = await resp.json()
    except aiohttp.client_exceptions.ClientConnectorError:
        blitzData['Status'] = False
        logger.error('Blitz数据获取失败')
    return blitzData

#获取Blitz统计数据
async def getBlitzStats(blitzData: dict) -> dict:
    blitzStats: dict = {}
    if blitzData['Data']['data']['records'] == []:
        blitzStats['Played'] = False
    else:
        blitzStats['Played'] = True
        blitzStats['Score'] = blitzData['Data']['data']['records'][0]['endcontext']['score']
    return blitzStats

#获取40L数据
async def getSprintData(userID: str) -> dict:
    userSprintUrl = f'https://ch.tetr.io/api/streams/40l_userbest_{userID}'
    sprintData: dict = {}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(userSprintUrl) as resp:
                if resp.status != 200:
                    sprintData['Status'] = False
                else:
                    sprintData['Status'] = True
                    sprintData['Data'] = await resp.json()
    except aiohttp.client_exceptions.ClientConnectorError:
        sprintData['Status'] = False
        logger.error('40L数据获取失败')
    return sprintData

#获取40L统计数据
async def getSprintStats(sprintData: dict) -> dict:
    sprintStats: dict = {}
    if sprintData['Data']['data']['records'] == []:
        sprintStats['Played'] = False
    else:
        sprintStats['Played'] = True
        sprintStats['Time'] = "%.2f" % (sprintData['Data']['data']['records'][0]['endcontext']["finalTime"] / 1000)
    return sprintStats
