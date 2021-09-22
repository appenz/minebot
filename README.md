# pybot - A Minecraft bot written in Python using Mineflayer

pybot is a Minecraft bot written using the Mineflayer framework via the Python to Javascript bridge. It is built for practical utility automating such tasks as mining for resources, mining out rooms or long corridors, building bridges, farmin, building structures and moving around resources between chests. Tested with Java 1.16.5.

### Authors

Guido Appenzeller, Daniel Appenzeller

### License

Released under Apache 2.0

## Functionality

Simple commands are given via chat. The bot has a specific "master" player that it will listen to. Try "come", "inventory" or "status" to get an idea. Other users can also give commands but need to preface it with a callsign.

PyBot starts most complex activities around a chest. There are two types:
- For an activity that dodesn't need a specifi direction like farming an area, it's just a chest. Material (e.g. seeds) and resources (e.g. wheat) will be taken from and later placed into that chest.
- For activities that do have a direction (e.g. dig a tunnel in a specific direction), starting point is a chest and the direction is indicated by placing a torch on the ground directly next to the chest. 

For these activities, have the bot come next to the chest and once it is there tell it to "farm" or "mine 3x3".

### Farming

To start, place a chest in the area you want to farm and start with "farm". The bot will take seeds from the cest, and plant them in any nearby farmland that it can reach. If there are fully grown crops, the pot will harvest them and place them and any extra seeds in the chest. Chat "stop" to stop the bot.

### Mining

Supports:
- Strip mining and lighting up corridors with torches. Try "mine fast", "mine 3x3" or "mine 5x5"
- The bot will looking for valuable ores off corridors, usually with a max distance of 5
- Try "boxmine" to mine out large areas for underground rooms
- The bot will automatically bridge across chasms/lava
- It will not defend itself yet

### Movement

Try "come" to make the bot come to the player

### Building

Still early, but if you add a blueprint to bulueprint_list.py, the bot can build it. Starting point is a chest with a torch. The bot can build a full sorting system with "build sorter".
