class Node:
    def __init__(self, value: str):
        self.children = {}
        self.value = value

    def getChild(self, value) -> 'Node':
        return self.children.get(value, None)

    def addChild(self, value: str):
        if value not in self.children:
            self.children[value] = Node(value)
