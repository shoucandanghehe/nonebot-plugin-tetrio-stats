from nonebot.log import logger

import aiohttp

# 封装请求函数
async def request(Url: str) -> dict:
    data: dict = {}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(Url) as resp:
                if resp.status != 200:
                    data['Status'] = False
                else:
                    data['Status'] = True
                    data['Success'] = (await resp.json())['success']
                    data['Data'] = await resp.json()
    except aiohttp.client_exceptions.ClientConnectorError:
        logger.error('数据获取失败')
        data['Status'] = False
    finally:
        return data

# 获取用户数据
async def getUserData(userName: str = None, userID: str = None) -> dict:
    userData: dict = {}
    if userName and userID:
        logger.error('参数错误')
        userData['Status'] = False
    elif userName:
        userDataUrl = f'https://ch.tetr.io/api/users/{userName}'
        userData = await request(Url = userDataUrl)
    elif userID:
        userDataUrl = f'https://ch.tetr.io/api/users/{userID}'
        userData = await request(Url = userDataUrl)
    else:
        logger.error('参数错误')
        userData['Status'] = False
    return userData

# 获取用户ID
async def getUserID(userData: dict) -> str:
    userID: str = userData['Data']['data']['user']['_id']
    return userID

# 获取排位统计数据
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

# 获取Solo数据
async def getSoloData(userName: str = None, userID: str = None) -> dict:
    soloData: dict = {}
    if userName and userID:
        logger.error('参数错误')
        soloData['Status'] = False
    elif userName:
        userSoloUrl = f'https://ch.tetr.io/api/users/{userName}/records'
        soloData = await request(Url = userSoloUrl)
    elif userID:
        userSoloUrl = f'https://ch.tetr.io/api/users/{userID}/records'
        soloData = await request(Url = userSoloUrl)
    else:
        logger.error('参数错误')
        soloData['Status'] = False
    return soloData

# 获取40L统计数据
async def getSprintStats(soloData: dict) -> dict:
    sprintStats: dict = {}
    if soloData['Data']['data']['records']['40l']['record'] == None:
        sprintStats['Played'] = False
    else:
        sprintStats['Played'] = True
        if soloData['Data']['data']['records']['40l']['rank'] != None:
            sprintStats['Rank'] = soloData['Data']['data']['records']['40l']['rank']
        else:
            sprintStats['Rank'] = False
        sprintStats['Time'] = "%.2f" % (soloData['Data']['data']['records']['40l']['record']['endcontext']['finalTime'] / 1000)
    return sprintStats

# 获取Blitz统计数据
async def getBlitzStats(soloData: dict) -> dict:
    blitzStats: dict = {}
    if soloData['Data']['data']['records']['blitz']['record'] == None:
        blitzStats['Played'] = False
    else:
        blitzStats['Played'] = True
        if soloData['Data']['data']['records']['blitz']['rank'] != None:
            blitzStats['Rank'] = soloData['Data']['data']['records']['blitz']['rank']
        else:
            blitzStats['Rank'] = False
        blitzStats['Score'] = soloData['Data']['data']['records']['blitz']['record']['endcontext']['score']
    return blitzStats

# 处理消息模板
async def handleMessage(userName: str = None, userID: str = None) -> str:
    message: str = ''
    if userName and userID:
        logger.error('参数错误')
        return
    elif userName:
        userData = await getUserData(userName = userName)
        if userData['Status']:
            if not userData['Success']:
                message += f'用户 {userName.upper()} 不存在'
                return message
    elif userID:
        userData = await getUserData(userID = userID)
        if userData['Status']:
            if not userData['Success']:
                message += f'用户 {userID} 不存在'
                return message
    else:
        logger.error('参数错误')
        return
    userName = (userData['Data']['data']['user']['username']).upper()
    userID = await getUserID(userData)
    leagueStats = await getLeagueStats(userData)
    if not leagueStats['Played']:
        message += f'用户 {userName} 没有排位统计数据'
    else:
        if not leagueStats['Rank']:
            message += f'用户 {userName} 暂无段位, {leagueStats["Rating"]} TR'
        else:
            message += f'{leagueStats["Rank"]} 段用户 {userName} {leagueStats["Rating"]} TR (#{leagueStats["Standing"]})'
        message += f', 段位分 {leagueStats["Glicko"]}±{leagueStats["RD"]}, 最近十场的数据：\n'
        message += f'L\'PM: {leagueStats["LPM"]} ( {leagueStats["PPS"]} pps )\n'
        message += f'APM: {leagueStats["APM"]} ( x{leagueStats["APL"]} )\n'
        message += f'ADPM: {leagueStats["ADPM"]} ( x{leagueStats["ADPL"]} ) ( {leagueStats["VS"]}vs )\n'
    soloData = await getSoloData(userID=userID)
    if soloData['Status']:
        sprintStats = await getSprintStats(soloData)
        blitzStats = await getBlitzStats(soloData)
        if sprintStats['Played']:
            message += f'40L: {sprintStats["Time"]}s\n'
            if sprintStats['Rank']:
                message = message.rstrip()
                message += f' ( #{sprintStats["Rank"]} )\n'
        if blitzStats['Played']:
            message += f'Blitz: {blitzStats["Score"]}'
            if blitzStats['Rank']:
                message = message.rstrip()
                message += f' ( #{blitzStats["Rank"]} )\n'
    message = message.rstrip()
    return message
