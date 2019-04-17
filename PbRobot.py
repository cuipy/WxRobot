#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import cgi
import json
import time

from wxpy import *
import urllib
from urllib.parse import urlencode, quote
import requests
import re
from io import BytesIO
from pydub import AudioSegment
from aip import AipSpeech
import platform
import random,os
import datetime
import asyncio
import hashlib
from utils import async_call,MysqlUtils,StringUtils

if platform.system() =='Windows':
    AudioSegment.converter = r"D:\\apps\\ffmpeg\\bin\\ffmpeg.exe"
elif platform.system()=='Linux':
    AudioSegment.converter = r"/usr/local/bin/ffmpeg"

""" Baidu AipSpeech 的你的 APPID AK SK """
APP_ID = '15726960'
API_KEY = 'UYvaI5wBPpngKIept9VCjEod'
SECRET_KEY = 'OckYaMV2cU8GZ4m2lli21PnaCcBWlu0G'

aipSpeech = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

black_word = ['习近平', '李克强', '习大大', '习主席', '共产党', '操你妈', '妈逼']

str_help = '机器人功能：[呲牙]\n[蜡烛]签名XXXX：各种字体设计个性签名\n[蜡烛]动图XXXX：亮眼的动图有你的字\n[蜡烛]藏头诗XXXX：也许最浪漫的是，就是做一首唐诗送给你\n[蜡烛]电影XXX：查询电影\n[蜡烛]测名XXX：测名字\n[蜡烛]运势XXX：星座今天的运势\n[蜡烛]天气XXX：查询城市的当天天气\n' \
           '[蜡烛]笑话：我会给你讲个笑话\n[蜡烛]翻译XXX：进行中英文翻译\n[蜡烛]发送语音，我会进行语音识别，当然识别的比较白痴\n'

str_houzhui = '\n[疑问]不会用请输入：帮助\n[强]牛逼的新功能：签名XXX，动图XXXXX'


# 创建mxpy 的Bot对象
bot = Bot(cache_path=True,console_qr=True)
bot.enable_puid()

# super user 名称列表
super_user_names = ['崔鹏宇']
super_users = bot.friends().search(super_user_names)

@bot.register(msg_types=NOTE)
def join_group(msg):
    if msg.text.find('邀请你加入了群聊') != -1:
        bot.registered.disable(group_reply)

        # 注册群聊消息
        @bot.register(chats=(Group), msg_types=TEXT)
        def _group_reply(msg2):
            return group_reply(msg2)
    return


# 监听测试的好友 或 群消息
@bot.register(chats=(Friend), msg_types=TEXT)
def friend_reply(msg):
    msgtxt = msg.text
    return text_msg_reply(msgtxt, True, toUser=msg.sender)


# 监听所有群的看电影的消息
@bot.register(chats=(Group), msg_types=TEXT)
def group_reply(msg):
    if msg.sender.name =='1607':
        return

    msgtxt = msg.text
    if msg.is_at:
        botname = msg.receiver.name
        msgtxt = msgtxt.replace('@%s'%(botname), '').strip()


    return text_msg_reply(msgtxt, msg.is_at, toUser=msg.sender)


# 监听超级用户的消息
@bot.register(chats=(super_users), msg_types=(TEXT))
def superuser_reply(msg):
    if strInArray(msg.text, black_word):
        return '请不要乱说'

    if msg.text.startswith('群发'):
        qf_friends = bot.friends()
        qf_groups = bot.groups()
        fcnt = 0
        gcnt = 0

        if msg.text.startswith('群发好友：'):
            for frd in qf_friends:
                try:
                    frd.send(msg.text[5:])
                    time.sleep(15)
                except Exception:
                    print()
                finally:
                    fcnt += 1

        if msg.text.startswith('群发群：'):
            for grp in qf_groups:
                try:
                    grp.send(msg.text[4:])
                    time.sleep(15)
                except Exception:
                    print()
                finally:
                    gcnt += 1

        return '已经群发给%d个好友和%d个群' % (fcnt, gcnt)

    return friend_reply(msg)


