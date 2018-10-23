from typedpy import ImmutableStructure, String, Array, Integer, Tuple
from selenium import webdriver
from __future__ import annotations


from dollarxpy.element_property import ElementProperty
from dollarxpy.path_utils import has_heirarchy, opposite_relation, transform_xpath_to_correct_axis
import dollarxpy.xpath_utils as xpath_utils

class BasicPath(ImmutableStructure):
    inside_xpath = String
    xpath = String(minLength=1)
    alternate_xpath = String
    xpath_explanation = String
    described_by = String
    element_properties = Tuple[ElementProperty]

    _required = ['xpath']

    def or_(self, other: BasicPath) -> BasicPath:
        self._verify_relationship_between_elements(other)
        return BasicPath(xpath = f'*[self::{transform_xpath_to_correct_axis(self)}] | [self::{transform_xpath_to_correct_axis(path)}]')

    def and_(self, *props) -> BasicPath:
        return self.that(props)

    def described_by(self, description) -> BasicPath:
        return BasicPath(xpath=self.xpath,
                         inside_path=self.inside_path,
                         alternate_path=self.alternate_xpath,
                         described_by=description,
                         element_properties=self.element_properties)

    def _verify_relationship_between_elements(self, other: BasicPath):
        if not self.get_xpath() or not other.get_xpath():
            raise ValueError()

    def with_global_index(self, n: int) -> BasicPath:
        return BasicPath.occurrence_number(n + 1).of(self)

    def that(self, *props) -> BasicPath:
        if (self.described_by):
            return BasicPath(xpath=self._get_xpath_without_inside_claus(),
                             inside_xpath=self.inside_xpath,
                             element_properties=tuple(props),
                             alternate_xpath=self.alternate_xpath,
                             xpath_explanation=self.described_by)
        else:
            return BasicPath(xpath=self.xpath,
                             inside_xpath=self.inside_xpath,
                             element_properties=(*self.element_properties, *props),
                             alternate_xpath=self.alternate_xpath,
                             xpath_explanation=self.described_by)

    def get_xpath(self) -> String:
        proccessed_xpath = (self.inside_xpath + '//' if self.inside_xpath else "") + self.xpath
        props = ''.join([f'[{x.to_xpath()}]' for x in self.element_properties])
        return proccessed_xpath + props

    def get_alternate_xpath(self) -> String:
        props = ''.join([f'[{x.to_xpath()}]' for x in self.element_properties])
        return (self.alternate_xpath or "*") + props


    def _get_xpath_without_inside_claus(self):
        props = ''.join([f'[{x.to_xpath()}]' for x in self.element_properties])
        return (self.xpath or "*") + props


    def inside_top_level(self) -> BasicPath:
        return BasicPath(xpath = xpath_utils.inside_top_level(self.get_xpath()),
                         described_by = str(self))


    def after_sibling(self, path: BasicPath) -> BasicPath:
        return self._create_with_relation(path, "following-sibling", human_readable_relation = "after the sibling")


    def after(self, path: BasicPath) -> BasicPath:
        return self._create_with_relation(path, "following", human_readable_relation="after")

    def before_sibling(self, path: BasicPath) -> BasicPath:
        return self._create_with_relation(path, "preceding-sibling", human_readable_relation = "before the sibling")

    def before(self, path: BasicPath) -> BasicPath:
        return self._create_with_relation(path, "preceding", human_readable_relation="before")

    def child_of(self, path: BasicPath) -> BasicPath:
        return self._create_with_relation(path, "parent")

    def containing(self, path: BasicPath) -> BasicPath:
        return self.ancestor_of(path)


    def contains(self, path: BasicPath) -> BasicPath:
        return self.ancestor_of(path)

    def ancestor_of(self, path: BasicPath) -> BasicPath:
        return self._create_with_relation(path, "ancestor")

    def descendant_of(self, path: BasicPath) -> BasicPath:
        return self._create_with_relation(path, "descendant")

    def with_class(self, css_class):
        return self._create_new_with_additional_property()

    def _create_new_with_additional_property(self, prop):
        if self.described_by:
            return BasicPath(xpath = self.get_xpath(),
                             alternate_xpath = self.get_alternate_xpath(),
                             inside_xpath = self.inside_xpath,
                             element_properties = (self.prop,),
                             xpath_explanation = self.described_by)
        else:
            new_props = *self.element_properties, prop
            return BasicPath(xpath = self.xpath,
                             alternate_xpath = self.get_alternate_xpath(),
                             element_properties = new_props,
                             inside_xpath = self.inside_xpath,
                             xpath_explanation = self.xpath_explanation)


    def _create_with_relation(self, path: BasicPath, xpath_relation: str, human_readable_relation: str = None):
        self._verify_relationship_between_elements(path)
        my_xpath = self.get_xpath()
        is_inside = bool(self.inside_xpath)
        processed_xpath = f'{self._get_xpath_without_inside_claus()}[ancestor::{self.inside_xpath}]' if is_inside else my_xpath
        new_alternate_xpath = self.get_alternate_xpath() + \
                              f'[{opposite_relation(xpath_relation)}::{path.get_alternate_xpath()}]'
        use_alternate_xpath = has_heirarchy(processed_xpath)
        new_xpath  = new_alternate_xpath if use_alternate_xpath else \
            f'{path.get_xpath()}/{xpath_relation}::{processed_xpath}'
        relation_as_text = human_readable_relation if human_readable_relation else xpath_relation
        return BasicPath(xpath = new_xpath,
                         alternate_xpath = new_alternate_xpath,
                         xpath_explanation = f'{str(self)},{relation_as_text} {_wrap_if_needed(path)}')


    def _get_xpath_explanation_for_str(self) -> str:
        return self.xpath_explanation if self.xpath_explanation else f"xpath: \"{xpath}\""

    def _get_properties_to_string_for_length1(self):
        first_prop_description = str(self.element_properties[0])
        that_maybe = "that " if (first_prop_description.startswith("has") or first_prop_description.startswith("is")) else ""
        return that_maybe + first_prop_description

    def _get_properties_to_string_for_length_larger_than_2(self):
        props_as_list: str = ", ".join([str(p) for p in self.element_properties])
        if (self.xpath_explanation and "with properties" in self.xpath_explanation) or self.element_properties==1:
            return f"and {props_as_list}"
        else:
            return f"that [{props_as_list}]"


    def __str__(self):
        if self.described_by and self.described_by != self.xpath_explanation:
            return self.described_by
        else:
            xpath = self._get_xpath_explanation_for_str()

            use_length_1 = self.element_properties and len(self.element_properties)==1 and (", " not in xpath or xpath==self.described_by)
            use_that_and = self.element_properties and len(self.element_properties==2) and " " not in xpath
            use_larger_format_than_2 = (self.element_properties and len(self.element_properties)>1) or \
                                       (" " in xpath and self.element_properties)
            props = self._get_properties_to_string_for_length1() if use_length_1 else \
                f"that {self.elementProperties[0]}, and {self.element_properties[-1]}" if use_that_and else \
                    self._get_properties_to_string_for_length_larger_than_2() if use_larger_format_than_2 else ""






