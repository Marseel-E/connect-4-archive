import pyrebase, random, typing
from func.items import items


config = {...}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

default = {
    "user": {
        "coins": 0,
        "cash": 0,
        "bank": 0,
        "points": 0,
        "playing": False,
        "wins": 0,
        "loses": 0,
        "draws": 0,
        "exp": 0,
        "level": 1,
        "rank": 0,
        "premium": False,
        "primaryDisc": ":blue_circle:",
        "secondaryDisc": ":yellow_circle:",
        "background": ":black_circle:",
        "embedColor": "F0F0F0"
    },

    "inventory": {

        "discs": {
            "blue": ":blue_circle:",
            "yellow": ":yellow_circle:",
        },

        "backgrounds": {
            "black_circle": ":black_circle:",
        },

        "embedColors": {
            "white": "F0F0F0",
        },
    },

    "guild": {
        "prefix": "c-"
    }
}

games = {}

ranksData = {
    "bronze": 100,
    "silver": 1000,
    "gold": 2500,
    "diamond": 5000,
    "ruby": 10000,
}

class Developers:

    def get():
        d = db.child("connect-4").child("developers").get()
        dv = d.val()
        if dv is None:
            db.child("connect-4").update({"developers": [470866478720090114]})
            return [470866478720090114]
        return dv

    async def add(id: int):
        d = Developers.get(); d.append(id)
        db.child("connect-4").update({"developers": d})

    async def remove(id: int):
        d = [i for i in Developers.get() if i != id]
        db.child("connect-4").update({"developers": d})


class Lobby:

    data = {}

    async def fetch():
        return Lobby.data

    async def get(userId):
        for key, value in Lobby.data.items():
            if key == userId:
                return {key: value}

    async def update(userId, key, value, overwrite : typing.Optional[bool] = False):
        if (overwrite):
            Lobby.data[userId] = {key: value}
            return
        uData = await Lobby.get(userId)
        Lobby.data[userId] = {key: uData[key] + value}
    
    async def delete(userId):
        Lobby.data.pop(userId)

class Fetch:

    async def game_ids():
        return games.keys()
    
    async def items():
        return items
    
    async def user_ids():
        data = db.child("connect-4").child("users").get()
        dataList = []
        dataVal = data.val()
        if dataVal is None:
            return [0000000000000000]
        for key, value in dataVal.items():
            dataList.append(key)
        return dataList


class Get:

    #! Fix
    # def blacklist():
    #     data = db.child("connect-4").child("blacklist").get()
    #     dataList = []
    #     dataVal = data.val()
    #     if dataVal is None:
    #         return [0000000000000000]
    #     for key in dataVal:
    #         dataList.append(key)
    #     return dataList

    def rank(points):
        rank = "Unranked"
        for key, value in ranksData.items():
            if points >= value:
                rank = key
            else:
                return rank

    async def game(gameId): 
        return games[gameId]

    async def user(userId): 
        data = db.child("connect-4").child("users").child(userId).get()
        dataVal = data.val()
        dataDict = {}
        if dataVal is None:
            db.child("connect-4").child("users").update({userId: default['user']})
            return default['user']
        for key, value in default['user'].items():
            if key not in dataVal.keys():
                db.child("connect-4").child("users").child(userId).update({key: value})
            else:
                pass
        for key, value in dataVal.items():
            dataDict[key] = value
        return dataDict
    
    async def guild(guildId):
        data = db.child("connect-4").child("guilds").child(guildId).get()
        dataVal = data.val()
        dataDict = {}
        if dataVal is None:
            db.child("connect-4").child("guilds").update({guildId: default['guild']})
            return default['guild']
        for key, value in default['guild'].items():
            if key not in dataVal.keys():
                db.child("connect-4").child("guilds").child(guildId).update({key: value})
            else:
                pass
        for key, value in dataVal.items():
            dataDict[key] = value
        return dataDict
    
    async def inventory(userId):
        data = db.child("connect-4").child("users").child(userId).child("inventory").get()
        dataVal = data.val()
        dataDict = {}
        if dataVal is None:
            db.child("connect-4").child("users").child(userId).update({"inventory": default['inventory']})
            return default['inventory']
        for key1, value in default['inventory'].items():
            for key, value in value.items():
                if key not in dataVal[key1].keys():
                    await Update.inventory(userId, key1, key, value)
                else:
                    pass
        for key, value in dataVal.items():
            dataDict[key] = value
        return dataDict

    async def theme(game): 
        one = await Get.user(game['players'][0])
        two = await Get.user(game['players'][1])
        background = one['background']
        embedColor = one['embedColor']
        oneP = one['primaryDisc']; oneS = one['secondaryDisc']; twoP = two['primaryDisc']; twoS = two['secondaryDisc']
        if oneP != twoP:
            oneDisc = oneP
            twoDisc = twoP
        elif oneP != twoS:
            oneDisc = oneP
            twoDisc = twoS          
        elif oneS != twoP:
            oneDisc = oneS
            twoDisc = twoP    
        elif oneS != twoS:
            oneDisc = oneS
            twoDisc = twoS          
        else:
            oneDisc = ":blue_circle:"
            twoDisc = ":yellow_circle:"
        dataDict = {
            "oneDisc": oneDisc,
            "twoDisc": twoDisc,
            "background": background,
            "embedColor": embedColor
        }
        return dataDict
    
    async def item(name):
        return items[name]


