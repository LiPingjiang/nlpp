import os
import unittest
import logging
from module.md5.md5calculator import Md5Calculator


class TestMD5(unittest.TestCase):

    def test_init(self):
        print('\ncurrent working path: '+os.getcwd()) #打印出当前工作路径
        os.chdir("../../")
        self.md5c=Md5Calculator(config='conf/md5.conf')

    def test_md5(self):
        print('\n')
        os.chdir("../../")
        self.md5c=Md5Calculator(config='conf/md5.conf')
        self.assertEqual(self.md5c.md5("abc200xyz".encode("utf-8")) , "e56763ca")

    def test_title_md5(self):
        print('\n')
        logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                            level=logging.DEBUG)
        os.chdir("../../")
        self.md5c=Md5Calculator(config='conf/md5.conf')
        # self.md5c.title_md5("abc200xyz".encode("utf-8"))
        self.md5c.title_md5("abc呸200x呸yz好的家具可以用3 三十 c09年")

    def test_content_md5(self):
        print('\n')
        logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                            level=logging.DEBUG)
        os.chdir("../../")
        self.md5c=Md5Calculator(config='conf/md5.conf')
        with open("data/test/content.html") as f:data=f.read()
        # print(data)
        self.assertEqual(self.md5c.content_md5(content=data),"096a96ae")




