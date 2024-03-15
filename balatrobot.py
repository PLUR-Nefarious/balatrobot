import praw
import re
import sys
import logging
import os
from urllib.parse import quote_plus

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client_id = os.environ['client_id']
client_secret = os.environ['client_secret']
username = os.environ['username']
password = os.environ['password']

# Dictionary of card names and their descriptions
card_info_dict = {
    "The Fool": "Creates a copy of the last Tarot or Planet card used during this run. Though it will not let you copy another copy of The Fool - that would be foolish",
    "The Magician": "Enhances 1 selected card into a Lucky card",
    "The High Priestess": "Creates 2 random Planet cards, or less if there is insufficient space",
    "The Empress": "Enhances up to 2 selected cards into Multi cards",
    "The Emperor": "Creates 2 random Tarot cards, or less if there is insufficient space",
    "The Hierophant": "Enhances up to 2 selected cards into Bonus cards",
    "The Lovers": "Enhances 1 selected card into a Wild card",
    "The Chariot": "Enhances 1 selected card into a Steel card",
    "Justice": "Enhances 1 selected card into a Glass card",
    "The Hermit": "Doubles your money, up to $20 max",
    "The Wheel of Fortune": '1 in 4 chance of adding Foil, Holographic or Polychrome editions to a random Joker. It cheerfully goes "Nope!" when it fails',
    "Strength": "Increases the rank of up to 2 selected cards by 1 (for example, 4 to 5, 10 to Jack, King to Ace)",
    "The Hanged Man": "Destroys up to 2 selected cards",
    "Death": "With 2 cards selected, it converts the left card into a copy of the right card (Cards can be rearranged in hand to get the desired left/right order)",
    "Temperance": "Gives the total selling value of all currently held Jokers (up to a max of $50)",
    "The Devil": "Enhances 1 selected card into a Gold card",
    "The Tower": "Enhances 1 selected card into a Stone card",
    "The Star": "Converts up to 3 selected cards to Diamonds. Their rank and upgrades are unchanged",
    "The Moon": "Converts up to 3 selected cards to Clubs. Their rank and upgrades are unchanged",
    "The Sun": "Converts up to 3 selected cards to Hearts. Their rank and upgrades are unchanged",
    "Judgement": "Creates a random Joker card, if there is sufficient space",
    "The World": "Converts up to 3 selected cards to Spades. Their rank and upgrades are unchanged",
    "Bonus": "+30 Chips",
    "Mult": "+4 Mult",
    "Wild": "Is considered to be every suit simultaneously",
    "Glass": "x2 Mult, 1 in 4 chance to destroy card after scoring",
    "Steel": "x1.5 Mult while this card stays in hand",
    "Stone": "50 Chips, No rank or suit",
    "Gold": "$3 if this card is held in hand at end of round",
    "Lucky": "1 in 5 chance for +20 Mult, 1 in 15 chance to win $20",
    "Base": "No extra effects",
    "Foil": "+50 Chips",
    "Holo": "+10 Mult",
    "Polychrome": "x1.5 Mult",
    "Negative": "+1 Joker/Consumable slot (Only for Jokers, except for Consumables created by Perkeo Perkeo. Slot type offered is equal to card type.)",
    "Gold Seal": "Earn $3 when this card is played and scores",
    "Red Seal": "Retrigger this card 1 time",
    "Blue Seal": "Creates a Planet card if this card is held in hand at end of round, if you have room",
    "Purple Seal": "Creates a Tarot card when discarded, if you have room",
    "White Stake": "Base difficulty",
    "Red Stake": "Small Blind gives no reward money, unlocks the Zodiac Deck",
    "Green Stake": "Required score scales faster for each Ante, unlocks the Painted Deck",
    "Black Stake": "Shop can have Eternal Jokers (Can't be sold or destroyed), unlocks the Anaglyph Deck. Note: Each Joker has a 30% chance of being Eternal.",
    "Blue Stake": "-1 Discard, unlocks the Plasma Deck",
    "Purple Stake": "Required score scales faster for each Ante",
    "Orange Stake": "Booster Packs cost $1 more per Ante, unlocks the Erratic Deck",
    "Gold Stake": "-1 hand size",
    "Small Blind": "No special effects. Can be skipped to receive a Tag.",
    "Big Blind": "No special effects. Can be skipped to receive a Tag.",
    "The Hook": "Discards 2 random cards from your hand, after each hand played.",
    "The Ox": "Playing your most played hand will set money to $0",
    "The House": "The first hand of cards is drawn completely face-down",
    "The Wall": "Extra large blind",
    "The Wheel": "1 in 7 cards are drawn face-down throughout the round",
    "The Arm": "Decreases the level of Hand you play by 1. (Hand levels can go to Level 1, and are reduced before scoring.)",
    "The Club": "All Club cards are debuffed",
    "The Fish": "The cards drawn after you play a hand are drawn face-down. (You can still sort by Suit/Rank to guess them.)",
    "The Psychic": "Hands must have five cards. (They do not all need to be scoring.)",
    "The Goad": "All Spade cards are debuffed",
    "The Water": "Start the round with no discards",
    "The Window": "All Diamond cards are debuffed",
    "The Manacle": "-1 hand size for this round",
    "The Eye": "Every hand played this round must be a different type, and not previously played this round.",
    "The Mouth": "Only one hand type can be played this round.",
    "The Plant": "All face cards are debuffed",
    "The Serpent": "After playing a hand or discarding cards, you always draw 3 more cards. Maximum hand size is ignored.",
    "The Pillar": "Cards played previously this ante (during Small and Big Blinds) are debuffed.",
    "The Needle": "Play only one, single hand.",
    "The Head": "All Heart cards are debuffed",
    "The Tooth": "Lose $1 per card played",
    "The Flint": "The base chips and Mult for playing a poker hand are halved this round",
    "The Mark": "All face cards are drawn face-down. (They can still be sorted by Suit.)",
    "Amber Acorn": "Flips and shuffles all Joker cards",
    "Verdant Leaf": "All cards debuffed until 1 Joker sold",
    "Violet Vessel": "Extremely large blind",
    "Crimson Heart": "One of your Jokers is disabled on every hand. (Only one Joker is disabled at a time.)",
    "Cerulean Bell": "The Blind forces 1 random card in your hand to be selected, at all times",
    "Uncommon tag": "In the next Shop, an Uncommon Joker is guaranteed.",
    "Rare tag": "In the next Shop, a Rare Joker is guaranteed.",
    "Negative tag": "The next base edition Joker you find in a Shop becomes Negative (+1 joker slot).",
    "Foil Tag": "The next base edition Joker you find in a Shop becomes Foil (+50 Chips).",
    "Holographic tag": "The next base edition Joker you find in a Shop becomes Holographic (+10 Mult).",
    "Polychrome tag": "The next base edition Joker you find in a Shop becomes Polychrome (x1.5 Mult).",
    "Investment tag": "Gain $15 after defeating the next Boss Blind.",
    "Voucher": "Adds a Voucher to the next Shop. If the current voucher hasn't been bought yet, you will have two to choose from.",
    "Boss tag": "Re-rolls the next Boss Blind.",
    "Standard tag": "Immediately open a free Mega Standard Pack.",
    "Charm tag": "Immediately open a free Mega Arcana Pack.",
    "Meteor tag": "Immediately open a free Mega Celestial Pack.",
    "Buffoon tag": "Immediately open a free Mega Buffoon Pack.",
    "Handy tag": "Gain $1 for each hand played this run.",
    "Garbage tag": "Gain $1 for each unused discard this run.",
    "Ethereal tag": "Immediately open a free Spectral Pack.",
    "Coupon tag": "In the next shop, initial Jokers and Booster Packs are free ($0). Vouchers, rerolls, and Jokers from re-rolls keep their usual cost.",
    "Double tag": "Gives a copy of the next Tag selected (excluding Double Tags). Each additional Double Tag adds one additional copy of the selected tag.",
    "Juggle tag": "+3 Hand Size for the next round only.",
    "D6 tag": "In the next Shop, re-rolls start at $0 (going up $1 per re-roll as normal).",
    "Top-up tag": "Create up to 2 Common Jokers (if you have space).",
    "Speed tag": "Gives $5 for each Blind you've skipped this run (including the Blind skipped to gain this Tag).",
    "Orbital tag": "Upgrades a Poker Hand by three levels. (The hand is decided by the Tag, not selected by the player.)",
    "Economy tag": "Doubles your money (adds a maximum of $40).",
    "Pluto": "Levels up High Card by +1 Mult and +10 Chips. When no other hand is possible, the one highest card in your hand. Aces are counted high for this card.",
    "Mercury": "Levels up Pair by +1 Mult and +15 Chips. Two cards with a matching rank. Suits don't matter.",
    "Uranus": "Levels up Two Pair by +1 Mult and +20 Chips. Two cards with a matching rank, and two cards with any other matching rank. Suits don't matter.",
    "Jupiter": "Levels up Flush by +2 Mult and +15 Chips. Five cards of any rank, all from a single suit.",
    "Venus": "Levels up Three of a Kind by +2 Mult and +20 Chips. Three cards with a matching rank. Suits don't matter.",
    "Earth": "Levels up Full House by +2 Mult and +25 Chips. Three cards with a matching rank, and two cards with any other matching rank which are not all the same suit.",
    "Saturn": "Levels up Straight by +2 Mult and +30 Chips. Five cards in order, which are not all from the same suit. (For example, A/K/Q/J/10 or 7/6/5/4/3.) Aces can be counted high or low, but not both at once (K/A/2/3/4 does not work).",
    "Mars": "Levels up Four of a Kind by +3 Mult and +30 Chips. Four cards with a matching rank. Suits don't matter.",
    "Neptune": "Levels up Straight Flush by +3 Mult and +40 Chips. Five cards in order, all from a single suit. When the five cards are A/K/Q/J/10, this is displayed as a Royal Flush.",
    "Planet X": "Levels up Five of a Kind by +3 Mult and +35 Chips. Five cards with the same rank which are not all the same suit. (This card can only be encountered after adding or altering cards in your deck and playing the corresponding hand at least once.)",
    "Ceres": "Levels up Flush House by +3 Mult and +40 Chips. Three cards with the same rank, and two cards with the same rank, all from a single suit. (This card can only be encountered after adding or altering cards in your deck and playing the corresponding hand at least once.)",
    "Eris": "Levels up Flush Five by +3 Mult and +40 Chips. Five cards with the same rank and same suit. (This card can only be encountered after adding or altering cards in your deck and playing the corresponding hand at least once.)",
    "Familiar": "Destroy 1 random card in your hand, but add 3 random Enhanced face cards instead",
    "Grim": "Destroy 1 random card in your hand, but add 2 random Enhanced Aces instead",
    "Incantation": "Destroy 1 random card in your hand, but add 4 random Enhanced numbered cards instead",
    "Talisman": "Adds a Gold Seal to 1 selected card",
    "Aura": "Adds a Foil, Holographic, or Polychrome effect (determined at random) to 1 selected card in hand",
    "Wraith": "Creates a random Rare Joker (must have room), but sets money to $0",
    "Sigil": "Converts every card in your hand to a single, random Suit",
    "Ouija": "Converts every card in your hand to a single, random Rank, but reduces total hand size by 1",
    "Ectoplasm": "Adds Negative to a random Joker, but reduces total hand size by 1",
    "Immolate": "Destroys 5 random cards in hand, but gain $20",
    "Ankh": "Creates a copy of 1 of your Jokers at random, then destroys the others, leaving you with two identical Jokers. (Enhancements are also copied, except Negative)",
    "Deja Vu": "Adds a Red Seal to 1 selected card",
    "Hex": "Adds Polychrome to a random Joker, and destroys the rest",
    "Trance": "Adds a Blue Seal to 1 selected card",
    "Medium": "Adds a Purple Seal to 1 selected card",
    "Cryptid": "Creates 2 exact copies (including Enhancements) of a selected card in your hand",
    "The Soul": "Creates a Legendary Joker, if you have room. (This can also occasionally be found in Tarot Packs as well as Spectral Packs.)",
    "Black Hole": "Upgrades every poker hand - including hands not yet discovered - by one level. (This can also occasionally be found in Celestial Packs as well as Spectral Packs.)",
    "Red Deck": "+1 discard every round\tNone - this is the starting deck.",
    "Blue Deck": "+1 hand every round\tDiscover at least 20 items from your collection.",
    "Yellow Deck": "Start with an extra $10\tDiscover at least 50 items from your collection.",
    "Green Deck": "You don't earn interest. Instead, gain $2 per remaining Hand and $1 per remaining Discard at the end of each round.\tDiscover at least 75 items from your collection.",
    "Black Deck": "+1 Joker slot, but -1 hand every round\tDiscover at least 100 items from your collection.",
    "Magic Deck": "Start run with the Crystal Ball voucher and 2 copies of The Fool\tWin a run with the Red Deck on any difficulty.",
    "Nebula Deck": "Start run with the Telescope voucher but -1 consumable slot.\tWin a run with the Blue Deck on any difficulty.",
    "Ghost Deck": "Spectral Cards may appear individually in the shop, and you start with a Hex card.\tWin a run with the Yellow Deck on any difficulty.",
    "Abandoned Deck": "This deck is smaller than normal as it has no Face Cards in it.\tWin a run with the Green Deck on any difficulty.",
    "Checkered Deck": "Start run with 26 Spades and 26 Hearts in deck, and no Clubs or Diamonds.\tWin a run with the Black Deck on any difficulty.",
    "Zodiac Deck": "Start the run with Tarot Merchant, Planet Merchant, and Overstock vouchers.\tWin a run with any deck on the Red Stake difficulty or harder.",
    "Painted Deck": "+2 Hand Size, -1 Joker Slot.\tWin a run with any deck on the Green Stake difficulty or harder.",
    "Anaglyph Deck": "After defeating each Boss Blind, gain a Double Tag\tWin a run with any deck on the Black Stake difficulty or harder.",
    "Plasma Deck": "Balance Chips and Mult when calculating score for played hand. X2 base Blind size. (Your chips and mult become averaged before scoring)\tWin a run with any deck on the Blue Stake difficulty or harder.",
    "Erratic Deck": "All Ranks and Suits in deck are randomized\tWin a run with any deck on the Orange Stake difficulty or harder.",
    "Challenge deck": "This back is used for the deck used during Challenge runs.\tChallenge mode is unlocked by winning a regular run with five different decks.",
    "Overstock": "The shop has an additional card slot, increasing it to 3 slots",
    "Overstock Plus": "The shop has an additional card slot, increasing it to 4 card slots in total",
    "Clearance Sale": "All cards and booster packs in the shop are 25% off from their normal price (Note: This also reduces the sell value of your present jokers)",
    "Liquidation": "All cards and booster packs in the shop are 50% off from their normal price (Note: This also reduces the sell value of your present jokers)",
    "Hone": "Foil, Holographic, and Polychrome cards appear 2x more often than normal",
    "Glow Up": "Foil, Holographic, and Polychrome cards appear 4x more often than normal",
    "Reroll Surplus": "Rerolls cost $2 less",
    "Reroll Glut": "Rerolls cost an additional $2 less (so $4 less in total)",
    "Crystal Ball": "+1 consumable slot",
    "Omen Globe": "Spectral cards may appear in Arcana Booster Packs",
    "Telescope": "Celestial Packs always contain the Planet card for your most played poker hand in this run",
    "Observatory": "Planet cards in your Consumables area give x1.5 Mult for their specified hand",
    "Grabber": "Permanently gain +1 hand per round",
    "Nacho Tong": "Permanently gain an additional +1 hand per round",
    "Wasteful": "Permanently gain +1 discard per round",
    "Recyclomancy": "Permanently gain an additional +1 discard per round",
    "Tarot Merchant": "Tarot cards appear 2x more frequently in the shop than normal",
    "Tarot Tycoon": "Tarot cards appear 4x more frequently in the shop than normal",
    "Planet Merchant": "Planet cards appear 2x more frequently in the shop than normal",
    "Planet Tycoon": "Planet cards appear 4x more frequently in the shop than normal",
    "Seed Money": "Raise the cap on interest earned per round to $10",
    "Money Tree": "Raise the cap on interest earned per round to $20",
    "Blank": "Does nothing.",
    "Antimatter": "+1 Joker slot",
    "Magic Trick": "Playing Cards can be purchased individually from the shop",
    "Illusion": "Cards bought from the shop can have an enhancement, edition, and/or seal",
    "Hieroglyph": "-1 Ante, but also -1 hand per round",
    "Petroglyph": "-1 Ante again, but also -1 discard per round",
    "Director's Cut": "Reroll the Boss Blind once per Ante, costing $10 per roll",
    "Retcon": "Reroll the Boss Blind unlimited times, costing $10 per roll",
    "Paint Brush": "+1 to your max hand size",
    "Palette": "+1 to your max hand size again",
    "High Card": {
        "Base Score": "5 Chips x 1 Mult",
        "How to Play the Hand": "When no other hand is possible, the one highest card in your hand. Aces are counted high for this card.",
    },
    "Pair": {
        "Base Score": "10 Chips x 2 Mult",
        "How to Play the Hand": "Two cards with a matching rank. Suits may differ.",
    },
    "Two Pair": {
        "Base Score": "20 Chips x 2 Mult",
        "How to Play the Hand": "Two cards with a matching rank, and two cards with any other matching rank. Suits may differ.",
    },
    "Three of a Kind": {
        "Base Score": "30 Chips x 3 Mult",
        "How to Play the Hand": "Three cards with a matching rank. Suits may differ.",
    },
    "Straight": {
        "Base Score": "30 Chips x 4 Mult",
        "How to Play the Hand": "Five cards in consecutive order which are not all from the same suit. Aces can be counted high or low, but not both at once.",
    },
    "Flush": {
        "Base Score": "35 Chips x 4 Mult",
        "How to Play the Hand": "Five cards of any rank, all from a single suit.",
    },
    "Full House": {
        "Base Score": "40 Chips x 4 Mult",
        "How to Play the Hand": "Three cards with a matching rank, and two cards with any other matching rank, with cards from two or more suits.",
    },
    "Four of a Kind": {
        "Base Score": "60 Chips x 7 Mult",
        "How to Play the Hand": "Four cards with a matching rank. Suits may differ.",
    },
    "Straight Flush": {
        "Base Score": "100 Chips x 8 Mult",
        "How to Play the Hand": "Five cards in consecutive order, all from a single suit.",
    },
    "Royal Flush": {
        "Base Score": "100 Chips x 8 Mult",
        "How to Play the Hand": "An ace-high Straight Flush formed by playing A K Q J 10 of the same suit. (For most purposes, including Levelling, this is considered to be a Straight Flush and not displayed as a separate type of hand.)",
    },
    "Five of a Kind": {
        "Base Score": "120 Chips x 12 Mult",
        "How to Play the Hand": "Five cards with the same rank which are not all the same suit.",
    },
    "Flush House": {
        "Base Score": "140 Chips x 14 Mult",
        "How to Play the Hand": "Three cards with the same rank, and two cards with the same rank, all from a single suit.",
    },
    "Flush Five": {
        "Base Score": "160 Chips x 16 Mult",
        "How to Play the Hand": "Five cards with the same rank and same suit.",
    },
}

