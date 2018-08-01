import json
import jieba
import logging
import logging
from module.Utilities.dict import Dict
from module.Utilities.text import trim_punct

class CategorizerV3(object):

    CAT_LBClassID_DICT = dict(finance=7, life=0, pet=26, emotion=19, travel=14, sports=4, politics=1, society=2, fashion=10, metaphysics=21, military=5, history=18, culture=20, edu=13, game=16, food=24, car=8, house=9, funny=25, tech=6, science=0, health=0, world=15, entertainment=3, comic=0, baby=17)

    FUNNY_PATTERN = [u"内涵图", u"内涵囧图", u"内涵趣图", u"内涵搞笑", u"内涵段子",
                     u"搞笑趣图", u"搞笑精选", u"【搞笑】"]

    FUNNY_START_PATTERN = [u"内涵", u"爆笑"]

    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger(__name__)
        self.params = Dict(json.load(open(kwargs.get('config', 'conf/cat.conf'))))
        self.classifiers = {}
        self.tokenizer = jieba.Tokenizer()
        self.tokens = set()
        for cate, config in self.params.v3.items():
            cid = config['cid']
            # load all category keyword
            with open(config['keyword2idfile'], "rb") as f:
                for line in f:
                    keyword, _id = line.decode("utf-8").rstrip("\n").split("")
                    self.tokens.add(keyword.lower())
            self.classifiers[cate] = OneVsRestClassifier(
                cate, cid, config['keyword2idfile'], config['publisher2idfile'],
                config['keyword2idffile'], config['modelfile'], config['thresholdfile'])
        for token in self.tokens:
            self.tokenizer.add_word(token)