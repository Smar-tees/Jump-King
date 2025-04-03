import game
import shared_data
import level_loader


level = level_loader.load_level()
game.game_loop(shared_data, level)