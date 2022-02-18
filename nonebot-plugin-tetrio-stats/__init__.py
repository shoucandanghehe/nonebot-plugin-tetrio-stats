from nonebot import on_command
from nonebot.rule import startswith
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import MessageEvent, Bot, GROUP
from nonebot.log import logger

from re import match
import os
import sqlite3
from asyncio import sleep

from .DataProcessing import *
from .MessageProcessing import *

if not os.path.exists('data/nonebot-plugin-tetrio-stars'):
    if not os.path.exists('data'):
        os.mkdir('data')
    os.mkdir('data/nonebot-plugin-tetrio-stars')

db = sqlite3.connect('data/nonebot-plugin-tetrio-stars/data.db')
cursor = db.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS BIND
                (QQ INTEGER NOT NULL,
                USERID TEXT NOT NULL)''')
db.commit()

statsQuery = on_command('IOStats', aliases={'IO查', 'io查'}, rule=startswith('io', ignorecase=True), permission=GROUP)
userBind = on_command('IOBind', aliases={'IOBind', 'iobind', 'io绑定', 'IO绑定'}, rule=startswith('io', ignorecase=True), permission=GROUP)

@statsQuery.handle()
async def handleStatsQuery(bot: Bot, event: MessageEvent, matcher: Matcher, args: Message = CommandArg()):
    userName = args.extract_plain_text()
    if userName == '':
        if (str(event.get_message())).find('[CQ:at,qq=') != -1:
            await matcher.send('TODO')
        else:
            await matcher.send('用户名为空')
    elif userName in ['我', '自己', '私', '俺', 'me']:
        #查询数据库中是否已经绑定
        cursor.execute('SELECT * FROM BIND WHERE QQ = ?', (event.sender.user_id,))
        if cursor.fetchone() is None:
            await matcher.send('你还没有绑定账号')
        else:
            cursor.execute('SELECT USERID FROM BIND WHERE QQ = ?', (event.sender.user_id,))
            userID = cursor.fetchone()[0]
            message = await handleMessage(userID=userID)
            await matcher.send(message)
    elif match(r'^[a-z0-9]{24}$', userName):
        message = await handleMessage(userID=userName)
        await matcher.send(message)
    elif not match(r'^[a-zA-Z0-9_-]{3,16}$', userName):
        await matcher.send('用户名不合法')
    else:
        message = await handleMessage(userName=userName)
        messageID = (await matcher.send(message))['message_id']
        #延迟一分半撤回
        await sleep(90)
        logger.info('尝试撤回消息')
        #撤回消息
        await bot.delete_msg(message_id=messageID)

@userBind.handle()
async def bindUser(event: MessageEvent, matcher: Matcher, args: Message = CommandArg()):
    userName = args.extract_plain_text()
    if userName:
        #检查用户名是否合法
        if match(r'^[a-zA-Z0-9_-]{3,16}$', userName):
            userData = await getUserData(userName)
            #查询用户是否存在
            if userData['Success']:
                #获取用户ID
                userID = await getUserID(userData)
                #读取数据库中是否已经存在该用户
                cursor.execute('SELECT * FROM BIND WHERE QQ = ?', (event.sender.user_id,))
                if cursor.fetchone() is None:
                    #插入数据库
                    cursor.execute('INSERT INTO BIND (QQ, USERID) VALUES (?, ?)', (event.sender.user_id, userID))
                    db.commit()
                    await matcher.send('绑定成功')
                else:
                    #如果存在，则更新
                    cursor.execute('UPDATE BIND SET USERID = ? WHERE QQ = ?', (userID, event.sender.user_id))
                    db.commit()
                    await matcher.send('更新成功')
            else:
                await matcher.send('用户不存在')
        else:
            await matcher.send('用户名不合法')
    else:
        await matcher.send('用户名为空')
