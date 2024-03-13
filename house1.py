import houseclass

kitchen=houseclass.Room("kitchen", [
    "sponge",
    "spoon",
    "fork",
    "knife",
    "spatula",
    "dinner plate",
    "lettuce",
    "carrot",
    "apple",
    "tomato",
    "potato chips",
    "Pepsi",
    "Sprite",
    "bottled water",
    "dish detergent",
    ])

bathroom=houseclass.Room("bathroom", [
    "broom",
    "soap",
    "toilet paper",
    "bucket",
    ])

livingroom=houseclass.Room("livingroom", [
    "chair",
    "stool",
    "TV remote",
    "deck of cards",
    ])

house=houseclass.House([livingroom, bathroom, kitchen])
