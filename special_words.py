from objects import LinkedList, Node, Operation
from settings import debug_output


class SpecialWords:
    @staticmethod
    @debug_output
    def sw_desc(linked_list: LinkedList, node: Node):
        return Operation(True)

    @staticmethod
    @debug_output
    def sw_comma(linked_list: LinkedList, node: Node):
        operation = SpecialWords.all_others(linked_list, node)
        return operation

    @staticmethod
    @debug_output
    def sw_union(linked_list: LinkedList, node: Node):
        next_node = node.next_node
        if next_node.data == "ALL":
            next_node.special_operation = Operation(True, indent_direction=1)
            return Operation(False, previous_indent=-1, no_space=False)
        return Operation(True, no_space=False)

    @staticmethod
    @debug_output
    def sw_all(linked_list: LinkedList, node: Node):
        return Operation(True, no_space=False)

    @staticmethod
    @debug_output
    def sw_not(linked_list: LinkedList, node: Node):
        return Operation(False, no_space=False)

    @staticmethod
    @debug_output
    def sw_open_comment(linked_list: LinkedList, node: Node):
        close_node: Node = node.next_node
        length: int = 0
        nodes: list[Node] = []
        splits: list[Node] = []
        while close_node is not None:
            if close_node.data == "*/":
                break
            if length > 40 and close_node.next_node.data != "*/":
                splits.append(close_node)
                length = 0
            length += len(close_node.data)
            nodes.append(close_node)
            close_node = close_node.next_node
        if close_node is not None:
            for modify_node in nodes:
                modify_node.special_operation = Operation(False, no_space=False)

            if len(splits) > 0:
                close_node.prev_node_original.special_operation = None
                for split in splits:
                    split.special_operation = Operation(True, no_space=False)
            else:
                return Operation(False, no_space=False)
        return Operation(True, no_space=False)

    @staticmethod
    @debug_output
    def sw_left(linked_list: LinkedList, node: Node):
        if node.next_node.data == "JOIN":
            return Operation(False, previous_indent=-1, indent_direction=1)
        return SpecialWords.all_others(linked_list, node)

    @staticmethod
    @debug_output
    def sw_case(linked_list: LinkedList, node: Node):
        close_node, length, max_skip = SpecialWords.get_open_or_close_node(
            node, "CASE", "END", "right"
        )
        if close_node is None:
            raise Exception("Couldn't find END node")
        if linked_list.get_distance_to_data(node, "WHEN", 1) == 1:
            if length > 10:
                close_node.special_operation = Operation(True, no_space=False)
                return Operation(True, indent_direction=1, special_node=close_node)
            else:
                return Operation(False, no_space=False)
        else:
            raise NotImplemented("Case followed by an expression")

    @staticmethod
    @debug_output
    def sw_when(linked_list: LinkedList, node: Node):
        no_return_node = node.next_node
        while no_return_node.next_node.data != "THEN":
            no_return_node = no_return_node.next_node
        return Operation(
            return_after=False, no_return_node=no_return_node, no_space=False
        )

    @staticmethod
    @debug_output
    def sw_then(linked_list: LinkedList, node: Node):
        distances = {
            "WHEN": linked_list.get_distance_to_data(node, "WHEN", 1),
            "ELSE": linked_list.get_distance_to_data(node, "ELSE", 1),
            "END": linked_list.get_distance_to_data(node, "END", 1),
        }
        for key in [key for key in distances.keys()]:
            if distances[key] < 1:
                del distances[key]
        key_min = min(distances.keys(), key=(lambda k: distances[k]))
        no_return_node = node.next_node
        while no_return_node.next_node.data != key_min:
            no_return_node = no_return_node.next_node
        return Operation(False, no_space=True, no_return_node=no_return_node)

    @staticmethod
    @debug_output
    def sw_else(linked_list: LinkedList, node: Node):
        no_return_node = node.next_node
        while no_return_node.next_node.data != "END":
            no_return_node = no_return_node.next_node
        return Operation(False, no_space=True, no_return_node=no_return_node)

    @staticmethod
    @debug_output
    def sw_end(linked_list: LinkedList, node: Node):
        if node.next_node.data == "AS":
            no_return_node = node.next_node.next_node
            return Operation(False, no_return_node=no_return_node, no_space=False)
        elif node.next_node.data == "AND":
            return Operation(True, indent_direction=-1)
        else:
            return Operation(True)

    @staticmethod
    @debug_output
    def sw_window_functions(linked_list: LinkedList, node: Node):
        as_node = node
        while as_node.data != "AS":
            as_node = as_node.next_node
        return Operation(True, no_return_node=as_node)

    @staticmethod
    @debug_output
    def sw_distinct(linked_list: LinkedList, node: Node):
        return Operation(True, indent_direction=1)

    @staticmethod
    @debug_output
    def sw_order(linked_list: LinkedList, node: Node):
        return Operation(False, no_space=False, previous_indent=-1, indent_direction=1)

    @staticmethod
    @debug_output
    def sw_null(linked_list: LinkedList, node: Node):
        return SpecialWords.all_others(linked_list, node)

    @staticmethod
    @debug_output
    def sw_create(linked_list: LinkedList, node: Node):
        as_node = node
        while as_node.data != "AS":
            as_node = as_node.next_node
        return Operation(True, no_return_node=as_node)

    @staticmethod
    @debug_output
    def sw_or_sticks(linked_list: LinkedList, node: Node):
        return Operation(False, previous_indent=1, indent_direction=-1)

    @staticmethod
    @debug_output
    def sw_between(linked_list: LinkedList, node: Node):
        close_node: Node = node
        distance = 0
        while distance != 2:
            distance += 1
            close_node = close_node.next_node
        return Operation(False, no_return_node=close_node)

    @staticmethod
    @debug_output
    def sw_by(linked_list: LinkedList, node: Node):
        if linked_list.get_distance_to_data(node, "GROUP", -1) == 1:
            return Operation(True, indent_direction=1)
        return SpecialWords.all_others(linked_list, node)

    @staticmethod
    @debug_output
    def sw_group(linked_list: LinkedList, node: Node):
        return_after: bool = True
        if linked_list.get_distance_to_data(node, "BY", 1) == 1:
            return_after = False
        return Operation(return_after, previous_indent=-1)

    @staticmethod
    @debug_output
    def sw_equal(linked_list: LinkedList, node: Node):
        return Operation(False, no_space=False)

    @staticmethod
    @debug_output
    def sw_and(linked_list: LinkedList, node: Node):
        if node.next_node.data == "CASE":
            return Operation(True, indent_direction=1)
        return Operation(False, no_space=False)

    @staticmethod
    @debug_output
    def sw_on(linked_list: LinkedList, node: Node):
        no_return_node = node
        while not SpecialWords.end_of_equality(linked_list, no_return_node):
            no_return_node = no_return_node.next_node
        if no_return_node == node or node.next_node.data == "(":
            return Operation(False, no_space=False)
        return Operation(False, no_return_node=no_return_node, no_space=False)

    @staticmethod
    @debug_output
    def sw_join(linked_list: LinkedList, node: Node):
        if SpecialWords.is_alias(linked_list, node.next_node.next_node):
            no_return_node = node.next_node.next_node
            return Operation(
                False, previous_indent=-1, no_return_node=no_return_node, no_space=False
            )
        return Operation(
            False, previous_indent=-1, no_return_node=node.next_node, no_space=False
        )

    @staticmethod
    @debug_output
    def sw_function(linked_list: LinkedList, node: Node):
        return Operation(False, no_space=True)

    @staticmethod
    @debug_output
    def all_others(linked_list: LinkedList, node: Node):
        next_node: Node = node.next_node
        if next_node is not None and next_node.data == ",":
            return Operation(False, no_space=True)
        if SpecialWords.is_in_block_comment(linked_list, node):
            return Operation(True, no_space=False)
        if SpecialWords.end_of_simple_select(linked_list, node):
            return Operation(True, indent_direction=-1)
        if SpecialWords.inside_simple_select(linked_list, node):
            return Operation(False, no_space=False)
        if SpecialWords.is_alias(linked_list, node):
            if linked_list.get_distance_to_data(node, "ON", 1) == 1:
                return Operation(True, indent_direction=1)
            distances = [
                linked_list.get_distance_to_data(node, "ORDER", 1),
                linked_list.get_distance_to_data(node, "JOIN", 1),
                linked_list.get_distance_to_data(node, "WHERE", 1),
                linked_list.get_distance_to_data(node, "UNION", 1),
            ]
            if 1 in distances:
                return Operation(True)
            return Operation(False, no_space=False)
        if SpecialWords.is_table_name(linked_list, node):
            if node.next_node is not None:
                if SpecialWords.is_alias(linked_list, node.next_node):
                    return Operation(False, no_space=False)
        if SpecialWords.part_of_equality(linked_list, node):
            if 1 in [
                linked_list.get_distance_to_data(node, mid, -1)
                for mid in equality_options
            ]:
                return Operation(True)
            if 1 in [
                linked_list.get_distance_to_data(node, mid, 1)
                for mid in equality_options
            ]:
                return Operation(False, no_space=False)
        open_distance = linked_list.get_distance_to_data(node, "(", -1)
        close_distance = linked_list.get_distance_to_data(node, ")", 1)
        if open_distance == 1 and close_distance == 1:
            return Operation(return_after=False, no_space=True)
        elif close_distance == 1:
            return Operation(True)
        if linked_list.get_distance_to_data(node, "AS", 1) == 1:
            return Operation(False, no_space=False)
        if linked_list.get_distance_to_data(node, "BETWEEN", 1) == 1:
            return Operation(False, no_space=False)
        if linked_list.get_distance_to_data(node, "||", 1) == 1:
            return Operation(False, no_space=False)
        return Operation(True)

    @staticmethod
    @debug_output
    def sw_with(linked_list: LinkedList, node: Node):
        if SpecialWords.is_alias(linked_list, node.next_node):
            return Operation(False, no_space=False)
        return Operation(True, indent_direction=1)

    @staticmethod
    @debug_output
    def sw_open_parenthesis(linked_list: LinkedList, node: Node):
        close_node, length, max_skip = SpecialWords.get_open_or_close_node(
            node, "(", ")", "right"
        )
        if SpecialWords.inside_simple_select(linked_list, node.next_node):
            return Operation(False, no_space=True, no_return_node=close_node)
        if linked_list.get_distance_to_node(node, close_node, 1) == 2:
            return Operation(False, no_space=True)
        if (
            node.next_node.data in single_parameter_functions
            and node.prev_node_original.data not in multi_parameter_functions
        ):
            return Operation(False, no_space=True)
        if node.prev_node_original.data in multi_parameter_functions:
            if length > 70:
                return Operation(True)
            else:
                return Operation(False, no_space=True)
        if length < 70:
            return Operation(False, no_return_node=close_node, no_space=True)
        else:
            close_node.prev_node_original.special_operation = Operation(True)
            close_node.special_operation = Operation(True)
            return Operation(True, indent_direction=1, special_node=close_node)
        return Operation(True, indent_direction=1)

    @staticmethod
    @debug_output
    def get_open_or_close_node(
        node: Node, skip_data: str, target_data: str, direction: str
    ):
        if direction not in ["left", "right"]:
            raise ValueError("direction must be 'left' or 'right'")
        if direction == "right":
            target_node: Node = node.next_node
        else:
            target_node: Node = node.prev_node_original
        to_skip: int = 0
        max_skip: int = 0
        length: int = 0
        while target_node is not None:
            length += len(target_node.data)
            if target_node.data == skip_data:
                to_skip += 1
                if max_skip < to_skip:
                    max_skip = to_skip
            if target_node.data == target_data:
                if to_skip >= 1:
                    to_skip -= 1
                else:
                    break

            if direction == "right":
                target_node = target_node.next_node
            else:
                target_node = target_node.prev_node_original
        return target_node, length, max_skip

    @staticmethod
    @debug_output
    def sw_close_parenthesis(linked_list: LinkedList, node: Node):
        open_node, length, max_skip = SpecialWords.get_open_or_close_node(
            node, ")", "(", "left"
        )
        if node.next_node is not None:
            if node.next_node.next_node.data == ",":
                if node.next_node.data == ")":
                    return Operation(False, no_space=True)
                return Operation(False, no_space=False)
            if node.next_node.data == ",":
                return Operation(False, no_space=True)
            if linked_list.get_distance_to_data(node, "AS", 1) == 1:
                return Operation(False, no_space=False)
            if linked_list.get_distance_to_data(node, ")", 1) == 1:
                return Operation(False, no_space=True)
            if node.next_node is not None and SpecialWords.is_alias(
                linked_list, node.next_node
            ):
                return Operation(False, no_space=False)
            if linked_list.get_distance_to_data(node, "(", -1) == 2:
                return Operation(False, no_space=False)
            if node.next_node.data == "||":
                return Operation(False, no_space=False)
        return Operation(True)

    @staticmethod
    @debug_output
    def sw_as(linked_list: LinkedList, node: Node):
        distances = [
            linked_list.get_distance_to_data(node, "SELECT", 1),
            linked_list.get_distance_to_data(node, "WITH", 1),
            linked_list.get_distance_to_data(node, "/*", 1),
        ]
        if 1 in distances:
            return Operation(True, indent_direction=1)
        return Operation(False, no_space=False)

    @staticmethod
    @debug_output
    def sw_select(linked_list: LinkedList, node: Node):
        from_distance = linked_list.get_distance_to_data(node, "FROM", 1)
        join_next = linked_list.get_distance_to_data(node, "JOIN", 1)
        if from_distance == 2 and join_next != 4:
            return Operation(False, no_space=False)
        if linked_list.get_distance_to_data(node, "DISTINCT", 1) == 1:
            return Operation(False, no_space=False)
        return Operation(True, indent_direction=1)

    @staticmethod
    @debug_output
    def sw_from(linked_list: LinkedList, node: Node):
        if SpecialWords.inside_simple_select(linked_list, node):
            return Operation(False, no_space=False)
        return Operation(True, indent_direction=1, previous_indent=-1)

    @staticmethod
    @debug_output
    def sw_where(linked_list: LinkedList, node: Node):
        if SpecialWords.inside_simple_select(linked_list, node):
            return Operation(False, no_space=False)
        return Operation(True, indent_direction=1, previous_indent=-1)

    @staticmethod
    @debug_output
    def sw_multi(linked_list: LinkedList, node: Node, parameter_count: int):
        close_node, length, max_skip = SpecialWords.get_open_or_close_node(
            node.next_node, "(", ")", "right"
        )
        if parameter_count == 2:
            if length < 70:
                return Operation(False, no_return_node=close_node, no_space=True)
            else:
                node.next_node.special_operation = Operation(True, indent_direction=1)
                close_node.special_operation = Operation(True, indent_direction=-1)
                return Operation(False, no_space=True)
        elif parameter_count == 3:
            return Operation(True)

    @staticmethod
    @debug_output
    def inside_simple_select(linked_list: LinkedList, node: Node):
        def calculate_distances(distance_node):
            return {
                "select_left": linked_list.get_distance_to_data(
                    distance_node, "SELECT", -1
                ),
                "select_right": linked_list.get_distance_to_data(
                    distance_node, "SELECT", 1
                ),
                "from_left": linked_list.get_distance_to_data(
                    distance_node, "FROM", -1
                ),
                "from_right": linked_list.get_distance_to_data(
                    distance_node, "FROM", 1
                ),
                "join_left": linked_list.get_distance_to_data(
                    distance_node, "JOIN", -1
                ),
                "join_right": linked_list.get_distance_to_data(
                    distance_node, "JOIN", 1
                ),
                "where_left": linked_list.get_distance_to_data(
                    distance_node, "WHERE", -1
                ),
                "where_right": linked_list.get_distance_to_data(
                    distance_node, "WHERE", 1
                ),
            }

        def process_select():
            if distances["from_right"] == 2:
                if distances["join_right"] == -1 or distances["join_right"] > 4:
                    if distances["where_right"] in [-1, 4, 5]:
                        return True
                    return False
                return False
            return False

        def process_from():
            if distances["select_left"] == 2:
                if distances["join_right"] == -1 or distances["join_right"] > 4:
                    if distances["where_right"] in [-1, 2, 3]:
                        return True
                    return False
                return False
            return False

        def process_where():
            if distances["from_left"] in [2, 3]:
                if distances["join_left"] == -1 or distances["join_left"] > 4:
                    if distances["select_left"] in [4, 5]:
                        return True
                    return False
                return False
            return False

        temp_node = node
        count = 0
        while temp_node is not None:
            if count > 2:
                return False
            distances = calculate_distances(temp_node)
            if temp_node.data == "SELECT":
                return process_select()
            if temp_node.data == "FROM":
                return process_from()
            if temp_node.data == "WHERE":
                return process_where()
            if temp_node.data == "JOIN":
                return False
            temp_node = temp_node.prev_node_original
            count += 1
        return False

    @staticmethod
    @debug_output
    def inside_simple_parenthesis(linked_list: LinkedList, node: Node):
        pass

    @staticmethod
    @debug_output
    def is_alias(linked_list: LinkedList, node: Node):
        one_distances = [
            linked_list.get_distance_to_data(node, ")", -1),
            linked_list.get_distance_to_data(node, "WITH", -1),
        ]
        two_distances = [
            linked_list.get_distance_to_data(node, "FROM", -1),
            linked_list.get_distance_to_data(node, "JOIN", -1),
        ]
        is_special_word = node.data in special_words.keys()
        if (1 in one_distances or 2 in two_distances) and not is_special_word:
            return True

    @staticmethod
    @debug_output
    def is_table_name(linked_list: LinkedList, node: Node):
        one_distances = [
            linked_list.get_distance_to_data(node, "FROM", -1),
            linked_list.get_distance_to_data(node, "JOIN", -1),
        ]
        if 1 in one_distances:
            return True
        return False

    @staticmethod
    @debug_output
    def end_of_simple_select(linked_list: LinkedList, node: Node):
        if SpecialWords.inside_simple_select(linked_list, node):
            if SpecialWords.is_alias(linked_list, node):
                return True
            elif SpecialWords.is_table_name(linked_list, node):
                return True
        return False

    @staticmethod
    @debug_output
    def end_of_list(linked_list: LinkedList, node: Node):
        from_distance = linked_list.get_distance_to_data(node, "FROM", 1)
        if from_distance == 1:
            return True
        return False

    @staticmethod
    @debug_output
    def part_of_equality(linked_list: LinkedList, node: Node):
        distances = [
            linked_list.get_distance_to_data(node, "=", -1),
            linked_list.get_distance_to_data(node, "=", 1),
        ]
        if 1 in distances:
            return True
        if node.data in equality_options:
            return True
        if linked_list.get_distance_to_data(node, "BETWEEN", 1) == 2:
            return True

        return False

    @staticmethod
    @debug_output
    def end_of_equality(linked_list: LinkedList, node: Node):
        if SpecialWords.part_of_equality(
            linked_list, node.next_node
        ) is False and SpecialWords.part_of_equality(linked_list, node):
            return True
        return False

    @staticmethod
    @debug_output
    def is_in_block_comment(linked_list: LinkedList, node: Node):
        if node.data == "here":
            print("")
        left_open = linked_list.get_distance_to_data(node, "/*", -1)
        left_close = linked_list.get_distance_to_data(node, "*/", -1)
        right_open = linked_list.get_distance_to_data(node, "/*", 1)
        right_close = linked_list.get_distance_to_data(node, "*/", 1)
        inside_block_comment = True
        if left_open == -1:
            inside_block_comment = False
        elif left_open >= left_close != -1:
            inside_block_comment = False
        if right_close == -1:
            inside_block_comment = False
        elif right_close > right_open != -1:
            inside_block_comment = False
        return inside_block_comment


