from nonebot.log import logger

import sqlite3
import os

_DB_FILE = 'data/nonebot-plugin-tetrio-stats/data.db'

# 初始化数据库
async def initDB():
    if not os.path.exists(os.path.dirname(_DB_FILE)):
        os.makedirs(os.path.dirname(_DB_FILE))
    db = sqlite3.connect(_DB_FILE)
    cursor = db.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS BIND
                    (QQ INTEGER NOT NULL,
                    USERID TEXT NOT NULL)''')
    db.commit()
    db.close()
    logger.info('数据库初始化完成')

# 查询绑定信息
async def queryBindInfo(QQNumber: int) -> dict:
    db = sqlite3.connect(_DB_FILE)
    cursor = db.cursor()
    cursor.execute('SELECT USERID FROM BIND WHERE QQ = ?', (QQNumber,))
    userID = cursor.fetchone()
    db.commit()
    db.close()
    if userID is None:
        return {'Hit': False, 'UserID': None}
    else:
        return {'Hit': True, 'UserID': userID[0]}

# 写入绑定信息
async def writeBindInfo(QQNumber: int, userID: str) -> str:
    db = sqlite3.connect(_DB_FILE)
    cursor = db.cursor()
    info = await queryBindInfo(QQNumber)
    if info['Hit']:
        cursor.execute('UPDATE BIND SET USERID = ? WHERE QQ = ?', (userID, QQNumber))
        message = '更新成功'
    else:
        cursor.execute('INSERT INTO BIND (QQ, USERID) VALUES (?, ?)', (QQNumber, userID))
        message = '绑定成功'
    db.commit()
    db.close()
    return message
