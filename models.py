"""
Core classes for blackjack simulation.
"""
from typing import List


class Card:
    RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    SUITS = ['♠', '♣', '♥', '♦']
    
    def __init__(self, rank: str, suit: str):
        self.rank = rank
        self.suit = suit
    
    def value(self) -> int:
        if self.rank == 'A':
            return 11
        elif self.rank in ['K', 'Q', 'J']:
            return 10
        return int(self.rank)
    
    def __str__(self):
        return f"{self.rank}{self.suit}"


class Hand:
    def __init__(self):
        self.cards: List[Card] = []
        self.bet: float = 1.0
    
    def add_card(self, card: Card):
        self.cards.append(card)
    
    def value(self) -> int:
        value = 0
        aces = 0
        
        # First count non-aces
        for card in self.cards:
            if card.rank == 'A':
                aces += 1
            else:
                value += card.value()
        
        # Then add aces optimally
        for _ in range(aces):
            if value + 11 <= 21:
                value += 11
            else:
                value += 1
        
        return value
    
    def is_soft(self) -> bool:
        """Returns True if the hand contains an ace counted as 11."""
        value = 0
        aces = 0
        
        # First count non-aces
        for card in self.cards:
            if card.rank == 'A':
                aces += 1
            else:
                value += card.value()
        
        # Then check if we can use an ace as 11
        return aces > 0 and (value + 11 <= 21)
    
    def is_blackjack(self) -> bool:
        return len(self.cards) == 2 and self.value() == 21
    
    def is_bust(self) -> bool:
        return self.value() > 21
    
    def __str__(self):
        return " ".join(str(card) for card in self.cards)


class Deck:
    def __init__(self, num_decks: int = 1):
        self.cards: List[Card] = []
        self.build_deck(num_decks)
        self.shuffle()
    
    def build_deck(self, num_decks: int):
        self.cards = []
        for _ in range(num_decks):
            for rank in Card.RANKS:
                for suit in Card.SUITS:
                    self.cards.append(Card(rank, suit))
    
    def shuffle(self):
        import random
        random.shuffle(self.cards)
    
    def deal(self) -> Card:
        return self.cards.pop()
    
    def cards_remaining(self) -> int:
        return len(self.cards)
