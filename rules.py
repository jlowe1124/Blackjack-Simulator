"""
Game rules and basic strategy for blackjack.
"""
from dataclasses import dataclass
from models import Card, Hand


@dataclass
class BlackjackRules:
    """Configuration for blackjack game rules."""
    # Core game rules
    blackjack_payout: float = 1.5
    dealer_hit_soft_17: bool = True
    deck_count: int = 8
    min_cards_before_shuffle: int = 0
    double_after_split: bool = True
    resplit_allowed: bool = False
    hit_after_split_aces: bool = False  # If False, only one card allowed after splitting aces
    max_splits: int = 3
    double_min_value: int = 0
    late_surrender: bool = True
    
    # Betting rules
    min_bet: float = 10.0  # Minimum bet size in dollars
    max_bet: float = 400.0  # Maximum bet size in dollars
    bet_size: float = 10.0  # Current bet size in dollars
    
    # Side bet configuration
    enable_perfect_20: bool = False  # Whether to enable Perfect 20 side bet
    perfect_20_side_bet: float = 5.0  # Side bet amount for Perfect 20 (4:1 payout)
    perfect_20_payout: float = 4.0  # Payout ratio for Perfect 20 side bet
    
    # Dealer bust side bet configuration
    enable_dealer_bust: bool = False  # Whether to enable dealer bust side bet
    dealer_bust_bet: float = 5.0  # Side bet amount for dealer bust
    # Dealer bust payouts based on dealer's upcard
    # Key is the dealer's upcard value (2-10 for number cards, 11 for Ace)
    # Value is the payout ratio (e.g., 1.0 means 1:1 payout)
    dealer_bust_payouts = {
        2: 1.0,  # 1:1 payout for dealer 2-6
        3: 1.0,
        4: 1.0,
        5: 1.0,
        6: 1.0,
        7: 2.0,  # 2:1 payout for dealer 7
        8: 2.5,  # 2.5:1 payout for dealer 8
        9: 3.0,  # 3:1 payout for dealer 9
        10: 3.5, # 3.5:1 payout for dealer 10/J/Q/K
        11: 4.0  # 4:1 payout for dealer A
    }


def should_double_down(player_value: int, dealer_value: int, is_soft: bool, num_cards: int, can_double: bool = True) -> bool:
    """Determine if the player should double down based on basic strategy."""
    if not can_double or num_cards != 2:
        return False

    # Only handle hard totals here, soft totals are handled in get_basic_strategy_move
    if not is_soft:
        if player_value == 11:
            return True
        elif player_value == 10:
            return dealer_value <= 9
        elif player_value == 9:
            return 3 <= dealer_value <= 6

    return False


def get_basic_strategy_move(player_hand: Hand, dealer_upcard: Card, can_split: bool, can_double: bool, can_surrender: bool) -> str:
    """Implements basic strategy for blackjack.
    Returns: 'H' (hit), 'S' (stand), 'D' (double), 'P' (split), 'R' (surrender)
    """
    player_value = player_hand.value()
    dealer_value = 11 if dealer_upcard.rank == 'A' else int(dealer_upcard.rank) if dealer_upcard.rank.isdigit() else 10
    is_soft = player_hand.is_soft()
    
    # Check surrender first (only on first two cards)
    if can_surrender and len(player_hand.cards) == 2 and not is_soft:
        # Hard 16 (except pair of 8s) vs 9-A
        if player_value == 16:
            if dealer_value >= 9 and not (can_split and player_hand.cards[0].rank == '8'):
                return 'R'
        # Hard 15 vs 10 or A
        elif player_value == 15 and dealer_value == 10:
            return 'R'
    
    # Check for pair splitting
    if can_split and len(player_hand.cards) == 2 and player_hand.cards[0].rank == player_hand.cards[1].rank:
        rank = player_hand.cards[0].rank
        
        # Always split aces and 8s
        if rank == 'A' or rank == '8':
            return 'P'
        # Never split 5s and 10s
        elif rank == '5' or rank in ['10', 'J', 'Q', 'K']:
            pass  # Continue to normal strategy
        # Split 2s, 3s against dealer 2-7
        elif rank in ['2', '3'] and dealer_value <= 7:
            return 'P'
        # Split 4s against dealer 5-6
        elif rank == '4' and 5 <= dealer_value <= 6:
            return 'P'
        # Split 6s against dealer 2-6
        elif rank == '6' and dealer_value <= 6:
            return 'P'
        # Split 7s against dealer 2-7
        elif rank == '7' and dealer_value <= 7:
            return 'P'
        # Split 9s against dealer 2-6,8-9
        elif rank == '9' and ((dealer_value <= 6) or dealer_value == 8 or dealer_value == 9):
            return 'P'
    
    # Check for doubling opportunities - only for hard totals
    if not is_soft and can_double and should_double_down(player_value, dealer_value, is_soft, len(player_hand.cards)):
        return 'D'
    
    # Check soft totals (hands with aces counted as 11)
    if is_soft:
        if player_value >= 20:  # A,9 or better
            return 'S'
        elif player_value == 19:  # A,8
            return 'S'  # Stand against all
        elif player_value == 18:  # A,7
            if dealer_value >= 9:
                return 'H'  # Hit against 9-A
            elif 3 <= dealer_value <= 6:
                return 'D' if can_double else 'H'  # Double against 3-6, hit if can't double
            return 'S'  # Stand against 2, 7-8
        elif player_value == 17:  # A,6
            if 3 <= dealer_value <= 6:
                return 'D' if can_double else 'H'  # Double against 3-6, hit if can't double
            return 'H'  # Hit against all else
        elif player_value == 16:  # A,5
            if 4 <= dealer_value <= 6:
                return 'D' if can_double else 'H'  # Double against 4-6, hit if can't double
            return 'H'  # Hit against all else
        elif player_value == 15:  # A,4
            if 4 <= dealer_value <= 6:
                return 'D' if can_double else 'H'  # Double against 4-6, hit if can't double
            return 'H'  # Hit against all else
        elif player_value == 14:  # A,3
            if 5 <= dealer_value <= 6:
                return 'D' if can_double else 'H'  # Double against 5-6, hit if can't double
            return 'H'  # Hit against all else
        elif player_value == 13:  # A,2
            if 5 <= dealer_value <= 6:
                return 'D' if can_double else 'H'  # Double against 5-6, hit if can't double
            return 'H'  # Hit against all else
        return 'H'  # Hit on soft 12
    
    # Hard totals
    if player_value >= 17:
        return 'S'  # Always stand on 17+
    elif player_value >= 13:
        return 'S' if dealer_value <= 6 else 'H'  # Stand vs 2-6, hit vs 7-A
    elif player_value == 12:
        return 'S' if 4 <= dealer_value <= 6 else 'H'  # Stand vs 4-6, hit vs 2-3,7-A
    elif player_value == 11:
        return 'D' if can_double else 'H'  # Always double 11, hit if can't double
    elif player_value == 10:
        return 'D' if can_double and dealer_value <= 9 else 'H'  # Double vs 2-9
    elif player_value == 9:
        return 'D' if can_double and 3 <= dealer_value <= 6 else 'H'  # Double vs 3-6
    elif player_value <= 8:
        return 'H'  # Always hit 8 or less
    
    # If nothing else matches, use basic hitting strategy
    return 'H'  # Hit on all other cases


def hilo_count(card) -> int:
    """Calculate Hi-Lo count contribution for a card."""
    rank = card if isinstance(card, str) else card.rank
    if rank in ['2', '3', '4', '5', '6']:
        return 1
    elif rank in ['10', 'J', 'Q', 'K', 'A']:
        return -1
    return 0