equality_options = ["=", "<=", ">=", ">", "<"]

data_types = [
    "INT",
]

exceptions = ["BY"]

single_parameter_functions = [
    "MIN",
    "MAX",
    "CAST",
    "YEAR",
    "MONTH",
    "DAY",
    "LPAD",
    "VARCHAR",
    "COUNT",
    "TO_DATE",
    "DATE",
    "HOUR",
]

multi_parameter_functions = {
    "TO_VARCHAR": 2,
    "COALESCE": 2,
    "DATEDIFF": 2,
}

special_words = {
    "WITH": SpecialWords.sw_with,
    "SELECT": SpecialWords.sw_select,
    "FROM": SpecialWords.sw_from,
    "WHERE": SpecialWords.sw_where,
    "ALL-OTHERS": SpecialWords.all_others,
    "(": SpecialWords.sw_open_parenthesis,
    ")": SpecialWords.sw_close_parenthesis,
    "AS": SpecialWords.sw_as,
    "ON": SpecialWords.sw_on,
    "JOIN": SpecialWords.sw_join,
    "=": SpecialWords.sw_equal,
    "AND": SpecialWords.sw_and,
    "||": SpecialWords.sw_or_sticks,
    "GROUP": SpecialWords.sw_group,
    "BETWEEN": SpecialWords.sw_between,
    "BY": SpecialWords.sw_by,
    "DISTINCT": SpecialWords.sw_distinct,
    "MULTI": SpecialWords.sw_multi,
    "CREATE": SpecialWords.sw_create,
    "NULL": SpecialWords.sw_null,
    "ORDER": SpecialWords.sw_order,
    "DESC": SpecialWords.sw_desc,
    "LAG": SpecialWords.sw_window_functions,
    "ROW_NUMBER": SpecialWords.sw_window_functions,
    "CASE": SpecialWords.sw_case,
    "WHEN": SpecialWords.sw_when,
    "THEN": SpecialWords.sw_then,
    "ELSE": SpecialWords.sw_else,
    "END": SpecialWords.sw_end,
    "LEFT": SpecialWords.sw_left,
    "/*": SpecialWords.sw_open_comment,
    "NOT": SpecialWords.sw_not,
    "UNION": SpecialWords.sw_union,
    "ALL": SpecialWords.sw_all,
    ",": SpecialWords.sw_comma,
}

for function in single_parameter_functions:
    special_words[function] = SpecialWords.sw_function