# Initialize Reddit instance
reddit = praw.Reddit(
  client_id = client_id,
  client_secret = client_secret,
  username = username,
  password = password,
  user_agent="Balatro Helper (by u/eBanta)",
)

# Subreddit to monitor
subreddit = reddit.subreddit("balatro")


# Define a function to extract card names from comments
def extract_card_names(comment_body):
    pattern = r"\[\[(.*?)\]\]"
    card_names = re.findall(pattern, comment_body)
    matched_card_names = []
    for card_name in card_names:
        for key in card_info_dict.keys():
            # Using word boundaries to match whole words only
            if re.search(r"\b" + re.escape(card_name) + r"\b", key, re.IGNORECASE):
                matched_card_names.append(key)
                break
    return matched_card_names


# Function to load responded comment IDs from a file
def load_responded_comments():
    if os.path.exists("responded_comments.txt"):
        with open("responded_comments.txt", "r") as file:
            return set(file.read().splitlines())
    else:
        return set()


# Function to save responded comment IDs to a file
def save_responded_comments(responded_comments):
    with open("responded_comments.txt", "w") as file:
        file.write("\n".join(responded_comments))


# Load responded comment IDs
responded_comments = load_responded_comments()

# Main loop
logger.info("BalatroBot started...")
logger.info("BalatroBot is now listening for comments...")
try:
    for comment in subreddit.stream.comments():
        try:
            # Check if the comment has already been responded to
            if comment.id in responded_comments:
                continue

            logger.info(f"Processing comment: {comment.id}")
            matched_card_names = extract_card_names(comment.body)
            if matched_card_names:
                response = "Here is some information about the cards you mentioned:\n\n"
                for card_name in matched_card_names:
                    if card_name in card_info_dict:
                        card_description = card_info_dict[card_name]
                        response += f"**{card_name}:**\n{card_description}\n\n"
                    else:
                        response += f"**{card_name}:** No information available\n\n"
                response += "\nThank you for using u/BalatroBot! :)"
                # Reply to the comment
                comment.reply(response)
                # Add the comment ID to the set of responded comments
                responded_comments.add(comment.id)
                # Save responded comment IDs
                save_responded_comments(responded_comments)
        except Exception as e:
            logger.error(
                f"An error occurred while processing comment {comment.id}: {e}"
            )
            # Continue processing other comments even if one fails
except KeyboardInterrupt:
    logger.info("Bot stopped by user.")
    sys.exit()
