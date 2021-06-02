import pyrebase, random, typing
from func.items import items


config = {
  "apiKey": "AIzaSyAGOCBHwfs22dA8o4RuGK4XdQHqPahzKfk",
  "authDomain": "discord-bot-101df.firebaseapp.com",
  "databaseURL": "https://discord-bot-101df.firebaseio.com",
  "projectId": "discord-bot-101df",
  "storageBucket": "discord-bot-101df.appspot.com",
  "messagingSenderId": "436184825011",
  "appId": "1:436184825011:web:5cadee57c3cd63336284c6"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

default = {
    "user": {
        "coins": 0,
        "playing": False,
        "wins": 0,
        "loses": 0,
        "draws": 0,
        "exp": 0,
        "level": 0,
        "rank": 0,
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


class Fetch:

    async def game_ids():
        data = db.child("connect-4").child("games").get()
        dataList = []
        dataVal = data.val()
        if dataVal is None:
            return [0000000000000000]
        for key, value in dataVal.items():
            dataList.append(key)
        return dataList
    
    async def items():
        return items


class Get:

    async def game(gameId): 
        data = db.child("connect-4").child("games").child(gameId).get()
        dataVal = data.val()
        dataDict = {}
        if dataVal is None:
            return False
        for key, value in dataVal.items():
            dataDict[key] = value
        return dataDict    

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

    async def game(gameId, key, value, overwrite : typing.Optional[bool] = False):
        game = await Get.game(gameId)
        if not (game): return False
        if (overwrite):
            db.child("connect-4").child("games").child(gameId).update({key: value})
        else:
            db.child("connect-4").child("games").child(gameId).update({key: game[key] + value})

    async def user(userId, key, value, overwrite : typing.Optional[bool] = False):
        user = await Get.user(userId)
        if not (user): return False
        if (overwrite):
            db.child("connect-4").child("users").child(userId).update({key: value})
        else:
            db.child("connect-4").child("users").child(userId).update({key: user[key] + value})
    
    async def guild(guildId, key, value, overwrite : typing.Optional[bool] = False):
        guild = await Get.guild(guildId)
        if not (guild): return False
        if (overwrite):
            db.child("connect-4").child("guilds").child(guildId).update({key: value})
        else:
            db.child("connect-4").child("guilds").child(guildId).update({key: guild[key] + value})
    
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
        db.child("connect-4").child("games").child(gameId).update({"board": [['0']*7]*6})
        await Update.game(gameId, "players", [playerOneId, playerTwoId], True)
        await Update.game(gameId, "turn", playerOneId, True)
        await Update.game(gameId, "status", "on-going", True)
        await Update.game(gameId, "id", gameId, True)
        game = await Get.game(gameId)
        return game


class Delete:

    async def game(gameId):
        db.child("connect-4").child("games").child(gameId).remove()