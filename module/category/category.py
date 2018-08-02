import json
import math
import jieba
import logging
import liblinearutil
import collections
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

class OneVsRestClassifier(object):

    def __init__(self, name, cid, keyword2idfile, publisher2idfile, keyword2idffile, modelfile, thresholdfile):
        self.logger = logging.getLogger(__name__)
        self.name = name
        self.cid = cid
        self.keyword2id = dict()
        self.id2keyword = dict()
        self.publisher2id = dict()
        self.id2publisher = dict()
        self.id2feature = dict()
        self.kwid2idf = dict()
        self.initialized = True
        self.threshold = None
        try:
            with open(keyword2idfile, "rb") as f:
                for line in f:
                    keyword, _id = line.decode("utf-8").rstrip("\n").split("")
                    keyword = keyword.lower()
                    kwid = int(_id)
                    self.keyword2id[keyword] = kwid
                    self.id2keyword[kwid] = keyword

            with open(publisher2idfile, "rb") as f:
                for line in f:
                    publisher, _id = line.decode("utf-8").rstrip("\n").split("")
                    publisher = publisher.lower()
                    pid = int(_id)
                    self.publisher2id[publisher] = pid
                    self.id2publisher[pid] = publisher

            with open(keyword2idffile, "rb") as f:
                for line in f:
                    keyword, _idf = line.decode("utf-8").rstrip("\n").split("")
                    keyword = keyword.lower()
                    idf = float(_idf)
                    self.kwid2idf[self.keyword2id[keyword]] = idf
            self.id2feature = self.id2keyword.copy()
            self.id2feature.update(self.id2publisher)

            with open(thresholdfile, "rb") as f:
                for line in f:
                    clazz, _thre = line.decode("utf-8").rstrip("\n").split("\t")
                    if int(clazz) == 1:
                        self.threshold = float(_thre)
                        if self.threshold <= 0.5:
                            self.threshold = 0.51
                        break
            assert self.threshold is not None
            assert len(self.id2feature) == len(self.id2keyword) + len(self.id2publisher)
        except Exception as e:
            self.logger.exception(e)
            self.logger.critical("two-class classifier %s failed when parsing files:\n%s" % (name, e))
            self.initialized = False
        self.model = liblinearutil.load_model(modelfile)
        assert self.model.get_nr_feature() == len(self.id2feature)
        pass

    def classify(self, aid, segtitle, segcontent, publisher, queue=None):
        if self.initialized == False:
            self.logger.info("two-class classifier %s is not properly initialized" % self.name)
            result = (False, 0.0, {})
            if queue is None:
                return result
            else:
                queue.put(result)
                return
        titlefea = filter(None, map(lambda x: self.keyword2id.get(x, 0), segtitle))
        contentfea = filter(None, map(lambda x: self.keyword2id.get(x, 0), segcontent))
        feas = collections.defaultdict(lambda: 0.0)
        for _id in list(titlefea) + list(contentfea):
            feas[_id] += 1
        for _id in set(titlefea):
            feas[_id] *= 1.2
        for _id in feas.keys():
            feas[_id] *= self.kwid2idf[_id]
        feas = dict(sorted(feas.items(), key=lambda x: x[1], reverse=True)[:50])
        denom = math.sqrt(sum([math.pow(score, 2) for _id, score in feas.items()]))
        for _id, score in feas.items():
            feas[_id] = score / denom
        publisher = publisher.strip().lower()
        pid = self.publisher2id.get(publisher, 0)
        if pid:
            feas[pid] = 1.0
        # 输入数据是所有的特征id以及其权重  {650: 0.6940445496636998, 31: 0.5952199358099312, 30866: 0.24321647045799732}
        # 返回值是两个概率，分别是为1类的概率和为-1类的概率
        # 由于是二分类，只是计算是否是这一类的概率，列别标签lable可以用self.model.get_labels()查看
        _, _, probs = liblinearutil.predict([1], [feas], self.model, "-b 1 -q")
        # print(probs)
        # print("feas:")
        # print(feas)
        pindex = self.model.get_labels().index(1)
        # print("self.model.get_labels()")
        # print(self.model.get_labels())
        assert pindex >= 0
        probs = probs[0]
        hit = None
        info = collections.OrderedDict()
        if probs[pindex] >= self.threshold:
            hit = True
            kws = sorted(filter(lambda x: x[0] is not None,
                                [(self.id2keyword.get(_id, None), _id, score, self.model.w[_id - 1])
                                 for _id, score in feas.items()]),
                         key=lambda x: x[2] * x[3], reverse=True)
            info["aid"] = aid
            info["name"] = self.name
            info["publisher"] = publisher
            info["weight"] = probs[pindex]
            info["kws"] = kws
            info["dotprod"] = sum([s * w for kw, _id, s, w in kws])
            info["publisherweight"] = self.model.w[pid-1] if pid else 0.0
        else:
            hit = False
        result = (hit, probs[pindex], info)
        if queue is None:
            return result
        else:
            queue.put(result)
        return
    pass