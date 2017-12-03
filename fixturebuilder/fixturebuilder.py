
from copy import deepcopy
from json import dumps as json_encode

import re


class _Location(object):
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


class _Value(object):
    def __init__(self, creator, current_value):
        self._value_creator = creator
        self._current_value = current_value

    @staticmethod
    def create(definition):
        try:
            return _Value(definition, definition())
        except TypeError:
            return _Value(lambda: definition, definition)

    @property
    def value(self):
        return self._current_value

    def copy(self, call_creator):
        if call_creator:
            return _Value(self._value_creator, self._value_creator())
        return _Value(self._value_creator, self._current_value)


class FixtureBuilder(object):
    def __init__(self, data, parent, location):
        """
        initializes a new builder instance. should not be called directly. Use FixtureBuilder.create() instead.
        :param data:
        :param parent: FixtureBuilder
        :param location: Location
        """
        self._data = self._wrap(data)
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
        return self._unwrap(self._data)

    @property
    def json(self):
        """
        returns builder's data as a JSON string
        :return str
        """
        return json_encode(self.data)

    def get(self, prop_name):
        """
        returns a single property by name
        :param prop_name: str
        :return:
        """
        return self._unwrap(self._data[prop_name])

    def set(self, prop_name, value):
        """
        set property
        :param prop_name: str
        :param value:
        :return: FixtureBuilder
        """
        if prop_name not in self._data:
            raise KeyError('attribute {} does not exist in {}'.format(prop_name, json_encode(self.data)))
        data = self._deepcopy(self._data)
        data[prop_name] = self._wrap(value)
        return FixtureBuilder(data, self.parent, self.location)

    def add(self, prop_name, value):
        """
        adds a new property to the data definition.
        :param prop_name: str
        :param value:
        :return: FixtureBuilder
        """
        data = self._deepcopy(self._data)
        data[prop_name] = self._wrap(value)
        return FixtureBuilder(data, self.parent, self.location)

    def append(self, prop_name, value):
        """
        append element to list
        :param prop_name: str
        :param value:
        :return: FixtureBuilder
        """
        if prop_name not in self._data:
            raise KeyError('attribute {} does not exist in {}'.format(prop_name, json_encode(self.data)))
        data = self._deepcopy(self._data)
        data[prop_name].append(self._wrap(value))
        return FixtureBuilder(data, self.parent, self.location)

    def with_dict(self, prop_name):
        """
        create a child builder to operate on a dict value
        :param prop_name: str
        :return: FixtureBuilder
        """
        if not isinstance(self._data[prop_name], dict):
            raise AttributeError('dict operations are not supported on property {}'.format(prop_name))
        return FixtureBuilder(self._data[prop_name], self, _Location(prop_name))

    def with_dict_list_element(self, prop_name, index=-1):
        """
        create a child builder to work on a list element that is a dict
        :param prop_name: str
        :param index: int
        :return: FixtureBuilder
        """
        if not isinstance(self._data[prop_name], list):
            raise AttributeError('prop {} is not a list'.format(prop_name))
        element = self._data[prop_name][index]
        if not isinstance(element, dict):
            raise AttributeError('dict operations are not supported on list element {} of property {}'.format(index, prop_name))
        return FixtureBuilder(element, self, _Location(prop_name, index))

    def duplicate_last_list_element(self, prop_name):
        """
        duplicates the last list element
        :param prop_name: str
        :return: FixtureBuilder
        """
        data = self._deepcopy(self._data)
        new_element = self._deepcopy(data[prop_name][-1], True)
        data[prop_name].append(new_element)
        return FixtureBuilder(data, self.parent, self.location)

    def done(self):
        """
        finish working on a child builder and return to the parent
        :return: FixtureBuilder
        """
        if self.parent is None:
            raise NotImplementedError('done() is not defined for an empty parent. Maybe you want to access data')
        data = self._deepcopy(self.parent._data)
        if self.location.has_index:
            data[self.location.prop_name][self.location.index] = self._data
        else:
            data[self.location.prop_name] = self._data
        return FixtureBuilder(data, self.parent.parent, self.parent.location)

    def copy(self):
        """
        returns a copy of this FixtureBuilder while getting new values from value creators
        :return:
        """
        if self._parent:
            raise NotImplementedError('creating copy of a non root FixutreBuilder is not supported')
        return FixtureBuilder.create(self._deepcopy(self._data, True))

    def _deepcopy(self, values, call_creators=False):
        if isinstance(values, dict):
            return {key: self._deepcopy(value, call_creators) for key, value in values.items()}
        if isinstance(values, list):
            return [self._deepcopy(value, call_creators) for value in values]
        return values.copy(call_creators)

    def _wrap(self, values):
        if isinstance(values, dict):
            return {key: self._wrap(value) for key, value in values.items()}
        if isinstance(values, list):
            return [self._wrap(value) for value in values]
        if isinstance(values, _Value):
            return values
        return _Value.create(values)

    def _unwrap(self, values):
        if isinstance(values, dict):
            return {key: self._unwrap(value) for key, value in values.items()}
        if isinstance(values, list):
            return [self._unwrap(value) for value in values]
        return values.value


