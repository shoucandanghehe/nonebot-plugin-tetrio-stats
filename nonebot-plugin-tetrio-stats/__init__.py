from nonebot import on_regex, get_driver
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import MessageEvent, Bot, GROUP

from re import I

from .MessageAnalyzer import *
from .StatsDataProcessing import *
from .SQL import *

driver=get_driver()

@driver.on_startup
async def startUP():
    await initDB()

statsQuery = on_regex(pattern=r'^io查', flags=I, permission=GROUP)
userBind = on_regex(pattern=r'^io绑定|^iobind', flags=I, permission=GROUP)

@statsQuery.handle()
async def handleStatsQuery(bot: Bot, event: MessageEvent, matcher: Matcher):
    message: str = str(event.get_message())
    decodedMessage = await handleStatsQueryMessage(message)
    if decodedMessage['Success']:
        if decodedMessage['Type'] == 'AT':
            bindInfo = await queryBindInfo(decodedMessage['QQNumber'])
            if bindInfo['Hit']:
                message = '* 由于无法验证绑定信息，不能保证查询到的用户为本人' + await handleMessage(bindInfo['UserID'])
            else:
                message = '未查询到绑定信息'
        elif decodedMessage['Type'] == 'ME':
            queryResult = await queryBindInfo(QQNumber=event.sender.user_id)
            if queryResult['Hit']:
                message = await handleMessage(userID=queryResult['UserID'])
            else:
                message = '您还没有绑定账号'
        elif decodedMessage['Type'] == 'ID':
            message = await handleMessage(userID=decodedMessage['UserID'])
        elif decodedMessage['Type'] == 'Name':
            message = await handleMessage(userName=decodedMessage['UserName'])
    else:
        message = decodedMessage['Message']
    await matcher.send(message)

@userBind.handle()
async def bindUser(event: MessageEvent, matcher: Matcher):
    message: str = str(event.get_message())
    decodedMessage = await handleUserBindMessage(message)
    if decodedMessage['Success']:
        QQNumber = event.sender.user_id
        if decodedMessage['Type'] == 'ID':
            userData = await getUserData(userID=decodedMessage['UserID'])
            if userData['Status']:
                if userData['Success']:
                    message = await writeBindInfo(QQNumber=QQNumber, userID=decodedMessage['UserID'])
                else:
                    message = '用户不存在'
            else:
                message = '获取用户失败'
        elif decodedMessage['Type'] == 'Name':
            userData = await getUserData(userName=decodedMessage['UserName'])
            if userData['Status']:
                if userData['Success']:
                    userID = await getUserID(userData)
                    message = await writeBindInfo(QQNumber=QQNumber, userID=userID)
                else:
                    message = '用户不存在'
            else:
                message = '获取用户失败'
    else:
        message = decodedMessage['Message']
    await matcher.send(message)
