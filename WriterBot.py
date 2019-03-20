#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from flask import Flask,jsonify,make_response,send_from_directory
import synonyms
import json

app = Flask(__name__)

@app.route('/test1/<word>',methods=['GET'])
def test1(word):
    str = word
    nstr = _nearby_word(str)
    return  nstr

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.root_path, 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.errorhandler(404)
def not_found(error):
    res = make_response(jsonify({'error': 'Restful service not found!'}), 404)
    return res

# 获得一个单词的最接近的同义词
def _nearby_word(src_word):
    if src_word is None or src_word=='':
        return ''
    lstNearby = synonyms.nearby(src_word)

    if len(lstNearby)==2 and len(lstNearby[0])>2:
        for nstr in lstNearby[0]:
            if nstr!=src_word:
                return nstr

    return ''



if __name__ == '__main__':
    app.run(debug=True,port=5071)
