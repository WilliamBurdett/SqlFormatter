import re
from special_words import (
    special_words, SpecialWords, data_types, multi_parameter_functions
)
from objects import LinkedList, Indent, Node, Operation
from settings import DEBUG


# CREATE OR REPLACE VIEW etl_fact_views.product_actions_by_user_school_article_week AS
def get_sql(file_name: str):
    with open(file_name, 'r') as file:
        return file.read()


def lower_case(linked_list: LinkedList):
    node: Node = linked_list.head
    while node is not None:
        if SpecialWords.is_table_name(linked_list, node):
            node.data = node.data.lower()
        node = node.next_node


def main(sql: str):
    tokens: list = get_tokens(sql)
    upper_case(tokens)
    linked_list: LinkedList = LinkedList()
    linked_list.build_from_array(tokens)
    lower_case(linked_list)
    return process_tokens(linked_list)


def upper_case(tokens: list):
    for index in range(0, len(tokens)):
        if tokens[index].upper() in special_words.keys():
            tokens[index] = tokens[index].upper()
        elif tokens[index].upper() in data_types:
            tokens[index] = tokens[index].upper()
        elif tokens[index].upper() in multi_parameter_functions.keys():
            tokens[index] = tokens[index].upper()
    return tokens


def process_tokens(linked_list: LinkedList):
    indent: Indent = Indent()
    previous_newline: bool = False
    node: Node = linked_list.head
    debub_linked_list: LinkedList = LinkedList()
    no_return_node: Node = node
    special_nodes: dict = {}
    while node is not None:
        if DEBUG:
            print(node)
        next_node = node.next_node
        if node.data in special_words.keys():
            operation = special_words[node.data](linked_list, node)
        elif node.data in multi_parameter_functions.keys():
            parameter_count = multi_parameter_functions[node.data]
            operation = special_words['MULTI'](linked_list, node, parameter_count)
        else:
            operation = special_words["ALL-OTHERS"](linked_list, node)

        #  Deals with nodes where we need to force an operation
        if operation.special_node is not None:
            special_nodes[operation.special_node] = {
                "operation": operation.special_operation,
                "open_indent": indent.indent,
            }

        if node in special_nodes.keys():
            special_operation = special_nodes[node]["operation"]
            default = Operation()
            for variable in default.__dict__.keys():
                default_variable = getattr(default, variable)
                special_operation_variable = getattr(special_operation, variable)
                if default_variable != special_operation_variable:
                    setattr(operation, variable, getattr(special_operation, variable))
                open_indent = special_nodes[node]["open_indent"]
                indent.indent = open_indent

        debub_linked_list.append(
            '\n'.join([
                str(f'previous_newline: {previous_newline}'),
                str(f'indent: {indent}'),
                str(f'operation: {operation}'),
                'node:' + str(node).replace('\n', '\\n')
            ]) +
            '\n'
        )
        debub_linked_list.append('\n')

        #  Preforms the actual linked list modifications based on the operation
        indent.modify_indent(operation.previous_indent)
        if (linked_list.get_distance_to_node(node, no_return_node, 1) <
                linked_list.get_distance_to_node(node, operation.no_return_node, 1)):
            no_return_node = operation.no_return_node
        if no_return_node == node:
            no_return_node = None
        if previous_newline:
            linked_list.insert_before(node, indent.calculate_indent())
        if node.next_node is not None:
            if operation.return_after and no_return_node is None:
                linked_list.insert_after(node, "\n")
                previous_newline = True
            else:
                if operation.no_space is False:
                    linked_list.insert_after(node, " ")
                previous_newline = False
        indent.modify_indent(operation.indent_direction)

        node = next_node

    if DEBUG:
        print(debub_linked_list)
    return str(linked_list)


def get_tokens(sql):
    regex = r"[a-zA-Z0-9,\"\'\._\*\=\|]+|[()]"
    return re.findall(regex, sql)


if __name__ == "__main__":
    print(main(get_sql('tests/test_3_input.sql')))
