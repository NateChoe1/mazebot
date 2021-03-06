import discord
import random

players = {}

class MyClient(discord.Client):
    hotkey = "!"
    async def on_message(self, message):
        if ("<@752081210355744828>" in message.content or "<@!752081210355744828>" in message.content or message.content.startswith(self.hotkey)):
            messageParts = message.content.split(" ");
            if (messageParts[0].startswith(self.hotkey)):
                messageParts[0] = messageParts[0][1:]
                messageParts.insert(0, "")
            if (len(messageParts) == 1):
                await message.channel.send("You pinged me and typed nothing.")
            elif (messageParts[1] == "start" and not message.author.id in players):
                width = 11
                height = 11
                
                if (len(messageParts) == 4):
                    if (int(messageParts[2]) % 2 == 0 and int(messageParts[3]) % 2 == 0):
                        await message.channel.send("You sent even numbers into the size inputs. Only odd numbers are allowed. The size will be set to 11x11 (default)")
                    elif(int(messageParts[2]) < 5 or int(messageParts[3]) < 5):
                        await message.channel.send("The maze you sent is too small. Width and height must be at least 5. Setting width and height to 5, 5")
                        width = 5
                        height = 5
                    else:
                        width = int(messageParts[2])
                        height = int(messageParts[3])
                else:
                    await message.channel.send("Not enough inputs. Defaulting to 11x11.")
                players[message.author.id] = Player(width, height, message.channel, message.author.id)
                await players[message.author.id].displayMaze()
            elif (messageParts[1] == "start"):
                await message.channel.send("You're already playing a game.")
            elif (messageParts[1] == "display"):
                await players[message.author.id].displayMaze()
            elif (messageParts[1] == "quit" and message.author.id in players):
                del players[message.author.id]
                await message.channel.send("Game ended")
            elif (messageParts[1] == "quit"):
                await message.channel.send("You haven't started a game yet.")
            elif(message.author.id in players and (messageParts[1] == "w" or messageParts[1] == "a" or messageParts[1] == "s" or messageParts[1] == "d")):
                if (messageParts[1] == "w"):
                    await players[message.author.id].move("up")
                if (messageParts[1] == "a"):
                    await players[message.author.id].move("left")
                if (messageParts[1] == "s"):
                    await players[message.author.id].move("down")
                if (messageParts[1] == "d"):
                    await players[message.author.id].move("right")
            elif (messageParts[1] == "w" or messageParts[1] == "a" or messageParts[1] == "s" or messageParts[1] == "d"):
                await message.channel.send("The game hasn't started yet.")
            elif (messageParts[1] == "getInviteLink"):
                await message.channel.send("The invite link is https://discord.com/oauth2/authorize?client_id=752081210355744828&scope=bot")
            elif (messageParts[1] == "source"):
                await message.channel.send("The source code can be found at https://github.com/NateChoe1/mazebot")
            else:
                await message.channel.send("You pinged me but didn't type a command. Or maybe you put the ping after the message, or something, but you didn't format it right.")
    async def on_raw_reaction_remove(self, payload):
        await self.process_reaction(str(payload.emoji), payload.user_id)
    async def on_reaction_add(self, reaction, user):
        await self.process_reaction(reaction.emoji, user.id)
    async def process_reaction(self, emoji, user_id):
        if (user_id in players):
            direction = ""
            if (emoji == "⬆"):
                await players[user_id].move("up")
            if (emoji == "⬅"):
                await players[user_id].move("left")
            if (emoji == "⬇"):
                await players[user_id].move("down")
            if (emoji == "➡"):
                await players[user_id].move("right")

class Player():
    def __init__(self, width, height, channel, user_id):
        self.maze = []
        self.x = 1
        self.y = 1
        self.beenDisplayed = False
        self.messageChannel = channel
        self.user_id = user_id
        for y in range(0, height):
            row = []
            for x in range(0, width):
                row.append(False)
            self.maze.append(row)

        self.maze[1][1] = True
        stack = [[1, 1]]
        directions = [[0, 1], [1, 0], [0, -1], [-1, 0]]
        while (len(stack) > 0):
            point = stack[len(stack)-1]
            availableDirections = []
            for direction in directions:
                newPoint = [point[0]+direction[0]*2, point[1]+direction[1]*2]
                if (newPoint[0] < 0 or newPoint[0] >= height or newPoint[1] < 0 or newPoint[1] >= width or self.maze[newPoint[0]][newPoint[1]]):
                    continue
                availableDirections.append(direction)
            if (len(availableDirections) == 0):
                stack.pop()
            else:
                direction = random.choice(availableDirections)
                self.maze[point[0]+direction[0]][point[1]+direction[1]] = True
                self.maze[point[0]+2*direction[0]][point[1]+2*direction[1]] = True
                stack.append([point[0]+2*direction[0], point[1]+2*direction[1]])

    async def displayMaze(self):
        if (not self.beenDisplayed):
            self.mazeMessages = []
        for y in range(0, len(self.maze)):
            row = ""
            for x in range(0, len(self.maze[y])):
                if (y == self.y and x == self.x):
                    row = row + "\U0001F600"
                elif (y == len(self.maze)-2 and x == len(self.maze[y])-2):
                    row = row + "✅"
                elif (self.maze[y][x]):
                    row = row + "⬛"
                else:
                    row = row + "❌"
            if (not self.beenDisplayed):
                self.mazeMessages.append(await self.messageChannel.send(row))
            else:
                await self.mazeMessages[x].edit(content=row)
        if (not self.beenDisplayed):
            await self.mazeMessages[-1].add_reaction("⬆")
            await self.mazeMessages[-1].add_reaction("➡")
            await self.mazeMessages[-1].add_reaction("⬇")
            await self.mazeMessages[-1].add_reaction("⬅")
        self.beenDisplayed = True

    async def refreshLine(self, y):
        row = ""
        for x in range(0, len(self.maze[y])):
            if (y == self.y and x == self.x):
                row = row + "\U0001F600"
            elif (y == len(self.maze)-2 and x == len(self.maze[y])-2):
                row = row + "✅"
            elif (self.maze[y][x]):
                row = row + "⬛"
            else:
                row = row + "❌"
        await self.mazeMessages[y].edit(content=row)

    async def move(self, direction):
        changes = [0, 0]
        oldY = self.y
        if (direction == "left"):
            changes = [0, -1]
        if (direction == "up"):
            changes = [-1, 0]
        if (direction == "right"):
            changes = [0, 1]
        if (direction == "down"):
            changes = [1, 0]
        if (self.maze[self.y+changes[0]][self.x+changes[1]]):
            self.y += changes[0]
            self.x += changes[1]
        await self.refreshLine(oldY)
        await self.refreshLine(self.y)

        if (self.y == len(self.maze)-2 and self.x == len(self.maze[0])-2):
            await self.messageChannel.send("You win!")
            del players[self.user_id]
client = MyClient()
secret_file = open("secrets.txt", "r")
client.run(secret_file.read())
