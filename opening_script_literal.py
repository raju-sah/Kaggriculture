OPENING_SCRIPT = [
    {'farmer': ['PASS'], 'hands': [], 'market': []},  # h0
    {'farmer': ['PASS'], 'hands': [], 'market': [['BUY_ANIMAL', 'COW', 1], ['BUY_PRODUCT', 'WHEAT', 5]]},  # h1
    {'farmer': ['PICKUP', 'COW', 1], 'hands': [], 'market': [['SELL', 'WHEAT', 1], ['HIRE'], ['HIRE'], ['HIRE'], ['HIRE'], ['BUY_ANIMAL', 'COW', 1], ['BUY_ANIMAL', 'SHEEP', 3]]},  # h2
    {'farmer': ['BUILD_PASTURE'], 'hands': [['PICKUP', 'SHEEP', 1], ['PASS'], ['PICKUP', 'COW', 1], ['PICKUP', 'SHEEP', 1]], 'market': [['SELL', 'WHEAT', 1]]},  # h3
    {'farmer': ['PLACE', 'COW', 1], 'hands': [['NORTH'], ['PICKUP', 'SHEEP', 1], ['NORTH'], ['WEST']], 'market': [['BUY_SEED', 'MELON', 2]]},  # h4
    {'farmer': ['PICKUP', 'WHEAT', 3], 'hands': [['WEST'], ['NORTH'], ['NORTH'], ['BUILD_PASTURE']], 'market': [['BUY_PRODUCT', 'WHEAT', 1]]},  # h5
    {'farmer': ['FEED'], 'hands': [['BUILD_PASTURE'], ['WEST'], ['NORTH'], ['PLACE', 'SHEEP', 1]], 'market': [['BUY_SEED', 'MELON', 2], ['BUY_PRODUCT', 'WHEAT', 1]]},  # h6
    {'farmer': ['CARE'], 'hands': [['PLACE', 'SHEEP', 1], ['WEST'], ['WEST'], ['WEST']], 'market': [['BUY_PRODUCT', 'WHEAT', 1]]},  # h7
    {'farmer': ['WEST'], 'hands': [['CARE'], ['BUILD_PASTURE'], ['BUILD_PASTURE'], ['WEST']], 'market': []},  # h8
    {'farmer': ['FEED'], 'hands': [['SOUTH'], ['PLACE', 'SHEEP', 1], ['PLACE', 'COW', 1], ['NORTH']], 'market': []},  # h9
    {'farmer': ['CARE'], 'hands': [['PICKUP', 'WHEAT', 1], ['WEST'], ['NORTH'], ['PLANT', 'MELON']], 'market': []},  # h10
    {'farmer': ['WEST'], 'hands': [['NORTH'], ['PLANT', 'MELON'], ['PLANT', 'MELON'], ['WATER']], 'market': []},  # h11
    {'farmer': ['FEED'], 'hands': [['FEED'], ['WATER'], ['WATER'], ['NORTH']], 'market': [['BUY_SEED', 'MELON', 2]]},  # h12
    {'farmer': ['CARE'], 'hands': [['NORTH'], ['WEST'], ['WEST'], ['PLANT', 'MELON']], 'market': [['BUY_SEED', 'WHEAT', 2]]},  # h13
    {'farmer': ['WEST'], 'hands': [['WEST'], ['PLANT', 'WHEAT'], ['PLANT', 'MELON'], ['WATER']], 'market': []},  # h14
    {'farmer': ['NORTH'], 'hands': [['PLANT', 'MELON'], ['WATER'], ['WATER'], ['NORTH']], 'market': [['SELL', 'WHEAT', 1], ['BUY_SEED', 'WHEAT', 1]]},  # h15
    {'farmer': ['WEST'], 'hands': [['WATER'], ['NORTH'], ['WEST'], ['PLANT', 'WHEAT']], 'market': [['BUY_SEED', 'WHEAT', 1]]},  # h16
    {'farmer': ['PLANT', 'WHEAT'], 'hands': [['WEST'], ['PLANT', 'WHEAT'], ['PASS'], ['WATER']], 'market': [['SELL', 'WHEAT', 1], ['BUY_SEED', 'WHEAT', 1]]},  # h17
    {'farmer': ['WATER'], 'hands': [['PLANT', 'WHEAT'], ['WATER'], ['PLANT', 'WHEAT'], ['WEST']], 'market': [['BUY_SEED', 'WHEAT', 1]]},  # h18
    {'farmer': ['NORTH'], 'hands': [['WATER'], ['NORTH'], ['WATER'], ['PLANT', 'WHEAT']], 'market': [['BUY_SEED', 'WHEAT', 1]]},  # h19
    {'farmer': ['PLANT', 'WHEAT'], 'hands': [['WEST'], ['NORTH'], ['NORTH'], ['WATER']], 'market': [['BUY_SEED', 'WHEAT', 1]]},  # h20
    {'farmer': ['WATER'], 'hands': [['NORTH'], ['NORTH'], ['PLANT', 'WHEAT'], ['NORTH']], 'market': [['BUY_SEED', 'WHEAT', 1]]},  # h21
    {'farmer': ['NORTH'], 'hands': [['NORTH'], ['PLANT', 'WHEAT'], ['WATER'], ['PASS']], 'market': [['BUY_SEED', 'WHEAT', 1]]},  # h22
    {'farmer': ['NORTH'], 'hands': [['PLANT', 'WHEAT'], ['WATER'], ['PASS'], ['WATER']], 'market': []},  # h23
]
