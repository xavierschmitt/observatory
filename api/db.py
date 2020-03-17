"""

"""

from settings import NEO4J_BORL_URL

from models.nlp_extraction.Entity import Entity
from py2neo.data import Node, Relationship
from py2neo import Graph

from constants import NER_TO_NODE_RELATIONSHIP, NER_LOCATION
graph = Graph(NEO4J_BORL_URL, auth=('neo4j', 'admin'))
# MATCH (n) DETACH DELETE n;


def create_relationships(relations, tx, root=None):
    """

    :param relations:
    :param tx:
    :param root:
    :return:
    """
    property = {}
    for relation in relations:
        if isinstance(relation.object, Entity) and relation.object.ner in NER_TO_NODE_RELATIONSHIP + NER_LOCATION:
            if relation.object.node is None:
                print("ERROR: node should be here")
            else:
                node_object = relation.object.node
            subject = root.node if root is not None else relation.subject.node
            create_relation(subject, relation.relation_text, node_object, tx)
        else:
            if isinstance(relation.object, Entity):
                property[relation.relation_text] = relation.object.text
            else:
                property[relation.relation_text] = relation.object
    return property


def create_node(entity, tx):
    """

    :param entity:
    :param tx:
    :return:
    """
    node = Node(entity.ner, name=entity.text, alt_names=entity.alt_names)
    if entity.ner in NER_LOCATION:
        node.add_label("LOCATION")
    tx.create(node)
    print("create node: "+entity.text)
    return node


def create_relation(node1, relation, node2, tx):
    relationship = Relationship(node1, relation, node2)
    print("create relationship: " + node1["name"] + " : " + relation + " : " + node2["name"])
    tx.create(relationship)


def _get_or_create_local_node(entity, tx):
    """

    :param entity:
    :param tx:
    :return:
    """
    if entity.node is None:
        node = create_node(entity, tx)
        entity.node = node
    else:
        node = entity.node
    return node


def _update_node(db_node, local_node, tx):
    """

    :param db_node:
    :param local_node:
    :return:
    """
    modification = False
    for label in local_node.label:
        if not db_node.has_label(label):
            db_node.add_label(label)

    for key, value in dict(local_node):
        if db_node[key] is None:
            db_node[key] = value
        elif db_node[key] == value:
            print("db node and local node have same value")
        else:
            print("db node and local node have different value :", db_node[key], value)

    if modification:
        print("update node: "+db_node.name)
        tx.push(db_node)


def _create_or_get_all_entities(list_entity, tx):
    """

    :param list_entity:
    :return:
    """
    for entity in list_entity:
        if entity.ner in NER_TO_NODE_RELATIONSHIP + NER_LOCATION:

            #TODO find node by name or alt_names
            # graph.nodes.match(entity.ner).where("_.name =~ '" + entity.text + "'").first()
            db_node = graph.nodes.match(entity.ner, name=entity.text).first()
            if db_node is None:
                _get_or_create_local_node(entity, tx)
            else:
                if entity.node is None:
                    entity.node = db_node
                else:
                    local_node = entity.node
                    _update_node(db_node, local_node, tx)


def _create_relationship_and_properties(list_entity, tx):
    """

    :param list_entity:
    :param tx:
    :return:
    """
    for entity in list_entity:
        if entity.node is not None:
            property = {}
            prop = create_relationships(entity.relations, tx)
            if prop:
                property.update(prop)

            for ref in entity.coref:
                # Create relationships from coref
                prop = create_relationships(ref.relations, tx, entity)
                if prop:
                    property.update(prop)

            # Add property
            for key, value in property.items():
                val = value.text if isinstance(value, Entity) else value
                entity.node[key] = val
                tx.push(entity.node)


def process_entity_db(list_entity):
    """

    :param list_entity:
    :return:
    """

    tx = graph.begin()

    _create_or_get_all_entities(list_entity, tx)

    _create_relationship_and_properties(list_entity, tx)

    tx.commit()