@bot.register(chats=(Friend), msg_types=(RECORDING))
def alluser_recording(msg):
    txt = baidu_record_to_txt(msg)
    if txt:
        strreply =  '语音识别：' + txt
        msg.sender.send(strreply)


@bot.register(chats=(Group), msg_types=(RECORDING))
def group_recording(msg):
    txt = baidu_record_to_txt(msg)
    if txt:
        strreply = msg.member.name + '：' + txt
        msg.sender.send(strreply)


# 自动接受新的好友请求
@bot.register(msg_types=FRIENDS)
def auto_accept_friends(msg):
    # 接受好友请求
    new_friend = msg.card.accept()
    # 向新的好友发送消息
    new_friend.send(str_help)

    # 监听测试的好友 或 群消息
    @bot.register(chats=(new_friend))
    def _friend_reply(msg):
        return friend_reply(msg)


def text_msg_reply(msgtxt, isAt, toUser=None):
    if strInArray(msgtxt, black_word):
        return '请不要乱说'

    msgtxt = msgtxt.strip(' ').strip(':').strip('：')
    if msgtxt.find('帮助') >= 0:
        return str_help

    if msgtxt.startswith('签名') and toUser:
        msgtxt = msgtxt[2:]
        imgpath = qianming(msgtxt)
        toUser.send_image(imgpath)
        return

    if msgtxt.startswith('动图') and toUser:
        msgtxt = msgtxt[2:]
        imgpath = dongtu(msgtxt)
        toUser.send_image(imgpath)
        return

    if msgtxt.find('笑话') >= 0:
        str = qingyunke_robot(msgtxt)
        str = str + str_houzhui
        return str
    if msgtxt.startswith('翻译'):
        str = qingyunke_robot(msgtxt)
        str = str + str_houzhui
        return str
    if msgtxt.startswith('藏头诗'):
        shi = msgtxt[3:]
        str = cangtoushi(shi)
        str = str+ str_houzhui
        return str
    if msgtxt.startswith('天气'):
        city = msgtxt[2:]
        str = tianqi(city)
        str = str + str_houzhui
        return str
    if msgtxt.startswith('测名'):
        xingming = msgtxt[2:]
        str = suanming_mingzi(xingming)
        str = str + str_houzhui
        return str
    if msgtxt.startswith('运势') or msgtxt.startswith('星座'):
        xingzuo = msgtxt[2:]
        str = suanming_yunshi(xingzuo)
        str = str + str_houzhui
        return str

    # 先搜电影
    if msgtxt.startswith('电影'):
        moviename = msgtxt[2:]
    elif msgtxt.startswith('看'):
        moviename = msgtxt[1:]
    elif len(msgtxt)>1 and len(msgtxt) < 10:
        moviename = msgtxt

    if moviename:
        str = search_movie(moviename)
        if str:
            str = str + str_houzhui
            return str

    # 没电影就用 图灵机器人 处理
    if isAt:
        reply = qingyunke_robot(msgtxt)
        return reply

# 青云客机器人，老骂人
def qingyunke_robot(txt):
    url = "http://api.qingyunke.com/api.php?key=free&appid=0&msg=%s" % (txt)
    html = getHtmlText(url)
    arrmsg = re.findall('0,"content":"([\s\S]*?)"}', html)
    if arrmsg:
        msg = arrmsg[0]
        msg = msg.replace('{br}', '\n')
    else:
        msg = ""

    if msg.find('加我的好友秋秋') >= 0:
        return '萍萍不知啊！'

    msg = msg.replace('菲菲', '萍萍').replace('你大爷', 'XXX').replace('傻逼', 'XX').replace('操', 'X').replace('你妈',
                                                                                                      'XX').replace(
        '梅州行', '石家庄')

    return msg

