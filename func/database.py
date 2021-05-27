import pyrebase, random, typing


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
            "black": ":black_circle:",
        },

        "embedColors": {
            "white": "F0F0F0",
        },
    },

    "guild": {
        "prefix": "c-"
    }
}


disc = {
    "blue": ":blue_circle:",
    "yellow": ":yellow_circle:",
    "purple": ":purple_circle:",
    "orange": ":orange_circle:",
    "green": ":green_circle:",
    "red": ":red_circle:",
    "brown": ":brown_circle:",
}

background = {
    "black": ":black_circle:",
    "white": ":white_circle:",
}

embedColor = {
    "white": "F0F0F0",
    "yellow": "FFF200",
    "orange": "FC6600",
    "red": "D30000",
    "pink": "FC0FC0",
    "violet": "B200ED",
    "blue": "0018F9",
    "green": "388143",
    "brown": "7C4700",
    "grey": "828282",
    "black": "000000",
    "gold": "F9A602",
    "baby_blue": "89CFEF",
    "navy": "000080",
    "lime": "C7EA46",
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
        return data
    
    async def shop():
        dataDict = {}
        dataDict['discs'] = disc
        dataDict['backgrounds'] = background
        dataDict['embedColors'] = embedColor
        return dataDict


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

    async def theme(userId):
        userData = await Get.user(userId)
        invData = await Get.inventory(userId)
        primaryDisc = [value for key, value in invData['discs'].items() if value == userData['primaryDisc']]
        secondaryDisc = [value for key, value in invData['discs'].items() if value == userData['secondaryDisc']]
        background = [value for key, value in invData['backgrounds'].items() if value == userData['background']]
        embedColor = [value for key, value in invData['embedColors'].items() if value == userData['embedColor']]
        return [primaryDisc, secondaryDisc, background, embedColor]


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
            # if key == "primaryDisc": value = [k for k, v in disc.items() if v == value]; value = value[0]
            # if key == "secondaryDisc": value = [k for k, v in disc.items() if v == value]; value = value[0]
            # if key == "background": value = [k for k, v in background.items() if v == value]; value = value[0]
            # if key == "embedColor": value = [k for k, v in embedColor.items() if v == value]; value = value[0]
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
    
    async def inventory(userId, child, key, value):
        data = await Get.inventory(userId)
        db.child("connect-4").child("users").child(userId).child("inventory").child(child).update({key: value})

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