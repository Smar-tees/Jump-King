import game
from shared_data import king_state
import level_loader


level = level_loader.load_level()
game.game_loop(king_state, level)