def xiaoi_robot(txt,userId='客官'):
    url="http://robot.open.xiaoi.com/ask.do?question=%s&userId=%s&type=0&platform=web"%(txt,userId)

    appKey = "open_oY2gsF6Ueint";
    appSecret = "srAx9cuHDjaFN2N7zw4v";

    str1 = ':'.join( [appKey,'xiaoi.com',appSecret] )
    ha1 = StringUtils.sha1hex(str1)
    ha2 =  StringUtils.sha1hex('GET:/ask.do')
    nonce = StringUtils.buildRandom("",36)

    sig =  StringUtils.sha1hex( ":".join( [ha1,nonce,ha2]) )
    h1={'X-Auth':'app_key="'+appKey+'",nonce="'+nonce+'",signature="'+sig+'"'}

    res = getHtmlText(url,header=h1)
    return res



movie_ignore = ['是的','好啊','哈哈哈','哈哈','可以','不错','??','笨蛋','谢谢','早上好','滚蛋','傻逼']

# 查找电影
def search_movie(txt):

    if len(txt) > 10:
        return

    if txt in movie_ignore:
        return

    url = 'http://www.ffilmer.com/video/search/%s.html' % (quote(txt, encoding='utf-8'))

    mhtml = getHtmlText(url)

    re1 = re.compile('href=\"\/video\/detail\/(\d+?)\.html\">')
    arr = re1.findall(mhtml)

    if len(arr) == 0:
        return

    url = get_surl(url)
    res = '电影《%s》(%d部)：%s' % (txt, len(arr), url)
    return res


# 长地址，转换为短地址
def get_surl(url):
    # 接口说明 http://suo.im/
    api = 'http://suo.im/api.php?url=%s' % (quote(url, encoding='utf-8'))
    surl = getHtmlText(api)
    if surl == '' or surl.startswith('showData({'):
        return url

    return surl


def getHtmlText(url, header=None, charset='utf-8'):
    try:
        r = requests.get(url, headers=header, timeout=3000)
        r.raise_for_status()
        r.encoding = charset
        return r.text.strip()
    except:
        print(r)
        return "error"


def postHtmlText(url, data=None, js=None, charset='utf-8'):
    try:
        r = requests.post(url, data=data, json=js, timeout=3000)
        r.raise_for_status()
        r.encoding = charset
        return r.text
    except:

        print( r )
        return "error"


# 从 https://www.sheup.com/xingming_dafen.php 获取数据 编码为gb2312
def suanming_mingzi(xingming):
    if xingming.startswith(':') or xingming.startswith('：') or xingming.startswith(' '):
        xingming = xingming[1:]

    if len(xingming) < 2 or len(xingming) > 4:
        return

    if len(xingming) <= 3:
        fronttype = 1
    else:
        fronttype = 2

    url = 'http://www.1518.com/s?FrontType=%d&word=%s' % (fronttype, quote(xingming, encoding='gb2312'))
    html = getHtmlText(url, charset='gb2312')

    arr_cm_result = re.findall('alt="宝宝起名" border="0" /></a></div>([\s\S]+?)<br>', html)
    cm_result = '\n'.join(arr_cm_result)

    cm_result = cm_result.replace('<br />', '');

    return xingming + ":" + cm_result


def suanming_yunshi(xingzuo):
    if xingzuo.startswith(':') or xingzuo.startswith('：') or xingzuo.startswith(' '):
        xingzuo = xingzuo[1:]
    xingzuo2 = xingzuo[0:2]

    xzobj = {'白羊': 'baiyang', '金牛': 'jinniu', '双子': 'shuangzi', '巨蟹': 'juxie', '狮子': 'shizi', '处女': 'chunv',
             '天平': 'tianping', '天秤': 'tianping',
             '天蝎': 'tianxie', '摩羯': 'mojie', '水瓶': 'shuiping', '射手': 'sheshou', '双鱼': 'shuangyu'}
    xz = xzobj.get(xingzuo2)
    if xz is None:
        return '%s是啥星座？算不了算不了~~~~请认真聊天好不好？' % (xingzuo)

    url = 'https://www.meiguoshenpo.com/yunshi/' + xz + '/'
    html = getHtmlText(url)

    arrstr1 = re.findall('运势短评</span>([\s\S]+?)</p>', html)
    str1 = ''.join(arrstr1)

    arrstr2 = re.findall('整体运势</span>([\s\S]+?)</p>', html)
    str2 = ''.join(arrstr2)

    arrstr3 = re.findall('爱情运势</span>([\s\S]+?)</p>', html)
    str3 = ''.join(arrstr3)

    arrstr4 = re.findall('财富运势</span>([\s\S]+?)</p>', html)
    str4 = ''.join(arrstr4)

    arrstr5 = re.findall('健康运势</span>([\s\S]+?)</p>', html)
    str5 = ''.join(arrstr5)

    str1 = str1.replace(' ', '').replace('\r\n', '')
    str2 = str2.replace(' ', '').replace('\r\n', '')
    str3 = str3.replace(' ', '').replace('\r\n', '')
    str4 = str4.replace(' ', '').replace('\r\n', '')
    str5 = str5.replace(' ', '').replace('\r\n', '')

    str = '[呲牙]%s今日运势：[呲牙]\n[蜡烛]运势短评：%s\n[蜡烛]整体运势：%s\n[蜡烛]爱情运势：%s\n[蜡烛]财富运势：%s\n[蜡烛]健康运势：%s' % (
        xingzuo, str1, str2, str3, str4, str5)
    return str


