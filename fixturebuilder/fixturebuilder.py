
from copy import deepcopy
from json import dumps as json_encode


class Location(object):
    def __init__(self, prop_name, index=None):
        """
        initializes a new Location
        :param prop_name: str
        :param index: int
        """
        self._prop_name = prop_name
        self._index = index

    @property
    def prop_name(self):
        """
        :return: str
        """
        return self._prop_name

    @property
    def index(self):
        """
        :return: int
        """
        return self._index

    @property
    def has_index(self):
        return self._index is not None


class FixtureBuilder(object):
    def __init__(self, data, parent, location):
        """
        initializes a new builder instance. should not be called directly. Use FixtureBuilder.create() instead.
        :param data:
        :param parent: FixtureBuilder
        :param location: Location
        """
        self._data = data
        self._location = location
        self._parent = parent

    @staticmethod
    def create(data):
        """
        create a new builder instance
        :param data:
        :return: FixtureBuilder
        """
        return FixtureBuilder(data, None, '')

    @property
    def location(self):
        """
        if this builder is a child builder
        this refers to the location of this builder's data in the parent
        :return: Location
        """
        return self._location

    @property
    def parent(self):
        """
        if this is a child builder
        :return: FixtureBuilder
        """
        return self._parent

    @property
    def data(self):
        """
        returns builder's data
        :return:
        """
        return self._data

    @property
    def json(self):
        """
        returns builder's data as a JSON string
        :return str
        """
        return json_encode(self.data)

    def set(self, prop_name, value):
        """
        set property
        :param prop_name: str
        :param value:
        :return: FixtureBuilder
        """
        if prop_name not in self.data:
            raise KeyError('attribute {} does not exist in {}'.format(prop_name, json_encode(self.data)))
        data = deepcopy(self.data)
        data[prop_name] = value
        return FixtureBuilder(data, self.parent, self.location)

    def add(self, prop_name, value):
        """
        append element to list
        :param prop_name: str
        :param value:
        :return: FixtureBuilder
        """
        if prop_name not in self.data:
            raise KeyError('attribute {} does not exist in {}'.format(prop_name, json_encode(self.data)))
        data = deepcopy(self.data)
        data[prop_name].append(value)
        return FixtureBuilder(data, self.parent, self.location)

    def with_dict(self, prop_name):
        """
        create a child builder to operate on a dict value
        :param prop_name: str
        :return: FixtureBuilder
        """
        if not isinstance(self.data[prop_name], dict):
            raise AttributeError('dict operations are not supported on property {}'.format(prop_name))
        return FixtureBuilder(self.data[prop_name], self, Location(prop_name))

    def with_dict_list_element(self, prop_name, index=-1):
        """
        create a child builder to work on a list element that is a dict
        :param prop_name: str
        :param index: int
        :return: FixtureBuilder
        """
        element = self.data[prop_name][index]
        if not isinstance(element, dict):
            raise AttributeError('dict operations are not supported on list element {} of property {}'.format(index, prop_name))
        return FixtureBuilder(element, self, Location(prop_name, index))

    def duplicate_last_list_element(self, prop_name):
        """
        duplicates the last list element
        :param prop_name: str
        :return: FixtureBuilder
        """
        data = deepcopy(self.data)
        data[prop_name].append(deepcopy(data[prop_name][-1]))
        return FixtureBuilder(data, self.parent, self.location)

    def done(self):
        """
        finish working on a child builder and return to the parent
        :return: FixtureBuilder
        """
        if self.parent is None:
            raise NotImplementedError('done() is not defined for an empty parent. Maybe you want to access data')
        data = deepcopy(self.parent.data)
        if self.location.has_index:
            data[self.location.prop_name][self.location.index] = self.data
        else:
            data[self.location.prop_name] = self.data
        return FixtureBuilder(data, self.parent.parent, self.parent.location)
