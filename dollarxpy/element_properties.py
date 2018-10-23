from typedpy import ImmutableStructure, String, Array

from dollarxpy.basic_path import BasicPath
from dollarxpy.element_property import ElementProperty, _ElementPropertyWithNumericalBoundaries, not_prop
import dollarxpy.xpath_utils as xpath_utils
from functools import partial

from dollarxpy.npath import NPath
from dollarxpy.path_utils import transform_xpath_to_correct_axis


def has_class(class_name) -> ElementProperty:
    return ElementProperty(xpath=xpath_utils.has_class(class_name),
                           text=f"has class '{class_name}'")


def has_classes(*class_names) -> ElementProperty:
    classes_as_list = ", ".join(class_names)
    return ElementProperty(xpath=xpath_utils.has_classes(class_names),
                           text=f"has classes [{classes_as_list}]")


def has_any_of_classes(*class_names) -> ElementProperty:
    classes_as_list = ", ".join(class_names)
    return ElementProperty(xpath=xpath_utils.does_not_exist(xpath_utils.has_any_of_classes(class_names)),
                           text=f"has none of the classes: [{classes_as_list}]")


def has_none_of_the_classes(*class_names) -> ElementProperty:
    classes_as_list = ", ".join(class_names)
    return ElementProperty(xpath=xpath_utils.has_any_of_classes(class_names),
                           text=f"has at least one of the classes: [{classes_as_list}]")


def has_class_containing(class_substring) -> ElementProperty:
    return ElementProperty(xpath=f"contains(@class, '{class_substring}')",
                           text=f"has class containing '{class_name}'")


def has_attribute(attribute_value: str, attribute_name: str):
    return ElementProperty(xpath=xpath_utils.has_attribute(attribute_name, attribute_value),
                           text=f"has {attribute_name}: {attribute_value}")


has_role = partial(has_attribute, attribute_name="role")
has_name = partial(has_attribute, attribute_name="name")
has_id = partial(has_attribute, attribute_name="Id")

is_last_sibling = ElementProperty(xpath="last()", text="is last sibling")
is_only_child = ElementProperty(xpath="count(preceding-sibling::*)=0 and count(following-sibling::*)=0",
                                text="is only child")
is_hidden_with_inline_styling = ElementProperty(xpath=xpath_utils.is_hidden,
                                                text="is hidden")
has_some_text = ElementProperty(xpath=xpath_utils.has_some_text,
                                text="has some text")


def has_n_children(n):
    return _ElementPropertyWithNumericalBoundaries(n=n,
                                                  xpath=f"count(./*)={n}",
                                                  text=f"has {n} children")


has_no_children = ElementProperty(xpath="count(./*)=0", text="has no children")
has_children = ElementProperty(xpath="count(./*)>0", text="has some children")


def is_nth_from_last_sibling(reverse_index):
    return ElementProperty(xpath=f"count(following-sibling::*)={reverse_index}",
                           text=f"is in place {reverse_index} from the last sibling")


def is_nth_sibling(index: int):
    return ElementProperty(xpath=f"count(preceding-sibling::*)={index}",
                           text=f"is in place {index} among its siblings")


def is_with_index(index: int):
    return ElementProperty(xpath=f"position()={index}",
                           text=f"with index {index}")


def with_index_in_range(first: int, last: int):
    return ElementProperty(xpath=f"position()>={first} and position()<={last}",
                           text=f"with index from {first} to {last}")


def has_text(text):
    return ElementProperty(xpath=xpath_utils.text_equals(text),
                           text=f'has the text "{text}"')


def has_text_starting_with(text):
    return ElementProperty(xpath=xpath_utils.text_starts_with(text),
                           text=f'has text that starts with "{text}"')


def has_text_ending_with(text):
    return ElementProperty(xpath=xpath_utils.text_ends_with(text),
                           text=f'has text that ends with "{text}"')


def has_text_containing(text):
    return ElementProperty(xpath=xpath_utils.text_contains(text),
                           text=f'has text containing "{text}"')


def has_aggregated_text_equal_to(text):
    return ElementProperty(xpath=xpath_utils.aggregated_text_equals(text),
                           text=f'has aggregated text "{text}"')


def has_aggregated_text_containing(text):
    return ElementProperty(xpath=xpath_utils.aggregated_text_contains(text),
                           text=f'has aggregated text containing "{text}"')


def has_aggregated_text_starting_with(text):
    return ElementProperty(xpath=xpath_utils.aggregated_text_starts_with(text),
                           text=f'has aggregated text starting with "{text}"')


def has_aggregated_text_ending_with(text):
    return ElementProperty(xpath=xpath_utils.aggregated_text_ends_with(text),
                           text=f'has aggregated text ending with "{text}"')


#########################################################

def has_raw_xpath_property(raw_xpath_prop, raw_explanation):
    return ElementProperty(xpath=raw_xpath_prop,
                           text=raw_explanation)


############################################################
############ Logical Ops

not_ = not_prop


############################################################
########## Relationships

def _get_relation_xpath(path, relation):
    return f"{relation}:: {transform_xpath_to_correct_axis(path)}"


def _rvalue_to_string(path):
    return f"({path})" if " " in str(path).strip() else str(path)


