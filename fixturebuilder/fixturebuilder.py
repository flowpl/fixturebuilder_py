
from copy import deepcopy
from json import dumps as json_encode


class FixtureBuilder(object):
    def __init__(self, data, parent, location):
        """initializes a new builder instance. should not be called directly. Use FixtureBuilder.create() instead."""
        self._data = data
        self._location = location
        self._parent = parent

    @staticmethod
    def create(data):
        """create a new builder instance"""
        return FixtureBuilder(data, None, '')

    @property
    def prop_name(self):
        return self._location['prop_name']

    @property
    def index(self):
        return self._location['index']

    @property
    def location(self):
        return self._location

    @property
    def parent(self):
        return self._parent

    @property
    def data(self):
        """returns builder's data"""
        return self._data

    @property
    def json(self):
        """returns builder's data as a JSON string"""
        return json_encode(self.data)

    def set(self, prop_name, value):
        """set property"""
        if prop_name not in self.data:
            raise KeyError('attribute {} does not exist in {}'.format(prop_name, json_encode(self.data)))
        data = deepcopy(self.data)
        data[prop_name] = value
        return FixtureBuilder(data, self.parent, self.location)

    def add(self, prop_name, value):
        """append element to list"""
        if prop_name not in self.data:
            raise KeyError('attribute {} does not exist in {}'.format(prop_name, json_encode(self.data)))
        data = deepcopy(self.data)
        data[prop_name].append(value)
        return FixtureBuilder(data, self.parent, self.location)

    def with_dict(self, prop_name):
        """create a child builder to operate on a dict value"""
        if not isinstance(self.data[prop_name], dict):
            raise AttributeError('dict operations are not supported on property {}'.format(prop_name))
        return FixtureBuilder(self.data[prop_name], self, {'prop_name': prop_name})

    def with_dict_list_element(self, prop_name, index=-1):
        """create a child builder to work on a list element that is a dict"""
        element = self.data[prop_name][index]
        if not isinstance(element, dict):
            raise AttributeError('dict operations are not supported on list element {} of property {}'.format(index, prop_name))
        return FixtureBuilder(element, self, {'prop_name': prop_name, 'index': index})

    def done(self):
        """finish working on a child builder and return to the parent"""
        if self.parent is None:
            raise NotImplementedError('done() is not defined for an empty parent. Maybe you want to access data')
        data = deepcopy(self.parent.data)
        if 'index' in self.location:
            data[self.prop_name][self.index] = self.data
        else:
            data[self.prop_name] = self.data
        return FixtureBuilder(data, self.parent.parent, self.parent.location)
