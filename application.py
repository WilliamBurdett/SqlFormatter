import re
from special_words import (
    special_words,
    SpecialWords,
    data_types,
    multi_parameter_functions,
)
from objects import LinkedList, Indent, Node, Operation, Direction
from settings import DEBUG


def get_sql(file_name: str):
    with open(file_name, "r") as file:
        return file.read()


def lower_case(linked_list: LinkedList):
    node: Node = linked_list.head
    while node is not None:
        if SpecialWords.is_table_name(linked_list, node):
            node.data = node.data.lower()
        node = node.next_node


def fix_commas(linked_list: LinkedList):
    node: Node = linked_list.head
    while node is not None:
        next_node: Node = node.next_node
        if "," in node.data and node.data[-1] != ",":
            prev_node: Node = None
            for index, split in enumerate(node.data.split(",")):
                if index == 0:
                    node.data = f"{split},"
                    prev_node = node
                elif index + 1 == len(node.data.split(",")):
                    prev_node = linked_list.insert_after(prev_node, f"{split}")
                else:
                    linked_list.insert_after(prev_node, f"{split},")
        node = next_node


def replace_comment_with_block(sql):
    lines = sql.split("\n")
    for index, line in enumerate(lines):
        if "--" in line:
            line = line.replace("--", "/* ")
            line = f"{line} */"
            lines[index] = line
    return "\n".join(lines)


def replace_single_block_comments(processed_sql: str):
    lines = processed_sql.split("\n")
    for index, line in enumerate(lines):
        if "/*" in line and "*/" in line:
            line = line.replace("/*", "--")
            line = line.replace(" */", "")
            lines[index] = line
    return "\n".join(lines)


def main(sql: str):
    sql: str = replace_comment_with_block(sql)
    tokens: list = get_tokens(sql)
    upper_case(tokens)
    linked_list: LinkedList = LinkedList()
    linked_list.build_from_array(tokens)
    lower_case(linked_list)
    fix_commas(linked_list)
    processed_sql: str = process_tokens(linked_list)
    return replace_single_block_comments(processed_sql)


def upper_case(tokens: list):
    for index in range(0, len(tokens)):
        if tokens[index].upper() in special_words.keys():
            tokens[index] = tokens[index].upper()
        elif tokens[index].upper() in data_types:
            tokens[index] = tokens[index].upper()
        elif tokens[index].upper() in multi_parameter_functions:
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
        operation = SpecialWords.get_operation(linked_list, node)

        #  Deals with nodes where we need to force an operation
        if operation.special_node is not None:
            special_nodes[operation.special_node] = indent.indent
        if node.special_operation is not None:
            special_operation = node.special_operation
            default = Operation(None)
            for variable in default.__dict__.keys():
                default_variable = getattr(default, variable)
                special_operation_variable = getattr(special_operation, variable)
                if default_variable != special_operation_variable:
                    setattr(operation, variable, getattr(special_operation, variable))
        if node in special_nodes:
            open_indent = special_nodes[node]
            indent.indent = open_indent

        # debub_linked_list.append(
        #     "\n".join(
        #         [
        #             str(f"previous_newline: {previous_newline}"),
        #             str(f"indent: {indent}"),
        #             str(f"operation: {operation}"),
        #             "node:" + str(node).replace("\n", "\\n"),
        #         ]
        #     )
        #     + "\n"
        # )
        debub_linked_list.append("\n")

        #  Preforms the actual linked list modifications based on the operation
        if no_return_node == node:
            no_return_node = None
        if no_return_node is None:
            indent.modify_indent(operation.previous_indent)
        if linked_list.get_distance_to_node(
            node, no_return_node, Direction.right()
        ) < linked_list.get_distance_to_node(
            node, operation.no_return_node, Direction.right()
        ):
            no_return_node = operation.no_return_node
        if previous_newline:
            linked_list.insert_before(node, indent.calculate_indent())
        if node.next_node is not None:
            if operation.return_after and no_return_node is None:
                linked_list.insert_after(node, "\n")
                previous_newline = True
            else:
                if operation.no_space is False or (
                    operation.no_space is None and no_return_node is not None
                ):
                    linked_list.insert_after(node, " ")
                previous_newline = False

        if no_return_node is None:
            indent.modify_indent(operation.indent_direction)
        else:
            operation.return_after = False

        # linked_list.insert_after(node, str(indent))

        node.final_operation = operation
        if no_return_node is None:
            node.no_return_status = False
        else:
            node.no_return_status = True
        node = next_node

    if DEBUG:
        print(debub_linked_list)
    return str(linked_list)


def get_tokens(sql):
    regex = r"[a-zA-Z0-9><_;\+\-\\\/\"\'\.\*\=\|]+|[,()]"
    return re.findall(regex, sql)


if __name__ == "__main__":
    print(main(get_sql("company_code/etl_dim_views.calendar.sql")))