class ChildNumber(ImmutableStructure):
    n = Integer(minimum=1)

    def of_type(self, path: BasicPath) -> BasicPath:
        new_xpath = f'{path.get_xpath()}[{self.n}]'
        alternate_xpath = f'{path.get_alternate_xpath()}[{self.n}]'
        return BasicPath(xpath=new_xpath, alternate_xpath=alternate_xpath,
                         xpath_explanation=f'child number {n} of type {path}')


class GlobalOccurrenceNumber(ImmutableStructure):
    n = Integer(minimum=0)

    def of(self, path: BasicPath) -> BasicPath:
        prefix = 'the first occurrence of ' if self.n == 1 \
            else 'the last occurrence of ' if self.n == 0 \
            else f'occurrence number {self.n}'
        path_st = path.__str__()
        wrapped = f'({path_st})' if " " in path_st else path_st
        index = 'last()' if self.n == 0 else f'{self.n}'
        xpath_prefix = '(' if path.get_xpath().startswidth('(') else '(//'
        new_xpath = f'{xpath_prefix}{path.get_xpath()})[{index}]'
        new_alternate_xpath = f'{xpath_prefix}{path.get_alternative_xpath()})[{index}]'
        return BasicPath(xpath=new_xpath,
                         alternate_xpath=new_alternate_xpath,
                         xpath_explanation=prefix + wrapped)


#  functions

def not_(path: BasicPath):
    return BasicPath(
        xpath = f"*[not(self::{transform_xpath_to_correct_axis(path)})]",
        alternate_xpath = f"*[not(self::{path.get_alternate_xpath()})]",
        xpath_explanation = f"anything except ({path})"
    )


def _wrap_if_needed(path:BasicPath) -> str:
        path_st = str(path)
        return f'({path_st})' if ' ' in path_st.strip() else path_st


def custom_element(xpath):
    return BasicPath(xpath=xpath, xpath_explanation=xpath)


def child_number(n: int) -> BasicPath.ChildNumber:
    return BasicPath.ChildNumber(n)


def occurrence_number(n: int) -> BasicPath.GlobalOccurrenceNumber:
    return BasicPath.GlobalOccurrenceNumber(n)


def first_occurrence_of(path: BasicPath):
    return path.occurrence_number(0)


def last_occurrence_of(path: BasicPath):
    return path.occurrence_number(-1)

def anything_except(path: BasicPath) -> BasicPath:
    transformed_xpath = transform_xpath_to_correct_axis(path)
    return BasicPath(xpath = f"*[not(self::{transformed_xpath})]",
                     alternate_xpath = f"*[not(self::{path.get_alternate_xpath()})]",
                     xpath_explanation = f"anything except ({str(path)})"
                     )

#########################################