class FixtureCollection(object):
    def __init__(self, fixtures, links):
        self._fixtures = fixtures
        self._links = links

    @staticmethod
    def create():
        return FixtureCollection({}, {})

    @property
    def fixtures(self):
        """
        :return: FixtureBuilder[]
        """
        return self._fixtures

    @property
    def data(self):
        """
        :return: dict all the data inside the collection
        """
        def find_linked_value(definition):
            if definition['linked_value'] == '' and len(self._fixtures[definition['linked_fixture']]) == 1:
                return self._fixtures[definition['linked_fixture']][0].get(definition['linked_field'])

            for fix in self._fixtures[definition['linked_fixture']]:
                value = fix.get(definition['linked_field'])
                if str(value) == str(definition['linked_value']):
                    return value

        d = {}
        for key, builder_list in self._fixtures.items():
            d[key] = []
            for element in builder_list:
                data = element.data
                if key in self._links:
                    for definition in self._links[key]:
                        value = find_linked_value(definition)
                        data[definition['target_field']] = value
                d[key].append(data)
        return d

    def get_fixture(self, name):
        """
        returns a single fixture by name
        :param name:
        :return:
        """
        return self._fixtures[name]

    def add_fixture(self, name, definition):
        """
        adds a new Fixture to the Collection
        :param name: name for the fixture inside the collection
        :param definition: dict|FixtureBuilder definition of the fixture
        :return: FixtureBuilder
        """
        fixtures = self._fixtures_copy()
        if isinstance(definition, FixtureBuilder):
            builder = definition
        else:
            builder = FixtureBuilder.create(definition)
        if name not in fixtures:
            fixtures[name] = []
        fixtures[name].append(builder)
        return FixtureCollection(fixtures, self._links_copy())

    def add_link(self, link_name, linked_field):
        """
        Adds a link between fixtures
        :param link_name: str definition of the link to set up :code:`table_name.field_name`
        :param linked_field: str definition of the field to link to :code:`table_name.field_name=target_value`
        :return: FixtureCollection
        """
        link_name_regexp = '^[a-z0-9_]+\.[a-z0-9_]+$'
        linked_field_regexp = '^[a-z0-9_]+\.[a-z0-9_]+='
        if not re.match(link_name_regexp, link_name, flags=re.IGNORECASE):
            raise ValueError('link_name does not match expected format ({})'.format(link_name_regexp))
        if linked_field.find('=') == -1:
            linked_field += '='
        if not re.match(linked_field_regexp, linked_field):
            raise ValueError('linked_field does not match expected format ({})'.format(link_name_regexp))

        target_fixture, target_field = link_name.split('.')
        link_def, linked_value = linked_field.split('=')
        linked_fixture, linked_field = link_def.split('.')
        links = self._links_copy()
        if target_fixture not in links:
            links[target_fixture] = []
        links[target_fixture].append({
            'target_field': target_field,
            'linked_fixture': linked_fixture,
            'linked_field': linked_field,
            'linked_value': linked_value,
        })
        return FixtureCollection(self._fixtures_copy(), links)

    def _fixtures_copy(self):
        return {key: val for key, val in self._fixtures.items()}

    def _links_copy(self):
        return {key: deepcopy(link) for key, link in self._links.items()}