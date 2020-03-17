"""

"""


class Entity:
    """

    """

    def __init__(self, sentence_num, token_begin, token_end, text, ner):
        self.sentence_num = sentence_num
        self.token_begin = token_begin
        self.token_end = token_end
        self.text = text
        self.ner = ner
        self.coref = []
        self.relations = []
        self.type = None
        self.node = None
        self.alt_names = []
        # self.linked_node = None

    # def is_following_entity(self, entity):
    #     """ Check if the entity is following self.
    #
    #     :param entity:
    #     :return:
    #     """
    #
    #     return self.token_begin == entity.token_end + 1

    def add_alt_name(self, text):
        """

        :param text:
        :return:
        """
        if text not in self.alt_names and text not in self.text:
            self.alt_names.append(text)
