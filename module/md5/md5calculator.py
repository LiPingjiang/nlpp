from module.Utilities.dict import Dict
from module.Utilities.text import trim_punct
from bs4 import BeautifulSoup
import hashlib
import logging
import json
import re


class Md5Calculator(object):
    def __init__(self, *args, **kwargs):
        with open(kwargs.get('config', 'conf/md5.conf')) as f: self.params = Dict(json.load(f))
        self.stop_list = map(lambda line: re.compile(line.strip()), open(self.params.stop_re));
        self.remove_regex = re.compile('|'.join(set(map(lambda line: line.strip(), open(self.params.stop_word)))))
        self.symbol_regex = re.compile(u'[^\u4E00-\u9FFF0-9a-zA-Z]')

    def md5(self, data):
        #   return last 8 charactors
        return hashlib.new('sha224', data).hexdigest()[-8:]

    def __is_junk(self, sentence):
        """判断是否是垃圾句子

        判断一个sentence是否是垃圾句子，比如包含广告语句等
        Args:
            sentence: 输入的句子
        Returns:
            boolean，是垃圾句子返回true
        """
        # print(sentence)
        for stop_pattern in self.stop_list:
            if stop_pattern.search(sentence):
                return True
        return False



    def title_md5(self, title):
        """cp中计算标题的md5

        使用正则表达式去除标题中的符号，无意义的词（啊，奥，哇等）使用sha224，取16进制形式的hash code的后8位。
        特殊的，结尾包含index形式的title有特殊处理，暂不知其应用场景。

        Args:
            title: 文章标题。python3下面有encode和decode的问题

        Returns:
            普通标题会返回标题的md5， 特殊标题会返回md5，sim_md5，clean_title，md5_list
            For example:

            {'Serak': ('Rigel VII', 'Preparer'),
             'Zim': ('Irk', 'Invader'),
             'Lrrr': ('Omicron Persei 8', 'Emperor')}

        Raises:
            IOError: 暂未发现.
        """
        # print(title)
        if isinstance(title, str):
            title = title.encode("utf-8")
        # remove symble and useless words
        title = self.symbol_regex.sub('', title.lower().decode('utf8'))
        title = self.remove_regex.sub('', title)
        min_length = 8
        max_list = 10
        ret = {}
        if title:
            logging.debug('title_md5 using title: %s', title)
            ret['md5'] = hashlib.new('sha224', title.encode('utf8')).hexdigest()[-8:]
            index = ''

            # 结尾包含index的需要特殊处理,逻辑未知

            # re.search 扫描整个字符串并返回第一个成功的匹配。
            #   +   至少一个
            #   $	匹配字符串的末尾。
            # 找到结尾有如下一个或多个字的词
            res = re.search(u'[上中下零一二三四五六七八九十0-9]+$', title)
            if res:
                # clean_title = 除结尾最后一词，去除所有的字母数字
                clean_title = re.sub('[a-zA-Z0-9]', '', title[:(len(title)-len(res.group()))])
                index = res.group() # 匹配到的最后一词
                # print('index: '+str(index))
                # print('clean title: ' + str(clean_title))
                if len(clean_title) >= 8:
                    # python3 使用 // 取整除，返回商的整数部分
                    title = clean_title[(len(clean_title)-min_length)//2:][:min_length] + index
                else:
                    clean_title = re.sub('[a-zA-Z0-9]', '', title)
                    if len(clean_title) >= 8:
                        title = clean_title[(len(clean_title)-min_length)//2:][:min_length]
                logging.debug('sim_title_md5 using title: %s', title)
                ret['sim_md5'] = hashlib.new('sha224', title.encode('utf8')).hexdigest()[-8:]
                ret['md5_list'] = []
                ret['clean_title'] = clean_title
                step = (len(clean_title)-min_length)//max_list or 1
                for i in range(max_list):
                    tmp = clean_title[i*step:(i+min_length)*step]
                    if len(tmp) == min_length:
                        tmp += index
                        ret['md5_list'].append(hashlib.new('sha224', tmp.encode('utf8')).hexdigest()[-8:])
            return ret

        else:
            logging.debug('title_md5 find empty title.')

    def content_md5(self, content, topK=3):
        thresh = 10
        # soup = BeautifulSoup(content.lower(), 'lxml')
        soup = BeautifulSoup(content.lower(),"html.parser")
        #对所有非html的句子，判断是否是junk
        sentenceList = filter(lambda item: not self.__is_junk(item), soup.strings)
        #将句子连在一起，然后分割出连续的词或句子
        sentenceList = re.split(u'，|。|！|：|；|“|”|？|,||!|"|:|;|\?', ','.join(sentenceList))
        #去除句子中的符号
        # map 得到的东西只能使用一次，第二次内容就会清空
        sentenceList = map(lambda item: trim_punct(item.strip()), sentenceList)
        #过滤出说有长度大于等于6的句子
        sentenceList = list(filter(lambda item: len(item) >= 6, sentenceList))
        #logging.debug(json.dumps(sentenceList, ensure_ascii=False))
        if len(sentenceList) >= thresh:
            sentenceList.sort(key=lambda item: len(item), reverse=True)
            # print(sentenceList)
            data = list(map(lambda item: self.remove_regex.sub('', item), sentenceList[:topK]))
            return hashlib.new('sha224', ''.join(data).encode("utf-8")).hexdigest()[-8:]
        else:
            # logging.debug('sentences length: %s, less then %s', len(sentenceList), thresh)
            data = trim_punct(soup.get_text('', strip=True))
            # logging.debug('using content: %s, length: %s', data, len(data))
            if len(data) >= 8:
                return hashlib.new('sha224', data.encode('utf8')).hexdigest()[-8:]