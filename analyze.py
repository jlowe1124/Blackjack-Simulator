"""
Analysis tools for blackjack simulation strategies.
"""
from typing import Dict, List, Tuple
from rules import BlackjackRules
from simulator import BlackjackSimulator


def analyze_side_bet_strategy(
    rules: BlackjackRules,
    rounds: int = 1000000,
    min_count: int = 1,
    max_count: int = 20,
    hands_per_hour: int = 100
) -> Dict:
    """Analyze side bet strategy effectiveness across different count thresholds."""
    simulator = BlackjackSimulator(rules)
    stats = simulator.simulate(num_rounds=rounds, bet_unit=rules.bet_size)
    
    # Format count frequencies
    count_freqs = []
    total_hands = stats['hands_played']
    for count in range(min_count, max_count + 1):
        freq = stats['count_frequencies'].get(count, 0)
        pct = freq / total_hands
        count_freqs.append((count, freq, pct))
    
    # Format strategy analysis
    strategies = []
    for threshold in range(min_count, max_count + 1):
        stats_t = stats['side_bet_stats'].get(threshold, {})
        bets_made = stats_t.get('made', 0)
        if bets_made > 0:
            wins = stats_t.get('won', 0)
            win_rate = wins / bets_made
            profit = stats_t.get('profit', 0)
            ev_per_hand = profit / total_hands
            hourly_ev = ev_per_hand * hands_per_hour
            strategies.append((threshold, bets_made, win_rate, ev_per_hand, hourly_ev))
    
    # Format main game stats
    main_stats = {
        'hands': total_hands,
        'wins': stats['wins'],
        'losses': stats['losses'],
        'pushes': stats['pushes'],
        'blackjacks': stats['blackjacks'],
        'win_rate': stats['win_rate'],
        'house_edge': stats['house_edge'],
        'ev_per_hand': stats['ev_per_hand'],
        'std_dev': stats['std_dev'],
        'avg_bet': stats['avg_bet'],
        'min_bet': stats['min_bet'],
        'max_bet': stats['max_bet']
    }
    
    main_stats['dealer_bust_stats'] = stats['dealer_bust_stats']
    return {
        'main_stats': main_stats,
        'count_frequencies': count_freqs,
        'strategies': strategies
    }


def print_analysis(rules: BlackjackRules, analysis: Dict):
    """Print formatted analysis results."""
    stats = analysis['main_stats']
    
    print("Blackjack Monte Carlo EV Simulator")
    print(rules)
    print(f"\nMain bet size: ${rules.bet_size:.2f}")
    print(f"Perfect 20 side bet: ${rules.perfect_20_side_bet:.2f} (pays {rules.perfect_20_payout}:1)")
    print(f"Dealer bust side bet: ${rules.dealer_bust_bet:.2f} (varies by upcard)")
    
    print("\nBlackjack Simulation Results:")
    print(f"Total Hands: {stats['hands']}")
    print(f"Wins: {stats['wins']} ({stats['win_rate']:.1%})")
    print(f"Losses: {stats['losses']} ({stats['losses']/stats['hands']:.1%})")
    print(f"Pushes: {stats['pushes']} ({stats['pushes']/stats['hands']:.1%})")
    print(f"Blackjacks: {stats['blackjacks']} ({stats['blackjacks']/stats['hands']:.1%})")
    
    print("\nBetting Statistics:")
    print(f"Minimum Bet: ${stats['min_bet']:.2f}")
    print(f"Average Bet: ${stats['avg_bet']:.2f}")
    print(f"Maximum Bet: ${stats['max_bet']:.2f}")
    
    print(f"House Edge: {-stats['house_edge']:.2%}")
    print(f"EV per Hand: ${stats['ev_per_hand']:.2f}")
    print(f"Std Dev: ${stats['std_dev']:.2f}")
    
    # Calculate hourly stats (assuming 100 hands per hour)
    hands_per_hour = 100
    hourly_ev = stats['ev_per_hand'] * hands_per_hour
    hourly_std = stats['std_dev'] * (hands_per_hour ** 0.5)
    
    print(f"\nHourly Statistics (at {hands_per_hour} hands/hour):")
    print(f"Expected Value: ${hourly_ev:.2f}/hour")
    print(f"Standard Deviation: ${hourly_std:.2f}/hour")
    print(f"68% of hours between: ${hourly_ev - hourly_std:.2f} to ${hourly_ev + hourly_std:.2f}")
    print(f"95% of hours between: ${hourly_ev - 2*hourly_std:.2f} to ${hourly_ev + 2*hourly_std:.2f}")
    
    if rules.enable_perfect_20:
        print("\nPerfect 20 Side Bet Analysis:")
        print("Count Frequencies:")
        for count, freq, pct in analysis['count_frequencies']:
            print(f"  Count {count:+d}: {freq:6d} hands ({pct:6.1%})")
        
        print("\nPerfect 20 Strategy by Count Threshold:")
        print("Thresh  Bets Made   Win Rate    EV/Hand   Hourly EV*")
        print("-" * 50)
        
        for thresh, bets, win_rate, ev, hourly_ev in analysis['strategies']:
            print(f"{thresh:4d}   {bets:6d}   {win_rate:6.1%}   ${ev:7.2f}  ${hourly_ev:8.2f}")
        
        print("\n* Hourly EV assumes 100 hands per hour")
    
    # Dealer Bust Side Bet Analysis
    if rules.enable_dealer_bust:
        print("\nDealer Bust Side Bet Analysis:")
        print("By Dealer Upcard:")
        print("Card   Hands    Bust%   Win Rate   EV/Hand   Hourly EV*")
        print("-" * 55)
        
        dealer_stats = analysis['main_stats']['dealer_bust_stats']['by_upcard']
        for card in range(2, 12):
            hands = dealer_stats[card]['hands']
            if hands > 0:
                busts = dealer_stats[card]['busts']
                bets = dealer_stats[card]['bets']
                profit = dealer_stats[card]['profit']
                
                bust_rate = busts / hands if hands > 0 else 0  # Same as win rate since we bet every hand
                ev_per_hand = profit / stats['hands']
                hourly_ev = ev_per_hand * 100
                
                card_name = 'A' if card == 11 else str(card)
                print(f"{card_name:4s}   {hands:6d}   {bust_rate:6.1%}   {bust_rate:6.1%}   ${ev_per_hand:7.2f}  ${hourly_ev:8.2f}")
        
        print("\nBy Count:")
        print("Count  Hands    Bust%   Win Rate   EV/Hand   Hourly EV*")
        print("-" * 55)
        
        count_stats = analysis['main_stats']['dealer_bust_stats']['by_count']
        for count in range(1, 16):
            hands = count_stats[count]['hands']
            if hands > 0:
                busts = count_stats[count]['busts']
                bets = count_stats[count]['bets']
                profit = count_stats[count]['profit']
                
                bust_rate = busts / hands if hands > 0 else 0  # Same as win rate since we bet every hand
                ev_per_hand = profit / stats['hands']
                hourly_ev = ev_per_hand * 100
                
                print(f"{count:+4d}   {hands:6d}   {bust_rate:6.1%}   {bust_rate:6.1%}   ${ev_per_hand:7.2f}  ${hourly_ev:8.2f}")