# 藏头诗
def cangtoushi(txt):
    txt = txt.strip(':').strip('：').strip(' ')
    if txt is None or len(txt) < 4:
        return '藏头诗必须为四字短语，%s没法藏啊，赶紧重写。' % (txt)

    url = 'https://m.mofans.net/tool/cts.php'
    data = {'word': txt, 'length': 7, 'type': 0, 'mode': 2}
    html = postHtmlText(url, data=data)

    arrshi = re.findall('<div id="verse" class="verse TextCenter P10 F22">([\s\S]+?)<br/></div>', html)

    if len(arrshi) == 0:
        return '遗憾，出的题目太难，没搞出来，重出一个吧老兄。'

    htmlshi = arrshi[0].strip('\n')
    arrshi = htmlshi.split('<br/>')

    return '[玫瑰]糖诗赏析[玫瑰]\n[NO]%s\n[胜利]%s\n[OK]%s\n[强]%s' % (arrshi[0], arrshi[1], arrshi[2], arrshi[3])


# 天气预报
arr_tianqistatus = {'晴': '☀', '多云': '☁', '晴转多云': '☁', '多云转晴': '☁', '阴': '☁', '小雨': '☔', '雷阵雨': '⚡', '未知': '💡'}
def tianqi(city):
    if city.startswith(':') or city.startswith('：') or city.startswith(' '):
        city = city[1:]
    qcity = quote(city)

    url = 'http://toy1.weather.com.cn/search?cityname=%s&callback=success_jsonpCallback&_=%d' % (
        qcity, int(time.time() * 1000))
    html = getHtmlText(url)
    arrjson = re.findall('success_jsonpCallback\((.*?)\)', html)
    jsonhtml = arrjson[0]

    if jsonhtml == '[]':
        return '机器人很忙，没找到%s的天气信息，请稍后再试' % (city)

    # 正则获得 各种信息
    arrcityid = re.findall('\[\{"ref":"(\d+?)~', jsonhtml)
    if arrcityid:
        cityid = arrcityid[0]
    else:
        return '机器人很忙，没找到%s的天气信息，请稍后再试' % (city)

    url2 = 'http://www.weather.com.cn/weather1d/%s.shtml' % (cityid)
    html_detail = getHtmlText(url2)

    arrcityname = re.findall('<title>【(.+?)天气】', html_detail)
    if arrcityname:
        cityname = arrcityname[0]

    arrtodayinfo = re.findall('hidden_title" value="(.+?)"', html_detail)
    if arrtodayinfo:
        todayinfo = arrtodayinfo[0]

    arrtodaystatus = re.findall('wea" title="(.+?)"', html_detail)
    if arrtodaystatus:
        daystatus = arrtodaystatus[0]
        neightstatus = arrtodaystatus[0]

        ico_daystatus = arr_tianqistatus.get(daystatus) if arr_tianqistatus.get(
            daystatus) != None else arr_tianqistatus.get('未知')
        ico_neightstatus = arr_tianqistatus.get(neightstatus) if arr_tianqistatus.get(
            neightstatus) != None else arr_tianqistatus.get('未知')
    else:
        daystatus = '未知'
        neightstatus = '未知'
        ico_daystatus = arr_tianqistatus.get('未知')
        ico_neightstatus = arr_tianqistatus.get('未知')

    arrxianxing = re.findall('限行</span><em>(.*?)</em>', html_detail)
    strxianxing = ''
    if arrxianxing:
        xianxing_html = arrxianxing[0]
        arr_xianxingshu = re.findall('\d', xianxing_html)
        shuxianxing = '|'.join(arr_xianxingshu)
        strxianxing = '\n[抓狂]今日限行：%s' % (shuxianxing)

    url3 = 'http://www.weather.com.cn/weather/%s.shtml' % (cityid)
    html_detail3 = getHtmlText(url3)
    arr_d7status = re.findall('class="wea">(.*?)</p>', html_detail3)
    arr_icon_d7status = []
    for s in arr_d7status:
        arr_icon_d7status.append(
            arr_tianqistatus.get(s) if arr_tianqistatus.get(s) != None else arr_tianqistatus.get('未知'))
    str_icon_d7status = ''.join(arr_icon_d7status)

    strmsg = '%s：%s。\n白天：%s%s，夜间：%s%s%s\n老天爷的七日心情：%s' % (
        cityname, todayinfo, ico_daystatus, daystatus, ico_neightstatus, neightstatus, strxianxing, str_icon_d7status);

    return strmsg


