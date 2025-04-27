"""
Visualize basic strategy for blackjack.
"""
import numpy as np
import matplotlib.pyplot as plt
from rules import BlackjackRules, get_basic_strategy_move
from models import Card, Hand

def create_basic_strategy_charts():
    """Create and display basic strategy charts."""
    rules = BlackjackRules()
    
    # Create figure with 3 subplots
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(20, 8))
    fig.suptitle('Basic Strategy Charts', fontsize=16)
    
    # Color mapping for actions
    colors = {
        'H': [1.0, 0.8, 0.8],  # Light red for Hit
        'S': [0.8, 1.0, 0.8],  # Light green for Stand
        'D': [0.8, 0.9, 1.0],  # Light blue for Double
        'P': [1.0, 1.0, 0.8],  # Light yellow for Split
        'R': [0.9, 0.8, 1.0]   # Light purple for Surrender
    }
    
    # Hard totals chart
    hard_data = np.full((10, 10), 'H', dtype='U1')  # 17 down to 8 vs dealer 2-A
    for i, total in enumerate(range(17, 7, -1)):
        for j, dealer in enumerate(['2', '3', '4', '5', '6', '7', '8', '9', '10', 'A']):
            hand = Hand()
            # Create a hand with the desired hard total
            if total >= 10:
                hand.add_card(Card('10', 'H'))
                hand.add_card(Card(str(total - 10), 'H'))
            else:
                hand.add_card(Card(str(total), 'H'))
            move = get_basic_strategy_move(hand, Card(dealer, 'H'), False, True, True)
            hard_data[i, j] = move
    
    # Soft totals chart
    soft_data = np.full((8, 10), 'H', dtype='U1')  # A,9 down to A,2 vs dealer 2-A
    for i, card in enumerate(range(2, 10)):
        for j, dealer in enumerate(['2', '3', '4', '5', '6', '7', '8', '9', '10', 'A']):
            hand = Hand()
            hand.cards = [Card('A', 'H'), Card(str(card), 'H')]
            print(f"Hand: A,{card} vs {dealer}, value={hand.value()}, soft={hand.is_soft()}")
            move = get_basic_strategy_move(hand, Card(dealer, 'H'), False, True, True)
            print(f"Move: {move}")
            soft_data[7-i, j] = move
    
    # Pairs chart
    pairs_data = np.full((10, 10), 'H', dtype='U1')  # A,A down to 2,2 vs dealer 2-A
    for i, card in enumerate(['A', 'K', '9', '8', '7', '6', '5', '4', '3', '2']):
        for j, dealer in enumerate(['2', '3', '4', '5', '6', '7', '8', '9', '10', 'A']):
            hand = Hand()
            hand.cards = [Card(card, 'H'), Card(card, 'H')]
            move = get_basic_strategy_move(hand, Card(dealer, 'H'), True, True, True)
            pairs_data[i, j] = move
    
    # Convert data to RGB arrays
    def data_to_rgb(data):
        rgb_data = np.zeros((data.shape[0], data.shape[1], 3))
        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                rgb_data[i, j] = colors[data[i, j]]
        return rgb_data
    
    # Plot hard totals
    ax1.imshow(data_to_rgb(hard_data))
    ax1.set_title('Hard Totals')
    ax1.set_yticks(range(10))
    ax1.set_yticklabels(range(17, 7, -1))
    ax1.set_xticks(range(10))
    ax1.set_xticklabels(['2', '3', '4', '5', '6', '7', '8', '9', '10', 'A'])
    for i in range(10):
        for j in range(10):
            ax1.text(j, i, hard_data[i, j], ha='center', va='center')
    
    # Plot soft totals
    ax2.imshow(data_to_rgb(soft_data))
    ax2.set_title('Soft Totals')
    ax2.set_yticks(range(8))
    ax2.set_yticklabels([f'A,{x}' for x in range(9, 1, -1)])
    ax2.set_xticks(range(10))
    ax2.set_xticklabels(['2', '3', '4', '5', '6', '7', '8', '9', '10', 'A'])
    for i in range(8):
        for j in range(10):
            ax2.text(j, i, soft_data[i, j], ha='center', va='center')
    
    # Plot pairs
    ax3.imshow(data_to_rgb(pairs_data))
    ax3.set_title('Pairs')
    ax3.set_yticks(range(10))
    ax3.set_yticklabels(['A,A', '10,10', '9,9', '8,8', '7,7', '6,6', '5,5', '4,4', '3,3', '2,2'])
    ax3.set_xticks(range(10))
    ax3.set_xticklabels(['2', '3', '4', '5', '6', '7', '8', '9', '10', 'A'])
    for i in range(10):
        for j in range(10):
            ax3.text(j, i, pairs_data[i, j], ha='center', va='center')
    
    # Add legend
    legend_elements = [plt.Rectangle((0, 0), 1, 1, facecolor=color, label=action)
                      for action, color in zip(colors.keys(), [color for color in colors.values()])]
    fig.legend(handles=legend_elements, loc='center right')
    
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    create_basic_strategy_charts()
