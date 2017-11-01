

from json import dumps as json_encode
from unittest import TestCase
from copy import deepcopy

from . import FixtureBuilder

DATA = {
    'prop1': 'value1',
    'prop2': 'value2',
    'dict1': {
        'dictprop1': 'dictvalue1'
    },
    'list1': ['listvalue1'],
    'list2': [
        {'listdictprop1': 'listdictvalue1'},
        {'listdictprop2': 'listdictvalue2', 'listdictprop3': 'listdictvalue3'},
    ]
}


class FixtureBuilderTest(TestCase):
    def setUp(self):
        super(FixtureBuilderTest, self).setUp()
        self.builder = FixtureBuilder.create(DATA)

    def test_init_builder(self):
        self.assertDictEqual(DATA, self.builder.data)

    def test_set_property_value_and_return_new_builder_instance(self):
        test_data = deepcopy(DATA)
        test_value = 'newvalue1'
        test_data['prop1'] = test_value
        result = self.builder.set('prop1', test_value)
        self.assertDictEqual(test_data, result.data)
        self.assertIsInstance(result, FixtureBuilder)
        self.assertIsNot(self.builder, result)

    def test_leave_original_builder_unchanged_when_setting_a_property(self):
        test_data = deepcopy(self.builder.data)
        self.builder.set('prop1', 'new value')
        self.assertDictEqual(self.builder.data, test_data)

    def test_raise_error_when_setting_a_missing_property(self):
        with self.assertRaises(KeyError) as context:
            self.builder.set('missing_prop1', 'some value')

    def test_add_element_to_list_and_return_new_builder_instance(self):
        test_data = deepcopy(DATA)
        test_value = 'new value'
        test_data['list1'].append(test_value)
        result = self.builder.add('list1', test_value)
        self.assertDictEqual(test_data, result.data)
        self.assertIsInstance(result, FixtureBuilder)
        self.assertIsNot(self.builder, result)

    def test_leave_original_builder_unchanged_when_adding_an_element_to_a_list(self):
        test_data = deepcopy(self.builder.data)
        self.builder.add('list1', 'new value')
        self.assertDictEqual(self.builder.data, test_data)

    def test_raise_error_when_adding_to_a_missing_list(self):
        with self.assertRaises(KeyError) as context:
            self.builder.add('missing_prop1', 'some_value')

    def test_raise_error_when_adding_to_an_invalid_list(self):
        with self.assertRaises(AttributeError) as context:
            self.builder.add('prop1', 'some_value')

    def test_set_property_on_a_dict_and_return_new_builder_instance(self):
        test_data = deepcopy(DATA)
        test_value = 'new value'
        test_data['dict1']['dictprop1'] = test_value
        result = self.builder.with_dict('dict1').set('dictprop1', test_value).done()
        self.assertIsInstance(result, FixtureBuilder)
        self.assertDictEqual(test_data, result.data)
        self.assertIsNot(self.builder.data, result)

    def test_leave_original_builder_unchanged_when_setting_a_property_on_a_dict(self):
        test_data = deepcopy(self.builder.data)
        self.builder.with_dict('dict1').set('dictprop1', 'new value').done()
        self.assertDictEqual(self.builder.data, test_data)

    def test_raise_error_when_accessing_a_missing_dict(self):
        with self.assertRaises(KeyError) as context:
            self.builder.with_dict('missing_dict').set('dict_prop1', 'new value')

    def test_raise_error_when_accessing_an_invalid_dict(self):
        with self.assertRaises(AttributeError) as context:
            self.builder.with_dict('prop1')

    def test_raise_error_if_calling_done_on_top_level_builder(self):
        with self.assertRaises(NotImplementedError) as context:
            self.builder.done()

    def test_set_property_value_on_last_list_element_and_return_new_builder_instance(self):
        test_data = deepcopy(DATA)
        test_value = 'new value'
        test_data['list2'][1]['listdictprop2'] = test_value
        result = self.builder.with_dict_list_element('list2').set('listdictprop2', test_value).done()
        self.assertIsInstance(result, FixtureBuilder)
        self.assertDictEqual(test_data, result.data)
        self.assertIsNot(self.builder.data, result)

    def test_set_property_value_on_random_list_element_and_return_new_builder_instance(self):
        test_data = deepcopy(DATA)
        test_value = 'new value'
        test_data['list2'][0]['listdictprop1'] = test_value
        result = self.builder.with_dict_list_element('list2', 0).set('listdictprop1', test_value).done()
        self.assertIsInstance(result, FixtureBuilder)
        self.assertDictEqual(test_data, result.data)
        self.assertIsNot(self.builder.data, result)

    def test_raise_error_when_accessing_a_missing_dict_inside_a_list(self):
        with self.assertRaises(IndexError) as context:
            self.builder.with_dict_list_element('list2', 4)

    def test_raise_error_when_accessing_an_invalid_dict_inside_a_list(self):
        with self.assertRaises(AttributeError) as context:
            self.builder.with_dict_list_element('list1')

    def test_raise_error_when_accessing_a_dict_on_an_invalid_list(self):
        with self.assertRaises(AttributeError) as context:
            self.builder.with_dict_list_element('prop1')

    def test_return_builder_data_as_json(self):
        test_data = json_encode(DATA)
        self.assertEqual(self.builder.json, test_data)

    def test_duplicate_the_last_list_element_and_return_a_new_builder_instance(self):
        test_data = deepcopy(DATA)
        test_data['list2'].append(deepcopy(test_data['list2'][-1]))
        result = self.builder.duplicate_last_list_element('list2')
        self.assertIsInstance(result, FixtureBuilder)
        self.assertDictEqual(test_data, result.data)
        self.assertIsNot(self.builder.data, result)
