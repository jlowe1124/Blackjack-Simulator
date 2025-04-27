"""
Blackjack simulation engine.
"""
import statistics
from typing import Dict, Tuple

from models import Card, Hand, Deck
from rules import BlackjackRules, get_basic_strategy_move, hilo_count


class BlackjackSimulator:
    def __init__(self, rules: BlackjackRules = None):
        self.rules = rules or BlackjackRules()
        self.shoe = Deck(self.rules.deck_count)
        self.running_count = 0
        self.true_count = 0
        self.cards_used = 0
        
    def draw_card(self) -> Card:
        """Draw a card from the shoe, reshuffling if needed."""
        # Reshuffle if needed
        if self.shoe.cards_remaining() <= self.rules.min_cards_before_shuffle:
            self.shoe = Deck(self.rules.deck_count)
            self.running_count = 0
            self.cards_used = 0
            self.true_count = 0
            return self.shoe.deal()
        
        # Draw and update count
        card = self.shoe.deal()
        self.running_count += hilo_count(card)
        self.cards_used += 1
        
        # Calculate true count (running count per deck remaining)
        cards_remaining = self.shoe.cards_remaining()
        if cards_remaining > 0:
            decks_remaining = cards_remaining / 52
            self.true_count = round(self.running_count / decks_remaining, 1)
        
        return card
    
    def get_bet_size(self, min_bet: float) -> float:
        """Calculate bet size based on Hi-Lo count, respecting table limits."""
        # Calculate bet based on count
        # Use a more aggressive betting ramp: bet = min_bet * (true_count + 1)
        # This means we bet:
        # Count -1 or less: minimum bet
        # Count 0: 1x
        # Count +1: 2x
        # Count +2: 3x
        # etc.
        bet = min_bet * max(1, self.true_count + 1)
        
        # Enforce table limits
        bet = max(self.rules.min_bet, min(bet, self.rules.max_bet))
        return bet
    
    def play_round(self, min_bet: float = 1.0) -> Tuple[float, int, int, bool]:
        """Play one round of blackjack, returns (profit, cards_used, count_delta, is_blackjack)."""
        # Calculate bet based on count
        bet = self.get_bet_size(min_bet)
        
        # Deal initial hands
        player_hand = Hand()
        dealer_hand = Hand()
        cards_used = 0
        count_delta = 0
        
        # Deal initial cards
        for _ in range(2):
            c = self.draw_card()
            player_hand.add_card(c)
            count_delta += hilo_count(c)
            cards_used += 1
            
            c = self.draw_card()
            dealer_hand.add_card(c)
            count_delta += hilo_count(c)
            cards_used += 1
        
        # Check Perfect 20 side bet - only make it when true count is high (lots of 10s)
        side_bet_profit = 0
        side_bet_won = False
        make_side_bet = self.true_count >= 3 and self.rules.enable_perfect_20  # Only bet when count is very favorable and enabled
        
        if make_side_bet:
            if player_hand.value() == 20 and len(player_hand.cards) == 2:
                side_bet_profit = self.rules.perfect_20_side_bet * self.rules.perfect_20_payout
                side_bet_won = True
            side_bet_profit -= self.rules.perfect_20_side_bet  # Lose the side bet stake
        
        # Check for blackjack
        player_blackjack = player_hand.is_blackjack()
        dealer_blackjack = dealer_hand.is_blackjack()
        
        if player_blackjack or dealer_blackjack:
            if player_blackjack and dealer_blackjack:
                return 0, cards_used, count_delta, False  # Push
            elif player_blackjack:
                return bet * self.rules.blackjack_payout, cards_used, count_delta, True
            else:  # dealer_blackjack
                return -bet, cards_used, count_delta, False
        
        # Check if we can split
        can_split = len(player_hand.cards) == 2 and player_hand.cards[0].rank == player_hand.cards[1].rank
        dealer_total = dealer_hand.value()
        
        # Player action
        def play_hand(hand: Hand, current_bet: float, can_split: bool, split_aces: bool = False) -> float:
            nonlocal dealer_total
            nonlocal cards_used, count_delta
            
            # Draw a card if this is a split hand
            if len(hand.cards) == 1:
                c = self.draw_card()
                hand.add_card(c)
                cards_used += 1
                count_delta += hilo_count(c)
                
                # If we split aces, only get one card and no blackjacks
                if split_aces:
                    if hand.value() > 21:
                        return -current_bet  # Bust
                    return hand.value()  # Return value for comparison
            
            while True:
                # Can only double on first two cards, and after split if allowed
                can_double = len(hand.cards) == 2 and (not split_aces or self.rules.double_after_split)
                action = get_basic_strategy_move(hand, dealer_hand.cards[0], can_split, can_double, self.rules.late_surrender)
                
                # Update can_double for should_double_down based on rules
                if action == 'D' and not can_double:
                    action = 'H'  # If we can't double, hit instead
                
                if action == 'S':
                    break
                elif action == 'H':
                    c = self.draw_card()
                    hand.add_card(c)
                    cards_used += 1
                    count_delta += hilo_count(c)
                    if hand.is_bust():
                        return -current_bet  # Bust
                elif action == 'D' and len(hand.cards) == 2:  # Can only double on first two cards
                    c = self.draw_card()
                    hand.add_card(c)
                    cards_used += 1
                    count_delta += hilo_count(c)
                    current_bet *= 2  # Double the bet
                    if hand.is_bust():
                        return -current_bet  # Bust
                    break  # Stand after doubling
                elif action == 'P' and can_split:
                    # Create two new hands
                    hand1 = Hand()
                    hand2 = Hand()
                    hand1.add_card(hand.cards[0])
                    hand2.add_card(hand.cards[1])
                    
                    # Split aces get only one card unless hit_after_split_aces is True
                    is_aces = hand.cards[0].rank == 'A'
                    
                    # Play each hand (no resplitting allowed)
                    result1 = play_hand(hand1, current_bet, False, split_aces=is_aces and not self.rules.hit_after_split_aces)
                    result2 = play_hand(hand2, current_bet, False, split_aces=is_aces and not self.rules.hit_after_split_aces)
                    
                    # For split hands, we need to play against dealer for each non-busted hand
                    dealer_total = dealer_hand.value()
                    dealer_played = False
                    
                    # Compare each hand with dealer
                    total_result = 0
                    for result in [result1, result2]:
                        if isinstance(result, (int, float)) and result >= 0:  # Not bust
                            # Play dealer if we haven't yet
                            if not dealer_played:
                                while dealer_total < 17 or (dealer_total == 17 and self.rules.dealer_hit_soft_17 and dealer_hand.is_soft()):
                                    c = self.draw_card()
                                    dealer_hand.add_card(c)
                                    cards_used += 1
                                    count_delta += hilo_count(c)
                                    dealer_total = dealer_hand.value()
                                dealer_played = True
                            
                            if dealer_total > 21:  # Dealer busts
                                total_result += current_bet
                            else:
                                if result > dealer_total:
                                    total_result += current_bet
                                elif result < dealer_total:
                                    total_result -= current_bet
                                # Push is a wash, no change to total_result
                        elif result == -2:  # Surrender
                            total_result -= current_bet/2
                        else:  # Bust
                            total_result -= current_bet
                    
                    return total_result
                elif action == 'R' and self.rules.late_surrender:
                    return -2  # Surrender (-2 is special code for surrender)
                else:
                    break
            
            # Return result based on hand value
            if hand.is_bust():
                return -current_bet
            elif hand.is_blackjack() and len(hand.cards) == 2:  # Only original dealt blackjacks count
                return current_bet * self.rules.blackjack_payout
            elif split_aces:  # For split aces, return value for comparison
                return hand.value()
            return hand.value()  # Return value for comparison with dealer
        
        # Play the initial hand
        player_result = play_hand(player_hand, bet, can_split)
        
        # If player hasn't busted or surrendered, dealer plays
        if isinstance(player_result, (int, float)) and player_result >= 0:  # Not bust or surrender
            # Dealer draws until hard 17 or soft 17+ (if not hitting soft 17)
            while True:
                dealer_total = dealer_hand.value()
                if dealer_total > 21:
                    break  # Dealer busts
                if dealer_total >= 17:
                    if not dealer_hand.is_soft() or not self.rules.dealer_hit_soft_17:
                        break  # Stand on hard 17+ or soft 17+ if not hitting soft 17
                
                # Draw a card
                c = self.draw_card()
                dealer_hand.add_card(c)
                cards_used += 1
                count_delta += hilo_count(c)
            
            # Compare hands
            if dealer_total > 21:  # Dealer busts
                result = bet
            else:
                if player_result > dealer_total:
                    result = bet
                elif player_result < dealer_total:
                    result = -bet
                else:
                    result = 0  # Push
        elif player_result == -2:  # Surrender
            result = -bet/2
        else:  # Already have result (bust or split hands)
            result = player_result
        
        # Return total profit (main bet + side bet) and stats
        return result + side_bet_profit, cards_used, count_delta, player_blackjack
    
    def simulate(self, num_rounds: int = 1000, bet_unit: float = 1.0) -> Dict:
        """Run Monte Carlo simulation for specified number of rounds."""
        profits = []
        bets = []
        wins = 0
        losses = 0
        pushes = 0
        blackjacks = 0
        
        # Track side bets by count threshold
        side_bet_stats = {i: {'made': 0, 'won': 0, 'profit': 0} for i in range(1, 16)}
        count_frequencies = {i: 0 for i in range(1, 16)}
        
        # Track dealer bust side bet stats
        dealer_bust_stats = {
            'by_upcard': {i: {'hands': 0, 'busts': 0, 'bets': 0, 'profit': 0} for i in range(2, 12)},
            'by_count': {i: {'hands': 0, 'busts': 0, 'bets': 0, 'profit': 0} for i in range(1, 16)}
        }
        
        for _ in range(num_rounds):
            # Get bet size before playing round (based on current count)
            bet = self.get_bet_size(bet_unit)
            bets.append(bet)
            
            # Deal initial cards
            player_hand = Hand()
            dealer_hand = Hand()
            
            # Deal first round of cards
            player_hand.add_card(self.draw_card())
            dealer_up_card = self.draw_card()
            dealer_hand.add_card(dealer_up_card)
            
            # Deal second round
            player_hand.add_card(self.draw_card())
            dealer_hand.add_card(self.draw_card())
            
            # Track side bet opportunities by count
            true_count = round(self.true_count)
            if 1 <= true_count <= 15:
                count_frequencies[true_count] += 1
                # Perfect 20 side bet
                if self.rules.enable_perfect_20:
                    for threshold in range(1, 16):
                        if true_count >= threshold:
                            side_bet_stats[threshold]['made'] += 1
                            if player_hand.value() == 20 and len(player_hand.cards) == 2:
                                side_bet_stats[threshold]['won'] += 1
                                side_bet_stats[threshold]['profit'] += self.rules.perfect_20_side_bet * self.rules.perfect_20_payout
                            side_bet_stats[threshold]['profit'] -= self.rules.perfect_20_side_bet
                
                # Dealer bust side bet
                dealer_value = dealer_up_card.value()
                if dealer_value > 10: dealer_value = 11  # Ace
                dealer_bust_stats['by_upcard'][dealer_value]['hands'] += 1
                dealer_bust_stats['by_count'][true_count]['hands'] += 1
                
                # Play dealer hand once and store result
                dealer_final_hand = Hand()
                for card in dealer_hand.cards:
                    dealer_final_hand.add_card(card)
                
                while dealer_final_hand.value() < 17 or (dealer_final_hand.value() == 17 and dealer_final_hand.is_soft() and self.rules.dealer_hit_soft_17):
                    dealer_final_hand.add_card(self.draw_card())
                
                # Track dealer bust side bet results
                if dealer_final_hand.value() > 21:
                    dealer_bust_stats['by_upcard'][dealer_value]['busts'] += 1
                    dealer_bust_stats['by_count'][true_count]['busts'] += 1
                    
                    # Calculate profit if we had bet
                    payout = self.rules.dealer_bust_payouts[dealer_value]
                    dealer_bust_stats['by_upcard'][dealer_value]['profit'] += self.rules.dealer_bust_bet * payout
                    dealer_bust_stats['by_count'][true_count]['profit'] += self.rules.dealer_bust_bet * payout
                
                dealer_bust_stats['by_upcard'][dealer_value]['profit'] -= self.rules.dealer_bust_bet
                dealer_bust_stats['by_count'][true_count]['profit'] -= self.rules.dealer_bust_bet
                dealer_bust_stats['by_upcard'][dealer_value]['bets'] += 1
                dealer_bust_stats['by_count'][true_count]['bets'] += 1
                
                # Use the same dealer final hand for main game
                dealer_hand = dealer_final_hand
            
            # Now play the actual round
            profit, _, _, is_blackjack = self.play_round(bet_unit)
            profits.append(profit)
            
            if is_blackjack:
                blackjacks += 1
                wins += 1
            elif profit > 0:
                wins += 1
            elif profit < 0:
                losses += 1
            else:
                pushes += 1
        
        # Calculate statistics
        total_wagered = sum(bets)
        total_profit = sum(profits)
        
        return {
            'hands_played': num_rounds,
            'wins': wins,
            'losses': losses,
            'pushes': pushes,
            'blackjacks': blackjacks,
            'win_rate': wins / num_rounds,
            'house_edge': -total_profit / total_wagered,
            'ev_per_hand': total_profit / num_rounds,
            'std_dev': statistics.stdev(profits),
            'avg_bet': sum(bets) / num_rounds,
            'max_bet': max(bets),
            'min_bet': min(bets),
            'side_bet_stats': side_bet_stats,
            'count_frequencies': count_frequencies,
            'dealer_bust_stats': dealer_bust_stats
        }