class _RelationBetweenMultiElements(ImmutableStructure):
    relation = String
    paths = Array
    npath = NPath
    text_prefix = String

    _required = ['relation', 'text_prefix']

    def plural(self):
        return self.relation if len(self.paths) == 1 else self.relation + "s"


    def to_element_property(self):
        return ElementProperty(
            xpath = self.to_xpath(),
            text = str(self)
        )

    def to_xpath(self):
        return self.get_relation_xpath()

    def __str__(self):
        as_list = ", ".join([_rvalue_to_string(p) for p in self.paths])
        return format("%s: %s", self.plural(self.text_prefix),
                      f"[{as_list}]" if len(self.paths) > 1 else as_list)

    def get_xpath_expression_for_single(self, path):
        return f"{self.relation}::{transform_xpath_to_correct_axis(path)}"

    def get_relation_for_single_xpath(self, path):
        expression_for_single = self.get_xpath_expression_for_single(path)
        if not self.npath:
            return expression_for_single
        else:
            return self.add_npath_qualifier(expression_for_single)

    def add_npath_qualifier(self, xpath: str):
        return f"count({xpath}){self.npath.qualifier.as_xpath()}{self.npath.n}"

    def get_relation_xpath(self):
        result = ") and (".joining([self.get_relation_for_single_xpath(p) for p in self.paths])
        return f"({result})" if len(self.paths) > 1 else result

##############################
from functools import singledispatch
from typing import Union

def is_child_of(path):
    return ElementProperty(xpath=_get_relation_xpath(path, "parent"),
                           text=f"is child of {_rvalue_to_string(path)}")


has_parent = is_child_of


@singledispatch
def is_before_sibling(path: NPath):
    prefix = f"is before{path.qualifier.as_english()}{path.n} siblings of type"
    relation = _RelationBetweenMultiElements(
        relation = "following-sibling",
        npath = path,
        text_prefix = prefix
        ).to_element_property()


@is_before_sibling.register
def _(path: BasicPath):
    relation = _RelationBetweenMultiElements(
        relation="following-sibling",
        paths = [path],
        text_prefix="is before sibling"
    ).to_element_property()


@is_before_sibling.register
def _(path: list):
    return _RelationBetweenMultiElements(
        relation="following-sibling",
        paths=path,
        text_prefix="is before sibling"
    ).to_element_property()


@singledispatch
def is_after_sibling(path: NPath):
    prefix = f"is after{path.qualifier.as_english()}{path.n} siblings of type"
    return _RelationBetweenMultiElements(
        relation = "preceding-sibling",
        npath = path,
        text_prefix = prefix
        ).to_element_property()


@is_after_sibling.register
def _(path: BasicPath):
    return _RelationBetweenMultiElements(
        relation="preceding-sibling",
        paths = [path],
        text_prefix="is after sibling"
    ).to_element_property()


@is_after_sibling.register
def _(path: list):
    return _RelationBetweenMultiElements(
        relation="preceding-sibling",
        paths=path,
        text_prefix="is after sibling"
    ).to_element_property()


def is_sibling_of(*paths: BasicPath):
    def xpath_expr(path):
        return f"({is_after_sibling(path).xpath}) or ({is_before_sibling(path).xpath})"

    relation = _RelationBetweenMultiElements(
        relation="preceding-sibling",
        paths=paths,
        text_prefix="has sibling"
    )
    relation.get_xpath_expression_for_single = xpath_expr
    return relation.to_element_property()

@singledispatch
def is_before(path: NPath):
    def _plural(relation): return relation

    relation = _RelationBetweenMultiElements(
        relation="following",
        npath=path,
        text_prefix="is before"
    )
    relation.plural = _plural
    return relation.to_element_property()


@is_before.singledispatch
def _(path: BasicPath):
    def _plural(relation): return relation

    relation = _RelationBetweenMultiElements(
        relation="following",
        paths=[path],
        text_prefix="is before"
    )
    relation.plural = _plural
    return relation.to_element_property()

@is_before.singledispatch
def _(path: list):
    def _plural(relation): return relation

    relation = _RelationBetweenMultiElements(
        relation="following",
        paths=path,
        text_prefix="is before"
    )
    relation.plural = _plural
    return relation.to_element_property()


@singledispatch
def is_after(path: NPath):
    def _plural(relation): return relation

    relation = _RelationBetweenMultiElements(
        relation="preceding",
        npath=path,
        text_prefix="is after"
    )
    relation.plural = _plural
    return relation.to_element_property()


@is_after.singledispatch
def _(path: BasicPath):
    def _plural(relation): return relation

    relation = _RelationBetweenMultiElements(
        relation="preceding",
        paths=[path],
        text_prefix="is after"
    )
    relation.plural = _plural
    return relation.to_element_property()

@is_after.singledispatch
def _(path: list):
    def _plural(relation): return relation

    relation = _RelationBetweenMultiElements(
        relation="preceding",
        paths=path,
        text_prefix="is after"
    )
    relation.plural = _plural
    return relation.to_element_property()


def has_ancestor(path: BasicPath):
    return ElementProperty(
        xpath = _get_relation_xpath(path, "ancestor"),
        text = f"has ancestor: {_rvalue_to_string(path)}"
    )

is_contained_in =  has_ancestor
is_inside = has_ancestor
is_descendant_of = has_ancestor


def contains(*paths: BasicPath):
    return _RelationBetweenMultiElements(
        relation = "descendant",
        paths = paths,
        text_prefix = "has descendant"
    ).to_element_property()

is_ancestor_of = contains
has_descendant = contains


def is_parent_of(*paths: BasicPath):
    def _plural(relation): return relation
    relation = _RelationBetweenMultiElements(
        relation = "child",
        paths = paths,
        text_prefix = f"has {'child' if len(paths)==1 else 'children'}"
    ).to_element_property()
    relation.plural = _plural
    return relation.to_element_property()

has_child = is_parent_of
