from enum import Enum
from re import compile

from dollarxpy.relation_operator import RelationOperation


class LogicalOp(Enum):
    AND = "and"
    OR = "or"


def _translate_text_for_path(txt: str) -> str:
    "translate(%s, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')".format(txt)


def text_contains(text: str) -> str:
    return "contains(%s, '%s')".format(_translate_text_for_path("text()"), text.lower())


def text_equals(text):
    return "%s = '%s'".format(_translate_text_for_path("text()"), text.lower())


def aggregated_text_equals(text):
    return "%s = '%s'".format(_translate_text_for_path("normalize-space(string(.))"), text.lower())


def aggregated_text_contains(text):
    return "contains(%s, '%s')".format(_translate_text_for_path("normalize-space(string(.))"), text.lower())


has_some_text = "string-length(text()) > 0"


def has_class(class_name):
    return f"contains(concat(' ', normalize-space(@class), ' '), ' {class_name} ')"


def has_class_containing(name):
    return f"contains(@class, '{name}')"


def has_classes(*class_names):
    return _has_classes_internal("and", class_names)


def has_any_of_classes(*class_names):
    return _has_classes_internal("or", class_names)


def _has_classes_internal(op: LogicalOp, *class_names):
    return f" {op.value} ".join([has_class(x) for x in class_names])


def has_id(id):
    return has_attribute("id", id)


def has_attribute(attribute, value):
    return f"@{attribute}={value}"


def does_not_exist(path: str) -> str:
    return f"not({path})"


def does_not_exist_in_entire_page(path: str) -> str:
    processed_path = f".{path}" if path.startswith("//") else \
        f"(./{path[2:]}" if path.startswith("(/") else f".//{path}"
    return f"/html[not({processed_path})]"


is_hidden = "contains(@style, 'display:none') or contains(normalize-space(@style), 'display: none')"


def n_occurrence(xpath: str, number_of_occurrences, relation_operator: RelationOperation):
    return f"[count(//{xpath}){relation_operator.as_xpath()}{str(number_of_occurrences)}]"


def inside_top_level(xpath):
    already_written_as_inside_top_level = compile("^[(]*[//]+.*").matches(xpath)
    prefix = "" if already_written_as_inside_top_level else \
        "(//" if xpath.startswith("/") else "//"
    chopn = 1 if (xpath.startswith("(") and not already_written_as_inside_top_level) else 0
    return prefix + xpath[chopn:]


def text_ends_with(suffix: str) -> str:
    return f"""substring(_translate_text_for_path("text()"), string-length(text()) - string-length('{suffix}') +1) = '{suffix.lower()}'"""


def text_starts_with(prefix: str) -> str:
    return f"""starts-with({_translate_text_for_path("text()")}, '{prefix.lower()}')"""


def aggregated_text_ends_with(suffix: str) -> str:
    return f"""substring({_translate_text_for_path("normalize-space(string(.))")}, string-length(normalize-space(string(.))) - string-length('{suffix}') +1) = '{suffix.lower()}'"""


def aggregated_text_starts_with(prefix: str) -> str:
    return f"""starts-with({_translate_text_for_path("normalize-space(string(.))")}, '{prefix.lower()}')"""
