from dollarxpy.basic_path import (
        BasicPath, not_, custom_element, child_number, occurrence_number, first_occurrence_of, last_occurrence_of,
        anything_except
    )

from dollarxpy.elements import *

from dollarxpy.element_property import ElementProperty

from dollarxpy.element_properties import (
        has_some_text, has_class, has_any_of_classes, has_attribute, has_aggregated_text_containing, has_aggregated_text_ending_with,
        has_aggregated_text_equal_to, has_aggregated_text_starting_with, has_ancestor, has_child, has_children, has_class_containing,
        has_classes, has_descendant, has_id, has_n_children, has_name, has_no_children, has_none_of_the_classes, has_parent, has_raw_xpath_property,
        has_role, has_text, has_text_containing, has_text_ending_with, has_text_starting_with, is_inside, is_after, is_after_sibling, is_ancestor_of, is_before,
        is_before_sibling, is_child_of, is_contained_in, is_descendant_of, is_hidden_with_inline_styling, is_last_sibling, is_nth_from_last_sibling,
        is_nth_sibling, is_only_child, is_parent_of, is_sibling_of, is_with_index, contains, with_index_in_range, not_, not_prop
)