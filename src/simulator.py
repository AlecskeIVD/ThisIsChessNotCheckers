from src.Openings.openingtree import Tree
from src.gamestate import Gamestate


def main():
    white = int(input("Which version would you like for white? "))
    black = int(input("Which version would you like for black? "))
    n = int(input("How many times would you like to simulate? "))
    white_wins = 0
    black_wins = 0
    draws = 0
    openingTree = Tree()
    for i in range(1,n+1):
        print(f"Game {i}: White has won {white_wins} games, black has won {black_wins} games and there have been {draws} draws.")
        gs = Gamestate()
        game_is_over = False
        while not game_is_over:
            print(f'Turn {(gs.move // 2) + 1}: Current evaluation gives: {gs.evaluate()}')
            gs.computer_makes_move(white, openingTree)
            if gs.white_wins():
                game_is_over = True
                white_wins += 1
            elif gs.black_wins():
                game_is_over = True
                black_wins += 1
            elif gs.stalemate():
                game_is_over = True
                draws += 1
            else:
                gs.computer_makes_move(black, openingTree)
                if gs.white_wins():
                    game_is_over = True
                    white_wins += 1
                elif gs.black_wins():
                    game_is_over = True
                    black_wins += 1
                elif gs.stalemate():
                    game_is_over = True
                    draws += 1
    print(f"Simulation is over\nWhite wins {100*white_wins/n}% as version {white}\nBlack wins {100*black_wins/n}% as "
          f"version {black}\n{100*draws/n}% of games end in a draw")


if __name__ == "__main__":
    main()
