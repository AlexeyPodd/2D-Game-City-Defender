from sqripts import *

my_game = Game()

my_game.instruct_player()
while my_game.level_number < 11 and len(my_game.city):

    my_game.show_transit_screen()
    my_game.run_level()

my_game.show_transit_screen()
