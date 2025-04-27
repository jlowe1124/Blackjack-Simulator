# Blackjack Strategy Simulator

A Monte Carlo simulation tool for analyzing blackjack strategies, including:
- Basic strategy implementation
- Hi-Lo card counting system
- Optimal bet sizing
- Side bet analysis (Perfect 20 and Dealer Bust)

## Features

- **Basic Strategy**: Complete implementation including:
  - Hard totals
  - Soft totals (A,2 through A,9)
  - Pair splitting
  - Double down opportunities
  - Late surrender
- **Card Counting**: Hi-Lo system with true count calculation
- **Bet Sizing**: Dynamic bet sizing based on true count
- **Side Bets**: Optional analysis of:
  - Perfect 20 (4:1 payout)
  - Dealer Bust (variable payouts by upcard)
- **Statistics**: Detailed analysis including:
  - Win/loss/push rates
  - House edge
  - Expected value per hand
  - Hourly rate projections
  - Standard deviation and variance ranges

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/blackjack-calculator.git

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Run basic simulation with default settings
python main.py

# Run with custom bet sizes
python main.py --min-bet 25 --max-bet 1000
```

## Configuration

The simulation can be configured through the `BlackjackRules` class in `rules.py`, including:
- Number of decks (default: 8)
- Dealer hit/stand on soft 17 (default: hit)
- Double after split (default: allowed)
- Split rules (default: up to 3 splits, no resplit aces)
- Side bet options and payouts
- Betting limits (default: $10-$400)

## Sample Output

```
Blackjack Simulation Results:
Total Hands: 1000000
Wins: 43.5%
Losses: 48.7%
Pushes: 7.8%
Blackjacks: 4.5%

Betting Statistics:
Minimum Bet: $10.00
Average Bet: $23.10
Maximum Bet: $400.00

Hourly Statistics (at 100 hands/hour):
Expected Value: $8.62/hour
Standard Deviation: $413.86/hour
68% of hours between: $-405.24 to $422.48
95% of hours between: $-819.10 to $836.33
```

## License

MIT License

## Disclaimer

This tool is for educational and entertainment purposes only. Card counting may be restricted or prohibited in some jurisdictions. Always check and comply with local laws and casino regulations.
