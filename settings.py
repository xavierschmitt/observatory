"""
Settings
"""
import os

# $ export NEO4J_USERNAME=neo4j
# $ export NEO4J_PASSWORD=neo4j
# $ export NEO4J_BOLT_URL="bolt://$NEO4J_USERNAME:$NEO4J_PASSWORD@localhost:7687"

NEO4J_BORL_URL="bolt://neo4j:neo4j@localhost:7687"
os.environ["CORENLP_HOME"] = "/home/xavier/Downloads/stanford-corenlp-full-2018-10-05"