# 字体编号
zitiids = [2, 9, 13, 14, 23, 24, 1, 901, 905, 5, 6, 8, 16, 21, 22, 343, 356, 358, 359, 364, 365, 375, 378, 388, 391,
           395, 399, 901, 905, 5, 6, 8, 16, 901, 905, 5, 6, 8, 16, 901, 905, 5, 6, 8, 16, 901, 905, 5, 6, 8, 16, 901,
           905, 5, 6, 8, 16, 901, 905, 5, 6, 8, 16,
           901, 905, 5, 6, 8, 16, 901, 905, 5, 6, 8, 16, 901, 905, 5, 6, 8, 16, 901, 905, 5, 6, 8, 16, 901, 905, 5, 6,
           8, 16, 901, 905, 5, 6, 8, 16, 901, 905, 5, 6, 8, 16, 901, 905, 5, 6, 8, 16, 901, 905, 5, 6, 8, 16, 901, 905,
           5, 6, 8, 16,
           901, 905, 5, 6, 8, 16, 901, 905, 5, 6, 8, 16]

# 图片下载路径
imgpath = 'dl_imgs'
colors = ['#0000FF', '#FF0500']

def baidu_record_to_txt(msg):
    try:
        rndstr = StringUtils.buildRandom()
        bsio = BytesIO(msg.get_file())
        audio = AudioSegment.from_mp3(bsio)
        audio2 = audio+6
        export = audio2.export(out_f='amr/%s.amr'%(rndstr),format="amr", bitrate="12.20k")
        bsMp3 = export.read()
        transform = aipSpeech.asr(bsMp3, 'amr', 8000, {'dev_pid': '1536', })

        if transform['err_no'] ==0:
            return  '|'.join(transform['result'])
        else:
            print(transform['err_no'],transform['err_msg'])
    except Exception as er:
        print(er);

def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

# 抓取签名网页的图片
def qianming(mingzi):
    mingzi = mingzi.strip(':').strip('：').strip(' ')

    zitiid = random.choice(zitiids)

    colorid = random.choice(colors)

    if not os.path.exists(imgpath):
        os.mkdir(imgpath)

    url = 'http://3.jiqie.com/a/re14.php'
    data = {'id': mingzi, 'idi': 'jiqie', 'id1': zitiid, 'id2': '14', 'id3': colorid, 'id5': '#FFFFFF'}
    html1 = postHtmlText(url, data=data)
    if html1.startswith('<img src="'):
        arr_imgurl = re.findall('<img src="(.+?)">', html1)
        if arr_imgurl:
            imgurl = arr_imgurl[0]
            imgname = _randstr() + '.jpg'

            urllib.request.urlretrieve(imgurl, imgpath + '/' + imgname)
            return imgpath + '/' + imgname


