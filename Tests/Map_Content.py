

class MapContent(dict):

    def __missing__(self, key):
        return (0,0,0)

    def __setitem__(self, key, value):
        if value!=(0,0,0):
            dict.__setitem__(self, key, value)
        else:
            if key in self.keys():
                dict.__delitem__(self, key)

# TODO numpy sparse array

if __name__ == '__main__':
    map_content=MapContent()
    assert map_content[(0,0)] ==(0,0,0)
    map_content[(0,0)]=(0,1,0)
    assert map_content[(0,0)]==(0,1,0)
    map_content[(0,0)]=(0,0,0)
    assert (0,0) not in map_content.keys()
    map_content[(0,1)]=(10,0,0)
    map_content[(1,1)]=(0,10,0)
    map_content[(1,0)]=(0,0,10)
    old_map1=MapContent(map_content)
    assert old_map1[(0,0)]==(0,0,0)
