"""
Command-line interface for blackjack simulator.
"""
from rules import BlackjackRules
from analyze import analyze_side_bet_strategy, print_analysis
import argparse


def run_sim(bet_size: float = 10.0):
    """Run blackjack simulation with specified parameters.
    
    Args:
        bet_size: Base bet size in dollars
    """
    rules = BlackjackRules(
        bet_size=bet_size,
        enable_perfect_20=False,
        enable_dealer_bust=False
    )
    
    analysis = analyze_side_bet_strategy(rules)
    print_analysis(rules, analysis)


if __name__ == "__main__":
    # Create rules first to get the default bet size
    rules = BlackjackRules()
    default_bet = rules.bet_size
    
    parser = argparse.ArgumentParser(description='Blackjack Monte Carlo Simulator')
    parser.add_argument('--min-bet', type=float, help=f'Minimum bet size (default: ${rules.min_bet:.2f})')
    parser.add_argument('--max-bet', type=float, help=f'Maximum bet size (default: ${rules.max_bet:.2f})')
    args = parser.parse_args()
    
    if args.min_bet:
        rules.min_bet = args.min_bet
        rules.bet_size = args.min_bet  # Set initial bet to minimum
    
    if args.max_bet:
        rules.max_bet = args.max_bet
        
    # Validate bet limits
    if rules.max_bet < rules.min_bet:
        print(f"Error: Maximum bet (${rules.max_bet:.2f}) cannot be less than minimum bet (${rules.min_bet:.2f})")
        exit(1)
    
    run_sim(bet_size=rules.min_bet)