# 生成动图
def dongtu(txt):
    txt = txt.strip(':').strip('：').strip(' ')
    if not os.path.exists(imgpath):
        os.mkdir(imgpath)

    if txt == '':
        txt = '萍萍是这么喜欢你，\n你也喜欢萍萍吧！'

    # zitiid = random.choice(all_zitiids)
    zitiid = 4
    colorid = random.choice(colors)

    # 杨幂转笔
    arr_url = ["http://3.jiqie.com/c/re39.php",  # 杨幂转笔
               'http://3.jiqie.com/c/re18.php',  # 美女转笔
               'http://3.jiqie.com/c/re42.php',  # 女孩荡秋千
               'http://3.jiqie.com/c/re8.php',    # 箭头指人
               'http://3.jiqie.com/c/re16.php',      # 转笔签名2
               'http://3.jiqie.com/c/re17.php',      # 血龙签名
               'http://3.jiqie.com/c/re19.php',      # 冰龙签名
               'http://3.jiqie.com/c/re20.php',      # 画墨龙签名
               'http://3.jiqie.com/c/re21.php',      # 狐狸和太阳
               'http://3.jiqie.com/c/re22.php',    # 墨人舞剑1
               'http://3.jiqie.com/c/re23.php',  # 墨人舞剑2
               'http://3.jiqie.com/c/re25.php',  # 雪地写字
               'http://3.jiqie.com/c/re26.php',  # 魔术手
               'http://3.jiqie.com/c/re31.php',   # 当个学生容易吗
               #'http://3.jiqie.com/c/re32.php',  # 流光岁月
               'http://3.jiqie.com/c/re33.php',  # 墨人动态抡锤
               'http://3.jiqie.com/c/re34.php',  # 墨人动态抡锤2
               'http://3.jiqie.com/c/re38.php', # 我为自己代言
               ]
    arr_data = [{'id': txt, 'idi': 'jiqie', 'id1': 200, 'id2': zitiid, 'id3': 28, 'id4': time.strftime("%Y-%m-%d", time.localtime()), 'id5': colorid},# 杨幂转笔
                {'id': txt, 'idi': 'jiqie', 'id1': 30, 'id2': zitiid, 'id3': 28,  'id4':'', 'id5': colorid},# 美女转笔
                {'id': txt, 'idi': 'jiqie', 'id1': 10, 'id2': zitiid, 'id3': colorid, 'id4': colorid, 'id5': ''},# 女孩荡秋千
                {'id': txt, 'idi': 'jiqie','id1':txt,  'id2': 50,'id3': 2, 'id4': zitiid,  'id5': '#FF0000','id6':'#550000'},# 箭头指人
                {'id': txt, 'idi': 'jiqie', 'id1': 30, 'id2': zitiid, 'id3': '', 'id4': '', 'id5': '#624475', 'id6': '#4F375F'},# 转笔签名2
                {'id': txt, 'idi': 'jiqie', 'id1': 10, 'id2': zitiid, 'id3': 100, 'id4': '', 'id5': '#FFFFFF','id6':'#FF0000'},# 血龙签名
                {'id': txt, 'idi': 'jiqie', 'id1': 10, 'id2': zitiid, 'id3': 100, 'id4': '', 'id5': '#FF0000', 'id6': '#FFFFFF'}, # 冰龙签名
                {'id': txt, 'idi': 'jiqie', 'id1': 10, 'id2': zitiid, 'id3': 100, 'id4': '', 'id5': '#FF0000',  'id6': '#FFFFFF'},# 画墨龙签名
                {'id': txt, 'idi': 'jiqie', 'id1': 30, 'id2': zitiid, 'id3': 30, 'id4': '', 'id5': '#FF0000', 'id6': '#FFFF00'}, # 狐狸和太阳
                {'id': txt, 'idi': 'jiqie', 'id1': 10, 'id2': 9016, 'id3': 80, 'id4': '', 'id5': ''},# 墨人舞剑1
                {'id': txt, 'idi': 'jiqie', 'id1': 10, 'id2': zitiid, 'id3': 80, 'id4': '', 'id5': '#000000'},# 墨人舞剑2
                {'id': txt, 'idi': 'jiqie', 'id1': 10, 'id2': zitiid, 'id3': '#FFFFFF', 'id4': 100, 'id5': ''},# 雪地写字
                {'id': txt, 'idi': 'jiqie', 'id1': 20, 'id2': zitiid, 'id3': '#210F11', 'id4': '#210F11', 'id5': ''}, # 魔术手
                {'id': txt, 'idi': 'jiqie', 'id1': 10, 'id2': 312, 'id3': 310, 'id4': '#000000', 'id5': '#FFFFFF', 'id6':'jiqie','id7':400,'id8':100,'id9':250,'id10':'60','id11':'5'},# 当个学生容易吗
                #{'id': txt, 'idi': 'jiqie', 'id1': 510, 'id2': 1303, 'id3': 10, 'id4': 20, 'id5': 0, 'id6':'jiqie','id7':'#FFFFFF','id8':10,'id9':801,'id10':'','id11':''}, # 流光岁月
                {'id': txt, 'idi': 'jiqie', 'id1': 20, 'id2': 399, 'id3': '#FF0000', 'id4': '#000000', 'id5': '平步科技','id6':0},# 墨人动态抡锤
                {'id': txt, 'idi': 'jiqie', 'id1': 10, 'id2': 9000, 'id3': '80', 'id4': '', 'id5': '', 'id6': ''},# 墨人动态抡锤2
                {'id': txt, 'idi': 'jiqie', 'id1': 10, 'id2': 3, 'id3': '#FF0000', 'id4': '#FFFF00', 'id5': '', 'id6': ''}, # 我为自己代言

                ]
    idx = random.randint(0, len(arr_url) - 1)

    url = arr_url[idx]
    data = arr_data[idx]

    print(url)
    html1 = postHtmlText(url, data=data)
    if html1.find('<img src="') >= 0:
        arr_imgurl = re.findall('<img src="(.+?)">', html1)
        print(arr_imgurl)
        if arr_imgurl:
            imgurl = arr_imgurl[0]
            imgname = _randstr() + '.gif'

            urllib.request.urlretrieve(imgurl, imgpath + '/' + imgname)
            return imgpath + '/' + imgname


