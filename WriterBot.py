#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from flask import Flask,jsonify,make_response,send_from_directory
import synonyms
import json
import re
import jieba
import random

app = Flask(__name__)

@app.route('/jinyi/<word>',methods=['GET','POST'])
def jinyi(word):
    str = word
    lstseg = synonyms.seg(str)
    nword=''
    for i,str1 in enumerate(lstseg[0]):
        # print('%s = %s'%(str1,lstseg[1][i] ),synonyms.nearby(str1) )

        # 忽略不处理的词性
        ignore_cixing = ['x','nz','nr','eng','nrfg']

        if lstseg[1][i] in ignore_cixing:
            nstr = str1
        else:
            nstr = _nearby_word(str1)
            if nstr == '':
                nstr = str1
            else:
                irnd = random.randint(1,10)
                if irnd<=1:
                    nstr = str1
        nword+= nstr

    #print('原句：%s\n新句：%s'%(word,nword))
    return  make_response(nword)

@app.route('/test2/<word>',methods=['GET'])
def test2(word):
    w = includeEngOrDigit(word)
    return str(w)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.root_path, 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.errorhandler(404)
def not_found(error):
    res = make_response(jsonify({'error': 'Restful service not found!'}), 404)
    return res



# 获得一个单词的最接近的同义词
def _nearby_word(src_word):
    if src_word is None or src_word=='' or includeEngOrDigit(src_word):
        return ''
    if len(src_word)<=1:
        return src_word

    lstNearby = synonyms.nearby(src_word)

    if len(lstNearby)==2 and len(lstNearby[0])>2:
        arr = lstNearby[0][1:]
        res = random.choice( arr )
        if res in ['</s>'] or includeEngOrDigit(res):
            return ''
        else:
            return res

    return ''

def includeEngOrDigit(word):
    return not re.match('[a-zA-Z0-9_]',word) == None


if __name__ == '__main__':
    app.run(debug=True,port=5071)
