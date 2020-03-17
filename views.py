from flask import Flask, g, Response, request
import time

from api.nlp_processing import process_nlp
from api.web_extraction import process_web_extraction
from api.db import process_entity_db


# Make sure java 11 is correctly configure
# export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64


# app = Flask(__name__, static_url_path='/static/')








start_time = time.time()


# Web crawling
# keyword = "NIST"
# web_start_time = start_time
# dict_web_extract = process_web_extraction(keyword)
# print("---Web extraction %s seconds ---" % (time.time() - web_start_time))

# count = 0
# for domain, webpage_dict in dict_web_extract.items():
#        for url, webpage in webpage_dict.items():
#               file = open("static/"+ str(count), "w")
#               file.write(webpage)
#               file.close()  # to change file access modes
#               count += 1
import os
entries = os.listdir('static/')
for file in entries:
       f = open("static/"+file, "r")
       str = f.read()
       f.close()
       list_entity = process_nlp(str)
       process_entity_db(list_entity)


       # NLP Processing
# text = "Obama was born in August 4, 1961."
# text = "Barak Obama was President of the United States. He was born in Honolulu, Hawaii, USA, the 4th of August 1961. " \
#        "The National Institute of Standards and Technology was created in 1901. Obama was chief at NIST from 2008 to 2016."
# nlp_start_time = time.time()
# for domain, webpage_dict in dict_web_extract.items():
#        for url, webpage in webpage_dict.items():
#               list_entity = process_nlp(webpage)
#        # print("---StanfordNLP %s seconds ---" % (time.time() - nlp_start_time))
#        #
#        #
#
#        # DB processing
#               process_entity_db(list_entity)








# @app.route("/")
# def get_index():
#     return None
#
#
# if __name__ == '__main__':
#     app.run(port=8088)


# def get_autocomplete(text):
#     query = """
#     start n = node(*) where n.name =~ '(?i)%s.*' return n.name,labels(n) limit 10;
#     """
#     query = query % (text)
#     obj = []
#     for res in graph.cypher.execute(query):
#         # print res[0],res[1]
#         obj.append({'name':res[0],'entity_type':res[1]})
#     return res
