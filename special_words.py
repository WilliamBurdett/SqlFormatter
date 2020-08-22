from objects import LinkedList, Node, Operation
from settings import debug_output





class SpecialWords:
    @staticmethod
    @debug_output
    def sw_desc(linked_list: LinkedList, node: Node):
        return Operation()

    @staticmethod
    @debug_output
    def sw_open_comment(linked_list: LinkedList, node: Node):
        close_node: Node = node.next_node
        length: int = 0
        splits: list[Node] = list()
        while close_node.data != "*/":
            if length > 20:
                splits.append(close_node)
                length = 0
            length += len(close_node.data)
            close_node.special_operation = Operation(return_after=False)
            close_node = close_node.next_node
        close_node.prev_node_original.special_operation = None
        for split in splits:
            split.special_operation = Operation()
        return Operation()

    @staticmethod
    @debug_output
    def sw_left(linked_list: LinkedList, node: Node):
        if node.next_node.data == "JOIN":
            return Operation(return_after=False, previous_indent=-1, indent_direction=1)
        return SpecialWords.all_others(linked_list, node)

    @staticmethod
    @debug_output
    def sw_case(linked_list: LinkedList, node: Node):
        close_node, length, max_skip = SpecialWords.get_close_node(node, "CASE", "END")
        if close_node is None:
            raise Exception("Couldn't find END node")
        if linked_list.get_distance_to_data(node, "WHEN", 1) == 1:
            if length > 10:
                close_node.special_operation = Operation()
                return Operation(indent_direction=1, special_node=close_node)
            else:
                return Operation(return_after=False)
        else:
            raise NotImplemented("Case followed by an expression")

    @staticmethod
    @debug_output
    def sw_when(linked_list: LinkedList, node: Node):
        no_return_node = node.next_node
        while no_return_node.next_node.data != "THEN":
            no_return_node = no_return_node.next_node
        return Operation(return_after=False, no_return_node=no_return_node)

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
        return Operation(return_after=False, no_return_node=no_return_node)

    @staticmethod
    @debug_output
    def sw_else(linked_list: LinkedList, node: Node):
        no_return_node = node.next_node
        while no_return_node.next_node.data != "END":
            no_return_node = no_return_node.next_node
        return Operation(return_after=False, no_return_node=no_return_node)

    @staticmethod
    @debug_output
    def sw_end(linked_list: LinkedList, node: Node):
        if node.next_node.data == "AS":
            no_return_node = node.next_node.next_node
            return Operation(return_after=False, no_return_node=no_return_node)
        elif node.next_node.data == "AND":
            return Operation(indent_direction=-1)
        else:
            return Operation()

    @staticmethod
    @debug_output
    def sw_window_functions(linked_list: LinkedList, node: Node):
        as_node = node
        while as_node.data != "AS":
            as_node = as_node.next_node
        return Operation(no_return_node=as_node, no_space=True)

    @staticmethod
    @debug_output
    def sw_distinct(linked_list: LinkedList, node: Node):
        return Operation(indent_direction=1)

    @staticmethod
    @debug_output
    def sw_order(linked_list: LinkedList, node: Node):
        return Operation(previous_indent=-1, return_after=False, indent_direction=1)

    @staticmethod
    @debug_output
    def sw_null(linked_list: LinkedList, node: Node):
        return Operation()

    @staticmethod
    @debug_output
    def sw_create(linked_list: LinkedList, node: Node):
        as_node = node
        while as_node.data != "AS":
            as_node = as_node.next_node
        return Operation(no_return_node=as_node)

    @staticmethod
    @debug_output
    def sw_or_sticks(linked_list: LinkedList, node: Node):
        return Operation(previous_indent=1, return_after=False, indent_direction=-1)

    @staticmethod
    @debug_output
    def sw_between(linked_list: LinkedList, node: Node):
        close_node: Node = node
        distance = 0
        while distance != 2:
            distance += 1
            close_node = close_node.next_node
        return Operation(return_after=False, no_return_node=close_node)

    @staticmethod
    @debug_output
    def sw_by(linked_list: LinkedList, node: Node):
        if linked_list.get_distance_to_data(node, "GROUP", -1) == 1:
            return Operation(indent_direction=1)
        return SpecialWords.all_others(linked_list, node)

    @staticmethod
    @debug_output
    def sw_group(linked_list: LinkedList, node: Node):
        return_after: bool = True
        if linked_list.get_distance_to_data(node, "BY", 1) == 1:
            return_after = False
        return Operation(previous_indent=-1, return_after=return_after)

    @staticmethod
    @debug_output
    def sw_equal(linked_list: LinkedList, node: Node):
        return Operation(return_after=False)

    @staticmethod
    @debug_output
    def sw_and(linked_list: LinkedList, node: Node):
        if node.next_node.data == "CASE":
            return Operation(indent_direction=1)
        return Operation(return_after=False)

    @staticmethod
    @debug_output
    def sw_on(linked_list: LinkedList, node: Node):
        no_return_node = node
        while not SpecialWords.end_of_equality(linked_list, no_return_node):
            no_return_node = no_return_node.next_node
        if no_return_node == node or node.next_node.data == "(":
            return Operation(return_after=False)
        return Operation(return_after=False, no_return_node=no_return_node)

    @staticmethod
    @debug_output
    def sw_join(linked_list: LinkedList, node: Node):
        if SpecialWords.is_alias(linked_list, node.next_node.next_node):
            no_return_node = node.next_node.next_node
            return Operation(
                return_after=False, previous_indent=-1, no_return_node=no_return_node,
            )
        return Operation(
            return_after=False, previous_indent=-1, no_return_node=node.next_node
        )

    @staticmethod
    @debug_output
    def sw_function(linked_list: LinkedList, node: Node):
        return Operation(return_after=False, no_space=True)

    @staticmethod
    @debug_output
    def all_others(linked_list: LinkedList, node: Node):
        if SpecialWords.is_in_block_comment(linked_list, node):
            return Operation()
        if SpecialWords.end_of_simple_select(linked_list, node):
            return Operation(indent_direction=-1, return_after=True)
        if SpecialWords.inside_simple_select(linked_list, node):
            return Operation(return_after=False)
        if SpecialWords.is_alias(linked_list, node):
            if linked_list.get_distance_to_data(node, "ON", 1) == 1:
                return Operation(indent_direction=1)
            if linked_list.get_distance_to_data(node, "ORDER", 1) == 1:
                return Operation()
            if linked_list.get_distance_to_data(node, "JOIN", 1) == 1:
                return Operation()
            return Operation(return_after=False)
        if SpecialWords.is_table_name(linked_list, node):
            if node.next_node is not None:
                if SpecialWords.is_alias(linked_list, node.next_node):
                    return Operation(return_after=False)
        if SpecialWords.part_of_equality(linked_list, node):
            if 1 in [
                linked_list.get_distance_to_data(node, mid, -1)
                for mid in equality_options
            ]:
                return Operation()
            if 1 in [
                linked_list.get_distance_to_data(node, mid, 1)
                for mid in equality_options
            ]:
                return Operation(return_after=False)
        open_distance = linked_list.get_distance_to_data(node, "(", -1)
        close_distance = linked_list.get_distance_to_data(node, ")", 1)
        if open_distance == 1 and close_distance == 1:
            return Operation(return_after=False, no_space=True)
        elif close_distance == 1:
            if node.next_node.next_node.data == ",":
                return Operation()
            return Operation(return_after=False, no_space=True)
        if linked_list.get_distance_to_data(node, "AS", 1) == 1:
            return Operation(return_after=False)
        if linked_list.get_distance_to_data(node, "BETWEEN", 1) == 1:
            return Operation(return_after=False)
        if linked_list.get_distance_to_data(node, "||", 1) == 1:
            return Operation(return_after=False)
        return Operation()

    @staticmethod
    @debug_output
    def sw_with(linked_list: LinkedList, node: Node):
        if SpecialWords.is_alias(linked_list, node.next_node):
            return Operation(return_after=False)
        return Operation(indent_direction=1)

    @staticmethod
    @debug_output
    def sw_open_parenthesis(linked_list: LinkedList, node: Node):
        close_node, length, max_skip = SpecialWords.get_close_node(node, "(", ")")
        if SpecialWords.inside_simple_select(linked_list, node.next_node):
            return Operation(indent_direction=1)
        if linked_list.get_distance_to_node(node, close_node, 1) == 2:
            return Operation(return_after=False, no_space=True)
        if node.next_node.data in single_parameter_functions:
            return Operation(return_after=False, no_space=True)
        if node.prev_node_original.data in multi_parameter_functions:
            return Operation(return_after=False, no_space=True)
        if length < 70:
            return Operation(
                return_after=False, no_return_node=close_node, no_space=True
            )
        else:
            close_node.special_operation = Operation()
            return Operation(indent_direction=1, special_node=close_node)
        return Operation(indent_direction=1)

    @staticmethod
    @debug_output
    def get_close_node(node, skip_data, target_data):
        close_node: Node = node.next_node
        to_skip: int = 0
        max_skip: int = 0
        length: int = 0
        while close_node is not None:
            length += len(close_node.data)
            if close_node.data == skip_data:
                to_skip += 1
                if max_skip < to_skip:
                    max_skip = to_skip
            if close_node.data == target_data:
                if to_skip >= 1:
                    to_skip -= 1
                else:
                    break
            close_node = close_node.next_node
        return close_node, length, max_skip

    @staticmethod
    @debug_output
    def sw_close_parenthesis(linked_list: LinkedList, node: Node):
        if node.next_node is not None:
            if node.next_node.next_node.data == ",":
                return Operation()
            if node.next_node.data == ",":
                return Operation(return_after=False, no_space=True)
            if linked_list.get_distance_to_data(node, "AS", 1) == 1:
                return Operation(return_after=False)
            if linked_list.get_distance_to_data(node, ")", 1) == 1:
                return Operation(return_after=False, no_space=True)
            if node.next_node is not None and SpecialWords.is_alias(
                linked_list, node.next_node
            ):
                return Operation(return_after=False)
            if linked_list.get_distance_to_data(node, "(", -1) == 2:
                return Operation(return_after=False)
            if node.next_node.data == "||":
                return Operation(return_after=False)
        return Operation()

    @staticmethod
    @debug_output
    def sw_as(linked_list: LinkedList, node: Node):
        distances = [
            linked_list.get_distance_to_data(node, "SELECT", 1),
            linked_list.get_distance_to_data(node, "WITH", 1),
        ]
        if 1 in distances:
            return Operation(indent_direction=1)
        return Operation(return_after=False)

    @staticmethod
    @debug_output
    def sw_select(linked_list: LinkedList, node: Node):
        from_distance = linked_list.get_distance_to_data(node, "FROM", 1)
        join_next = linked_list.get_distance_to_data(node, "JOIN", 1)
        if from_distance == 2 and join_next != 4:
            return Operation(return_after=False)
        if linked_list.get_distance_to_data(node, "DISTINCT", 1) == 1:
            return Operation(return_after=False)
        return Operation(indent_direction=1)

    @staticmethod
    @debug_output
    def sw_from(linked_list: LinkedList, node: Node):
        if SpecialWords.inside_simple_select(linked_list, node):
            return Operation(return_after=False)
        return Operation(indent_direction=1, previous_indent=-1)

    @staticmethod
    @debug_output
    def sw_where(linked_list: LinkedList, node: Node):
        return Operation(indent_direction=1, previous_indent=-1)

    @staticmethod
    @debug_output
    def sw_multi(linked_list: LinkedList, node: Node, parameter_count: int):
        close_node = node
        while close_node.data != ")":
            close_node = close_node.next_node
        if parameter_count == 2:
            return Operation(
                return_after=False, no_return_node=close_node, no_space=True
            )
        elif parameter_count == 3:
            return Operation()

    @staticmethod
    @debug_output
    def inside_simple_select(linked_list: LinkedList, node: Node):
        temp_node = node
        while temp_node is not None:
            if temp_node.data == "SELECT":
                from_distance = linked_list.get_distance_to_data(temp_node, "FROM", 1)
                join_next = linked_list.get_distance_to_data(temp_node, "JOIN", 1)
                if from_distance == 2 and join_next != 4 and join_next != 5:
                    return True
                else:
                    return False
            temp_node = temp_node.prev_node
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
        if node.data == 'here':
            print('')
        left_open = linked_list.get_distance_to_data(node, '/*', -1)
        left_close = linked_list.get_distance_to_data(node, '*/', -1)
        right_open = linked_list.get_distance_to_data(node, '/*', 1)
        right_close = linked_list.get_distance_to_data(node, '*/', 1)
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
}

for function in single_parameter_functions:
    special_words[function] = SpecialWords.sw_function
