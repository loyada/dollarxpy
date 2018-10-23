from typedpy import ImmutableStructure, String, PositiveInt, Array

from dollarxpy import xpath_utils
from dollarxpy.npath import NPath
from dollarxpy.relation_operator import RelationOperation


class ElementProperty(ImmutableStructure):
    xpath = String
    text = String

    _required = ['xpath', 'text']

    def or_(self, elementProperty):
        return ElementProperty(
            xpath=f"({self} or {elementProperty})",
            text=f"({self} or {elementProperty})"
        )

    def and_(self, elementProperty):
        return ElementProperty(
            xpath=f"({self} and {elementProperty})",
            text=f"({self} and {elementProperty})"
        )

    def and_not(self, element_property):
        return self.and_(not_prop(element_property))



def not_prop(element_property):
    return ElementProperty(
        xpath=xpath_utils.does_not_exist(element_property),
        text=f"not ({element_property})")


class _ElementPropertyWithNumericalBoundaries(ElementProperty):
    n = PositiveInt

    def _create_with_relation(self, relation):
        return ElementProperty(
            xpath=f"count(./*){relation.as_xpath()}{self.n}",
            text=f"has{relation.as_english()}{self.n} children"
        )

    def or_more(self) -> ElementProperty:
        return self._create_with_relation(RelationOperation.OrMore)

    def or_less(self) -> ElementProperty:
        return self._create_with_relation(RelationOperation.OrLess)

    def exactly(self) -> ElementProperty:
        return self._create_with_relation(RelationOperation.Exactly)


