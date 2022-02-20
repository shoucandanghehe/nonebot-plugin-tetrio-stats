from re import match

# statsQuery
async def handleStatsQueryMessage(message: str) -> dict:
    CMD_ALIASES = ['io查']
    ME = ['我', '自己', '私', '俺', 'me']
    message = (message.strip()).lower()
    # 剔除命令前缀
    for i in CMD_ALIASES:
        if message.startswith(i):
            message = message.replace(i, '')
            message = message.strip()
            break
    if message == '' or message.isspace():
        return {'Success': False, 'Type': None, 'Message': '用户名为空'}
    elif message.startswith('[cq:at,qq='):
        try:
            QQNumber:int = int((str(message)).split('[cq:at,qq=')[1].split(']')[0])
        except ValueError:
            return {'Success': False, 'Type': None, 'Message': 'QQ号码不合法'}
        else:
            return {'Success': True, 'Type': 'AT', 'Message': '', 'QQNumber': QQNumber}
    elif message in ME:
        return {'Success': True, 'Type': 'ME', 'Message': '',}
    elif match(r'^[a-f0-9]{24}$', message):
        return {'Success': True, 'Type': 'ID', 'Message': '', 'UserID': message}
    elif not match(r'^[a-zA-Z0-9_-]{3,16}$', message):
        return {'Success': False, 'Type': None, 'Message': '用户名不合法'}
    else:
        return {'Success': True, 'Type': 'Name', 'Message': '', 'UserName': message}

# userBind
async def handleUserBindMessage(message: str) -> dict:
    CMD_ALIASES = ['io绑定', 'iobind']
    message = (message.strip()).lower()
    # 剔除命令前缀
    for i in CMD_ALIASES:
        if message.startswith(i):
            message = message.replace(i, '')
            message = message.strip()
            break
    if message == '' or message.isspace():
        return {'Success': False, 'Type': None, 'Message': '用户名为空'}
    elif match(r'^[a-f0-9]{24}$', message):
        return {'Success': True, 'Type': 'ID', 'Message': '', 'UserID': message}
    elif not match(r'^[a-zA-Z0-9_-]{3,16}$', message):
        return {'Success': False, 'Type': None, 'Message': '用户名不合法'}
    else:
        return {'Success': True, 'Type': 'Name', 'Message': '', 'UserName': message}
