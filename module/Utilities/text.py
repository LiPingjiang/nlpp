import logging
from bs4 import BeautifulSoup

def trim_punct( content):
    punct = set(u''':!),.:;@~`#$%^&*()?]}¢'"、。<>〉》」』】〕〗〞︰︱︳﹐､﹒﹔﹕﹖﹗﹚﹜﹞！），．：；？｜|｝︴︶︸︺︼︾﹀﹂﹄﹏､～￠々‖•·ˇˉ―--′’”([{£¥'"‵〈《「『【〔〖（［｛￡￥〝︵︷︹︻︽︿﹁﹃﹙﹛﹝（｛“‘-—_…←↑~…*　=■● \xc2\xa0''')
    if isinstance(content, str):
        return ''.join(filter(lambda x: x not in punct, content))
    elif isinstance(content, unicode):
        return ''.join(filter(lambda x: x not in punct, content.decode('utf8'))).encode('utf8')
    elif isinstance(content, list):
        return map(lambda line: trim_punct(line), content)

def html_to_text(content, logger = logging.getLogger('Html Helper')):
    for parser in ['html.parser','lxml', 'html5lib']:
        try:
            soup = BeautifulSoup(content, parser)
            return trim_punct(soup.get_text('', strip=True))
        except Exception as e:
            logger.error('%s parse content failed, exception: %s' % (parser, e))
    return content