# 保存所有的Friend 和 Group信息到数据库中
def save_chater_to_db():
    global bot
    frds = bot.friends()
    for frd in frds:
        # utils.MysqlUtils.getSession('')

        print('friend:%s - %s  - %s - %s - %s '%( frd.puid,frd.name,frd.sex,frd.province,frd.city ) )

    grps = bot.groups()
    for grp in grps:
        print('group:%s - %s  - %s - %s   ' % (grp.puid, grp.name,grp.owner.puid,grp.owner.name))

save_chater_to_db()

# 判断一个字符串是否包含数组中的字符
def strInArray(str, arr):
    for a in arr:
        if str.find(a) >= 0:
            return True
    return False


def _randstr(len=8):
    seed = 'zyxwvutsrqponmlkjihgfedcba1234567890'
    sa = []
    for i in range(len):
        sa.append(random.choice(seed))
    salt = ''.join(sa)

    return salt


# @async_call
def for_1607():
    while True:
        grps=bot.groups().search('1607')
        if grps is None or len(grps)==0:
            return

        grp=grps[0]

        # 获取当前的时间
        strTime = time.strftime('%H:%M', time.localtime(time.time()))
        if strTime != '07:00':
            time.sleep(60)
            continue


        # 获得当前年、月、日
        today = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        arr_today = today.split('-')
        dt1 = datetime.date(int(arr_today[0]), int(arr_today[1]), int(arr_today[2]))

        dt2 = datetime.date(2019,6,7)
        days = dt2.timetuple().tm_yday - dt1.timetuple().tm_yday

        msg = '不怕千万人阻挡就怕自己投降\n距离高考还有 %d 天 奋斗吧'%(days)
        grp.send(msg)

        time.sleep(60)

for_1607()

embed()
