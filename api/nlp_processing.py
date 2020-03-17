"""

"""

from pycorenlp import StanfordCoreNLP
from models.nlp_extraction.Entity import Entity
from models.nlp_extraction.Relation import Relation
from constants import NLP_SERVER_URL


nlp = StanfordCoreNLP(NLP_SERVER_URL)


def _call_stanfordnlp_server(text):
    """

    :param text:
    :return:
    """
    try:
        output = nlp.annotate(text, properties={"annotators": "tokenize,ssplit,pos,ner,depparse,dcoref,natlog,openie",
                                              "outputFormat": "json", "openie.triple.strict": "true"})
        if isinstance(output, str):
            raise Exception()
        return output
    except Exception as e:
        print("Error while calling NLP server: "+str(e))
        return None


def _find_entity_relation(list_entity, num_sentence, text, token_begin, token_end):
    """

    :param list_entity:
    :param num_sentence:
    :param text:
    :param token_begin:
    :param token_end:
    :return:
    """
    for entity in list_entity:
        if entity.text in text and entity.token_begin >= token_begin and entity.token_end <= token_end \
                and entity.sentence_num == num_sentence:
            return entity
    return None


def _find_entity_by_name_and_pos(list_entity, num_sentence, text, token_begin, token_end):
    """

    :param list_entity:
    :param num_sentence:
    :param text:
    :param token_begin:
    :param token_end:
    :return:
    """
    for entity in list_entity:
        # if entity.text == text and entity.token_begin == token_begin and entity.token_end == token_end \
        #         and entity.sentence_num == num_sentence:
        if entity.sentence_num == num_sentence and \
                ((entity.token_begin <= token_end and token_end <= entity.token_end) or
                     (entity.token_end >= token_begin and token_begin >= entity.token_begin)):
            return entity
    return None


def _get_most_representative(list_entities_coref, list_entity):
    """

    :param list_entities_coref:
    :param list_entity:
    :return:
    """

    for entity in list_entities_coref:
        if entity["isRepresentativeMention"]:
            most_representative = _find_entity_by_name_and_pos(list_entity, int(entity["sentNum"]) - 1, entity["text"],
                                                               entity["startIndex"] - 1,
                                                               entity["endIndex"] - 1)
            if most_representative is not None:
                most_representative.type = entity["type"]
                return most_representative
    return None


def _found_same_relation(entity_subject, relation, object):
    """

    :param entity_subject:
    :param relation:
    :param object:
    :return:
    """
    # TODO
    return True


def _fing_entity_normalizedNER(entitymentions, list_entity, num_sentence):
    """

    :param entitymentions:
    :param list_entity:
    :param num_sentence:
    :return:
    """

    for entity in list_entity:
        if entity.sentence_num == num_sentence and entity.ner == entitymentions["ner"] and entity.text == entitymentions["normalizedNER"]:
            return entity
    return None


def _update_normalizedNER_entity(entitymentions, entity):
    """

    :param entitymentions:
    :param entity:
    :return:
    """
    if entitymentions["tokenBegin"] < entity.token_begin:
        entity.token_begin = entitymentions["tokenBegin"]
    if entitymentions["tokenEnd"] > entity.token_end:
        entity.token_end = entitymentions["tokenEnd"]


def create_entity_and_relations(output):
    """

    :param output:
    :return:
    """
    list_entity = []
    for num_sentence, sentence in enumerate(output["sentences"]):

        # Create entities
        # previous_entity = None
        for entitymentions in sentence["entitymentions"]:
            update = False
            if "normalizedNER" in entitymentions.keys():
                entity = _fing_entity_normalizedNER(entitymentions, list_entity, num_sentence)
                if entity is None:
                    entity = Entity(num_sentence, entitymentions["tokenBegin"], entitymentions["tokenEnd"],
                                    entitymentions["normalizedNER"], entitymentions["ner"])
                else:
                    _update_normalizedNER_entity(entitymentions, entity)
                    update = True
            else:
                entity = Entity(num_sentence, entitymentions["tokenBegin"], entitymentions["tokenEnd"],
                                entitymentions["text"], entitymentions["ner"])

            # if previous_entity is None:
            #     previous_entity = entity
            # else:
            #     if entity.is_following_entity(previous_entity):
            #         previous_entity.linked_node = entity
            #     previous_entity = entity

            if not update:
                list_entity.append(entity)

        # Create relations
        for relations in sentence["openie"]:
            entity_subject = _find_entity_by_name_and_pos(list_entity, num_sentence, relations["subject"],
                                                          relations["subjectSpan"][0], relations["subjectSpan"][1])
            entity_object = _find_entity_by_name_and_pos(list_entity, num_sentence, relations["object"],
                                                         relations["objectSpan"][0], relations["objectSpan"][1])
            entity_relation = _find_entity_relation(list_entity, num_sentence, relations["relation"],
                                                    relations["relationSpan"][0], relations["relationSpan"][1])

            entity_subject = entity_subject if entity_subject is not None else relations["subject"]
            entity_object = entity_object if entity_object is not None else relations["object"]

            # Assign relation to entity
            if not isinstance(entity_subject, Entity) and not isinstance(entity_object, Entity):
                pass
                #relation = Relation(relations["subject"], entity_relation, relations["relation"], relations["object"])
                # Case where we don't do anything with the relation
            elif isinstance(entity_subject, Entity) and not isinstance(entity_object, Entity):
                relation = Relation(entity_subject, entity_relation, relations["relation"], relations["object"])
                if not _found_same_relation(entity_subject, relations["relation"], relations["object"]):
                    entity_subject.relations.append(relation)
            elif not isinstance(entity_subject, Entity) and isinstance(entity_object, Entity):
                relation = Relation(relations["subject"], entity_relation, relations["relation"], entity_object)
                # entity_object.relations.append(relation)
                print("!!!!ENTITY SUBJECT IS NONE!!!! - ", relations["subject"], relations["relation"], entity_object.text)
            else: # Subject and Object are not None
                relation = Relation(entity_subject, entity_relation, relations["relation"], entity_object)
                # just put one relation. probably better for DB later
                entity_subject.relations.append(relation)

    return list_entity


def handle_coreference(list_entity, output):
    """

    :param list_entity:
    :param output:
    :return:
    """
    for value in output["corefs"].items():
        list_entities_coref = value[1]
        if len(list_entities_coref) > 0:

            # Find the most representative in the list
            most_representative_entity = _get_most_representative(list_entities_coref, list_entity)
            if most_representative_entity is not None:

                for ent in list_entities_coref:
                    entity = _find_entity_by_name_and_pos(list_entity, int(ent["sentNum"]) - 1, ent["text"],
                                                          ent["startIndex"] - 1,
                                                          ent["endIndex"] - 1)
                    if entity != most_representative_entity and entity is not None \
                            and entity.ner == most_representative_entity.ner:
                        entity.type = ent["type"]
                        most_representative_entity.coref.append(entity)
                        if entity.type == "PROPER":
                            most_representative_entity.add_alt_name(entity.text)
                        try:
                            list_entity.remove(entity)
                        except:
                            pass


def process_nlp(text):
    """

    :param text:
    :return:
    """
    list_entity = []
    # Process the text by calling StanfordNLP Server
    output = _call_stanfordnlp_server(text)
    if output is not None:
        # Process the output of StanfordNLP Server - Create entities and related relations
        list_entity = create_entity_and_relations(output)
        # Process co-reference
        handle_coreference(list_entity, output)
    return list_entity




