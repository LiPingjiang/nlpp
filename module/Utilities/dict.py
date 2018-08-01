class Dict(dict):

    '''
    将dict转换为通过属性访问
    '''

    def __init__(self, *args, **kwargs):
        super(Dict, self).__init__(*args, **kwargs)
        for key in self:
            if isinstance(self[key], dict):
                self[key] = Dict(self[key])

    def __getattr__(self, key):
        try:
            return self[key]
        except:
            return None
            # except KeyError as k:
            # raise AttributeError, k

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
            return True
        except:
            return False
            # except KeyError as k:
            # raise AttributeError, k

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state):
        self.__dict__ = state

    def __repr__(self):
        return '<Dict ' + dict.__repr__(self) + '>'