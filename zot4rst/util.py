import jsbridge
import re
import urllib

def unquote(source):
    if type(source) == list:
        return [ unquote(x) for x in source ]
    elif type(source) == dict:
        return dict([ (k, unquote(v)) for (k,v) in source.items()])
    elif (type(source) == unicode) or (type(source) == str) or (type(source) == jsbridge.jsobjects.JSString):
        res = urllib.unquote(unicode(source))
        if '%u' in res:
            reslst = re.split(r'(%u[A-Za-z0-9]{4})', res)
            for i in range(1, len(reslst), 2):
                reslst[i] = reslst[i].replace('%u','\\u').decode('unicode_escape')
            res = u"".join(reslst)
        return res
    else:
        return source
