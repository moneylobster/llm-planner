def visualize(agent):
    loc=agent.location.name
    print("------------------------")
    print(f"Hand: {agent.hand}")
    for room in agent.house.rooms:
        prefix= "[*]" if room.name==loc else "   "
        print(f"{prefix} {room.name} {room.items}")
    print("------------------------")
