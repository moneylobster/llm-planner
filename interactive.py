import agentclass
from house1 import *

goal=input("Goal:")

agent=agentclass.ZeroShotPlanner(house, goal)
agent.start()