class Generate:

    async def game_id():
        gameId = ""
        for i in range(1,16):
            gameId += str(random.randint(1,9))
        return gameId


class Update:

    #! Fix
    # async def blacklist(id, delete : typing.Optional[bool] = False):
    #     if (delete):
    #         db.child("connect-4").child("blacklist").child(id).delete()
    #     else:
    #         data = Get.blacklist()
    #         data = data.append(id)
    #         db.child("connect-4").update({"blacklist": data})

    async def game(gameId, key, value, overwrite : typing.Optional[bool] = False):
        if not (games[gameId]): return False
        if (overwrite):
            games[gameId][key] = value
        else:
            games[gameId][key] = games[gameId][key] + value

    async def user(userId, key, value, overwrite : typing.Optional[bool] = False):
        user = await Get.user(userId)
        if not (user): return False
        if (overwrite):
            try:
                if value in ['True', 'False', True, False, 'true', 'false']:
                    value = bool(value); return
                value = int(value)
            except ValueError:
                value = str(value)
            finally:
                db.child("connect-4").child("users").child(userId).update({key: value}); return
        db.child("connect-4").child("users").child(userId).update({key: int(user[key]) + int(value)})
    
    async def guild(guildId, key, value, overwrite : typing.Optional[bool]):
        guild = await Get.guild(guildId)
        if not (guild): return False
        if (overwrite):
            db.child("connect-4").child("guilds").child(guildId).update({key: value})
        else:
            db.child("connect-4").child("guilds").child(guildId).update({key: int(guild[key]) + int(value)})
    
    async def inventory(userId, child, item_name):
        data = await Fetch.items()
        icon = [v['icon'] for key, value in data.items() if key == child for k, v in value.items() if k == item_name]
        db.child("connect-4").child("users").child(userId).child("inventory").child(child).update({item_name: icon[0]})

class Create:

    async def game(playerOneId, playerTwoId):
        gameId = await Generate.game_id()
        gameIds = await Fetch.game_ids()
        while gameId in gameIds:
            gameId = await Generate.game_id()
        gData = {
            "board": [['0']*7 for i in range(6)],
            "players": [playerOneId, playerTwoId],
            "turn": playerOneId,
            "status": "on-going",
            "id": gameId
        }
        games.update({gameId: gData})
        return games[gameId]


class Delete:

    async def game(gameId):
        games.pop(gameId)
    
    async def user(userId):
        db.child("connect-4").child("users").child(userId).remove()
    
    async def guild(guildId):
        db.child("connect-4").child("guilds").child(guildId).remove()
