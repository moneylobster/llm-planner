import agentclass
from house1 import *

agent=agentclass.ZeroShotPlanner(house, "")

## Moving objects
agent=agentclass.ZeroShotPlanner(house, "Take the remote to the bathroom")
agent.start()
assert "TV remote" in bathroom.items

agent=agentclass.ZeroShotPlanner(house, "Take the Sprite to the living room")
agent.start()
assert "Sprite" in livingroom.items
