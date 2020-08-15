from settings import debug_output
import random


class Node:
    def __init__(self, data: str, node_id: int):
        self.data: str = data
        self._prev_node: Node = None
        self._next_node: Node = None
        self._prev_node_original: Node = None
        self._next_node_original: Node = None
        self.node_id: int = node_id

    @property
    def next_node(self):
        return self._next_node

    @next_node.setter
    def next_node(self, node):
        self._next_node = node
        if self._next_node_original is None:
            self._next_node_original = node

    @property
    def prev_node(self):
        return self._prev_node

    @prev_node.setter
    def prev_node(self, node):
        self._prev_node = node
        if self._prev_node_original is None:
            self._prev_node_original = node

    @property
    def next_node_original(self):
        return self._next_node_original

    @property
    def prev_node_original(self):
        return self._prev_node_original

    def __str__(self):
        prev_data: str = "None"
        if self.prev_node is not None:
            prev_data = self.prev_node.data
        next_data: str = "None"
        if self.next_node is not None:
            next_data = self.next_node.data
        return f"(\"{prev_data}\" | \"{self.data}\" | \"{next_data}\" | \"{self.node_id}\")"

    def __hash__(self):
        return self.node_id


class Operation:
    def __init__(
        self,
        indent_direction: int = 0,
        return_after: bool = True,
        previous_indent: int = 0,
        no_return_node: Node = None,
        no_space: bool = False,
        special_node: Node = None,
        special_operation=None,
    ):
        if ((special_node is None and special_operation is not None)
                or (special_node is not None and special_operation is None)):
            raise ValueError("You must fill both special_node and special_operation")
        self.indent_direction = indent_direction
        self.return_after = return_after
        self.previous_indent = previous_indent
        self.no_return_node = no_return_node
        self.no_space = no_space
        self.special_node = special_node
        self.special_operation = special_operation

    def __str__(self):
        objects: list = []
        if self.indent_direction != 0:
            objects.extend([f"indent_direction:", str(self.indent_direction)])
        if self.return_after is not True:
            objects.extend([f"return_after:", str(self.return_after)])
        if self.indent_direction != 0:
            objects.extend([f"previous_indent:", str(self.previous_indent)])
        if self.no_return_node is not None:
            objects.extend([f"no_return_node:", str(self.no_return_node)])
        if self.no_space is True:
            objects.extend([f"no_space:", str(self.no_space)])
        if self.special_node is not None:
            objects.extend(
                [
                    f"special_node:",
                    str(self.special_node),
                    f"special_operation:",
                    str(self.special_operation),
                ]
            )

        return f"({' '.join(objects)})"


class LinkedList:
    def __init__(self):
        self.head: Node = None

    def __str__(self):
        node = self.head
        output = ""
        while node is not None:
            output += node.data
            node = node.next_node
        return output

    @debug_output
    def build_from_array(self, array: list):
        for item in array:
            self.append(item)

    @debug_output
    def get_ids(self):
        ids = []
        node = self.head
        while node is not None:
            ids.append(node.node_id)
            node = node.next_node
        return ids

    @debug_output
    def get_new_id(self):
        new_id = random.randint(0, 1000000000)
        while new_id in self.get_ids():
            new_id = random.randint(0, 1000000000)
        return new_id

    @debug_output
    def append(self, data: str):
        new_node = Node(data, self.get_new_id())
        if self.head is None:
            self.head = new_node
            return
        if self.head.next_node is None:
            self.head.next_node = new_node
            new_node.prev_node = self.head
            return
        node = self.head
        while True:
            if node.next_node is None:
                break
            node = node.next_node
        node.next_node = new_node
        new_node.prev_node = node

    @staticmethod
    @debug_output
    def get_distance_to_data(node: Node, data: str, direction: int):
        if direction not in [-1, 1]:
            raise ValueError("direction but be 1 or -1")
        count = 0
        temp_node = node
        while temp_node is not None:
            count += 1
            if direction == -1:
                temp_node = temp_node.prev_node
            if direction == 1:
                temp_node = temp_node.next_node
            if temp_node is None:
                return -1
            if temp_node.data.isspace() or temp_node.data == "":
                count -= 1
            if temp_node.data == data:
                return count
        return -1

    @staticmethod
    @debug_output
    def get_distance_to_node(starting_node: Node, target_node: Node, direction: int):
        if direction not in [-1, 1]:
            raise ValueError("direction but be 1 or -1")

        if target_node is None:
            return -1

        return LinkedList.get_distance_to_data(
            starting_node, target_node.data, direction
        )

    @debug_output
    def insert_before(self, node: Node, data: str):
        new_node = Node(data, self.get_ids())
        prev_node = node.prev_node

        node.prev_node = new_node
        if prev_node is not None:
            prev_node.next_node = new_node
        new_node.prev_node = prev_node

        new_node.next_node = node

    @debug_output
    def insert_after(self, node: Node, data: str):
        new_node = Node(data, self.get_ids())
        next_node = node.next_node
        node.next_node = new_node

        if next_node is not None:
            next_node.prev_node = new_node
            new_node.next_node = next_node

        new_node.prev_node = node


class Indent:
    def __init__(self, spaces: int = 4):
        self.indent = 0
        self.spaces = spaces

    def modify_indent(self, direction):
        self.indent += direction

        if self.indent < 0:
            self.indent = 0

    def calculate_indent(self):
        return "".join([" "] * self.indent * self.spaces)

    def __str__(self):
        return f"{self.indent}"
