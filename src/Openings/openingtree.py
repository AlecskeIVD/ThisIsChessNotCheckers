import re

from src.Openings.node import Node


class Tree:
    def __init__(self):
        self.root = Node("")

        path = '/Users/alecvandeuren/ThisIsChessNotCheckers/assets/GM_games/WijkaanZee'
        for year in range(2006, 2021):
            temp_path = path + str(year) + '.txt'
            games = load_moves_up_to_nth(temp_path, 7)
            for game in games:
                node = self.root
                for move in game:
                    node.addChild(move)
                    node = node.getChild(move)

    def getNextMoves(self, moves: str) -> None or list[str]:
        """
        Returns a list of all the next moves played in WijkaanZee following the previous moves
        :param moves: The moves in order, split by a space, to get next known moves
        """
        node = self.root
        for move in moves:
            node = node.getChild(move)
            if node is None:
                return None
        return node.children.keys()


def get_moves(content):
    turns = content.split('.')
    actual_turns = [turn[:-2] for turn in turns]
    output = []
    for turn in actual_turns:
        turn = turn.strip()
        output += turn.split()

    return output


def load_moves_up_to_nth(file_path, up_to_move):
    with open(file_path, 'r') as file:
        content = file.read()
        # Split the content by empty lines to separate games
        games = re.split(r'\n\n+', content)
        all_games_moves = []

        for game in games:
            moves = get_moves(game)
            # Extract moves up to the specified move count
            move_count = min(up_to_move * 2, len(moves))
            all_games_moves.append(moves[:move_count])

        return all_games_moves
