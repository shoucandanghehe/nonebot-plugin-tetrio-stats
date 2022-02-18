from .DataProcessing import *

async def handleMessage(userID: str = None, userName:str = None) -> str:
    message: str = ''
    if userID is None:
        userData = await getUserData(userName)
        if userData['Success']:
            userID = await getUserID(userData)
        else:
            message += f'用户 {userName.upper()} 不存在'
            return message
    else:
        userData = await getUserData(userID)
        if not userData['Success']:
            message += f'用户 {userID.upper()} 不存在'
            return message
    if not userData['Status']:
        message += f'用户数据请求失败，请联系呵呵。'
        return message
    userName = userData['Data']['data']['user']['username']
    leagueStats = await getLeagueStats(userData)
    if not leagueStats['Played']:
        message += f'{userName.upper()} 没有排位统计数据\n'
    else:
        if not leagueStats['Rank']:
            message += f'用户 {userName.upper()} 暂无段位, {leagueStats["Rating"]} TR, 段位分 {leagueStats["Glicko"]}±{leagueStats["RD"]}, 最近十场的数据：\n'
        else:
            message += f'{leagueStats["Rank"]} 段用户 {userName.upper()} {leagueStats["Rating"]} TR (#{leagueStats["Standing"]}), 段位分 {leagueStats["Glicko"]}±{leagueStats["RD"]}, 最近十场的数据：\n'
        message += f'L\'PM: {leagueStats["LPM"]} ( {leagueStats["PPS"]} pps )\n'
        message += f'APM: {leagueStats["APM"]} ( x{leagueStats["APL"]} )\n'
        message += f'ADPM: {leagueStats["ADPM"]} ( x{leagueStats["ADPL"]} ) ( {leagueStats["VS"]}vs )\n'
    blitzData = await getBlitzData(userID)
    if not blitzData['Status']:
        message += f'Blitz数据请求失败，请联系呵呵。\n'
    else:
        blitzStats = await getBlitzStats(blitzData)
        if blitzStats['Played']:
            message += f'Blitz: {blitzStats["Score"]}\n'
    sprintData = await getSprintData(userID)
    if not sprintData['Status']:
        message += f'40L数据请求失败，请联系呵呵。'
    else:
        sprintStats = await getSprintStats(sprintData)
        if sprintStats['Played']:
            message += f'40L: {sprintStats["Time"]}s'
    return message
