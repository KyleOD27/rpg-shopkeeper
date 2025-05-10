from app.conversation import PlayerIntent
SHOP_ACTIONS = [{'intent': PlayerIntent.BUY_ITEM, 'label': 'Buy',
    'description': 'Purchase an item from the shop.'}, {'intent':
    PlayerIntent.SELL_ITEM, 'label': 'Sell', 'description':
    'Sell an item from your inventory.'}, {'intent': PlayerIntent.
    DEPOSIT_GOLD, 'label': 'Deposit Gold', 'description':
    'Add gold to your party stash.'}, {'intent': PlayerIntent.WITHDRAW_GOLD,
    'label': 'Withdraw Gold', 'description':
    'Take gold out of your party stash.'}, {'intent': PlayerIntent.HAGGLE,
    'label': 'Haggle', 'description': 'Try to negotiate a better price.'}]
QUERY_ACTIONS = [{'intent': PlayerIntent.CHECK_BALANCE, 'label':
    'Check Balance', 'description':
    'See how much gold your party currently holds.'}, {'intent':
    PlayerIntent.VIEW_ITEMS, 'label': 'View Items', 'description':
    'Look at the list of items available in the shop.'}, {'intent':
    PlayerIntent.VIEW_LEDGER, 'label': 'View Ledger', 'description':
    'View your recent transactions.'}]
CONVERSE_ACTIONS = [{'intent': PlayerIntent.BARTER, 'label': 'Haggle',
    'description': 'Try to negotiate a better price.'}]


def get_action_menu():
    return SHOP_ACTIONS + QUERY_ACTIONS + CONVERSE_ACTIONS
