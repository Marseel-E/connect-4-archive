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
        "draws": 0
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
        return data


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
        for key, value in dataVal.items():
            dataDict[key] = value
        return dataDict


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