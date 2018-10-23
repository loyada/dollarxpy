from enum import Enum

from typedpy import create_typed_field


class RelationOperation(Enum):
    Exactly = ("=", " ")
    OrMore = (">=", " at least ")
    OrLess = ("<=", " at most ")

    def as_english(self):
        return self.value[1]

    def as_xpath(self):
        return self.value[0]



RelationOpField = create_typed_field("RelationOperationField", RelationOperation)