
def has_heirarchy(xpath) -> object:
    return '/' in xpath


def transform_xpath_to_correct_axis(source_path) -> str:
    return source_path.get_alternate_xpath() if has_heirarchy(source_path.get_xpath()) else source_path.get_xpath()


def opposite_relation(relation: str):
    opposite_relations = {
        'parent': 'child',
        'ancestor': 'descendant',
        'following': 'preceding',
        'self': 'self',
        'ancestor-or-self': 'descendant-or-self',
        'following-sibling': 'preceding-sibling',
    }

    reverse_relations = dict([(value, key) for key, value  in opposite_relations.items()])
    opposite_relations.update(reverse_relations)
    return opposite_relations[relation]

