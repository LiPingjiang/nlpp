import os
import unittest
import logging
import json
import jieba
from module.Utilities.dict import Dict
from module.category.category import OneVsRestClassifier


class TestCat(unittest.TestCase):
    def test_ovr(self):
        print('\n')
        logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                            level=logging.DEBUG)
        os.chdir("../../")
        cate='sports'
        cid='25'
        config=Dict(json.load(open('conf/cat.conf'))).v3[cate]
        tokens = set()
        classifiers = {}
        tokenizer = jieba.Tokenizer()
        with open(config['keyword2idfile'], "rb") as f:
            for line in f:
                keyword, _id = line.decode("utf-8").rstrip("\n").split("")
                tokens.add(keyword.lower())
        classifiers[cate] = OneVsRestClassifier(
            cate, cid, config['keyword2idfile'], config['publisher2idfile'],
            config['keyword2idffile'], config['modelfile'], config['thresholdfile'])

        # uuid: xs450ZNtVOCaRmrDRYXl5w
        title='发改委：今年体育消费预计将近1万亿，已成经济发展“新风口”'
        content='<p>8月2日，国家发展改革委召开专题新闻发布会，介绍扩大消费有关工作情况并回答记者提问。关于体育领域的情况及政策考虑摘要如下：</p><p><br /></p><p><img src="http://img.contents.m.liebao.cn/c8288ddf-0434-523b-a044-e46bdc6707e0_w685.jpg" width="500" height="333" /></p><p>▲发展改革委社会司司长欧晓理</p><p><br /></p><p>今年我国体育产业持续高速发展，已经成为经济发展的“新风口”。</p><p><br /></p><p>一是规模不断扩大，预计今年底，体育产业增加值占GDP比重将超过1%，体育消费将近1万亿，体育产业机构数量增长超过20%，吸纳就业人数超过440万人。体育产业对于促消费、惠民生、稳增长的作用不断体现。</p><p><br /></p><p>二是结构不断优化，体育服务业增加值占体育产业增加值的比重超过50%，健身休闲产业和竞赛表演业增速均超过20%，航空、击剑、山地户外等体育消费蓬勃发展，成为体育消费的新热点。</p><p><br /></p><p>三是新模式新业态不断涌现，35个体育产业联系点城市和110个体育产业联系点单位积极推进各项改革任务，运动健康城市、体育小镇、体育综合体、体育公园和产业园区等平台建设加速推进。体育产业由点到线、由线及面的集聚区发展趋势日益凸显。</p><p><br /></p><p><strong>延展阅读：</strong></p><p><strong><br /></strong></p><p><strong>体育分段位获得政策关注之下，羽毛球分级赛事羽众现在怎么样了？</strong></p><p><br /></p><p><strong>从苟仲文上任后的几次大动作，我们读出体育总局未来三项工作重点</strong></p><p><br /></p><p></p>'
        publisher='懒熊体育'
        segtitle = tokenizer.lcut(title.lower())
        segcontent = tokenizer.lcut(content.lower())
        segpublisher = tokenizer.lcut(publisher.lower())
        kw_len = len((set(segtitle) | set(segcontent) | set(segpublisher)) & tokens)

        hit, prob, info = classifiers[cate].classify(-1, segtitle, segcontent, publisher)
        if hit:
            print('The prossiblity of ' + cate + ' is ' + str(prob) + ', extra information:\n' )
            from pprint import pprint
            pprint(info, indent=4)
            # cate = dict(name=sc.name, cid=sc.cid, weight=prob)
            # print("category result: %s" % json.dumps(info, ensure_ascii=False))
            # print(cate)


