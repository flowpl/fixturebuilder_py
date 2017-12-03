

from json import loads as json_decode
from unittest import TestCase
from copy import deepcopy

from datetime import datetime

from faker import Faker

from . import FixtureBuilder, FixtureCollection


class FixtureBuilderTest(TestCase):
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

    def setUp(self):
        super(FixtureBuilderTest, self).setUp()
        self.builder = FixtureBuilder.create(self.DATA)

    def test_init_builder(self):
        self.assertDictEqual(self.DATA, self.builder.data)

    def test_set_property_value_and_return_new_builder_instance(self):
        test_data = deepcopy(self.DATA)
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
        test_data = deepcopy(self.DATA)
        test_value = 'new value'
        test_data['list1'].append(test_value)
        result = self.builder.append('list1', test_value)
        self.assertDictEqual(test_data, result.data)
        self.assertIsInstance(result, FixtureBuilder)
        self.assertIsNot(self.builder, result)

    def test_leave_original_builder_unchanged_when_adding_an_element_to_a_list(self):
        test_data = deepcopy(self.builder.data)
        self.builder.append('list1', 'new value')
        self.assertDictEqual(self.builder.data, test_data)

    def test_raise_error_when_adding_to_a_missing_list(self):
        with self.assertRaises(KeyError) as context:
            self.builder.append('missing_prop1', 'some_value')

    def test_raise_error_when_adding_to_an_invalid_list(self):
        with self.assertRaises(AttributeError) as context:
            self.builder.append('prop1', 'some_value')

    def test_set_property_on_a_dict_and_return_new_builder_instance(self):
        test_data = deepcopy(self.DATA)
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
        test_data = deepcopy(self.DATA)
        test_value = 'new value'
        test_data['list2'][1]['listdictprop2'] = test_value
        result = self.builder.with_dict_list_element('list2').set('listdictprop2', test_value).done()
        self.assertIsInstance(result, FixtureBuilder)
        self.assertDictEqual(test_data, result.data)
        self.assertIsNot(self.builder.data, result)

    def test_set_property_value_on_random_list_element_and_return_new_builder_instance(self):
        test_data = deepcopy(self.DATA)
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
        self.assertEqual(json_decode(self.builder.json), self.DATA)

    def test_duplicate_the_last_list_element_and_return_a_new_builder_instance(self):
        test_data = deepcopy(self.DATA)
        test_data['list2'].append(deepcopy(test_data['list2'][-1]))
        result = self.builder.duplicate_last_list_element('list2')
        self.assertIsInstance(result, FixtureBuilder)
        self.assertDictEqual(test_data, result.data)
        self.assertIsNot(self.builder.data, result)

    def test_add_new_field_using_str(self):
        builder = FixtureBuilder.create({}) \
            .add('prop1', 'some value') \
            .add('prop2', 12345)

        result1 = builder.data
        result2 = builder.data

        self.assertEqual(result1, result2)

    def test_add_new_prop_using_value_generator(self):
        faker = Faker()
        builder = FixtureBuilder.create({}) \
            .add('prop1', faker.address) \
            .add('prop2', faker.random_number)

        result1 = builder.data
        result2 = builder.data

        self.assertEqual(result1, result2)

    def test_set_prop_using_value_generator(self):
        faker = Faker()
        builder = FixtureBuilder.create(self.DATA) \
            .set('prop1', faker.address) \
            .set('prop2', faker.random_number)

        result1 = builder.data
        result2 = builder.data

        self.assertEqual(result1, result2)

    def test_append_value_to_list_using_value_generator(self):
        faker = Faker()
        builder = FixtureBuilder.create(self.DATA) \
            .append('list1', faker.address)

        result1 = builder.data
        result2 = builder.data

        self.assertEqual(result1, result2)

    def test_generate_new_values_from_generator_when_duplicating_list_element(self):
        faker = Faker()
        builder = FixtureBuilder.create({}) \
            .add('list1', []) \
            .append('list1', faker.random_number) \
            .duplicate_last_list_element('list1') \

        element1, element2 = builder.get('list1')
        self.assertNotEqual(element1, element2)

    def test_generate_new_values_from_generator_when_duplicating_dict_list_element(self):
        faker = Faker()
        builder = FixtureBuilder.create({}) \
            .add('list1', []) \
            .append('list1', {'dictprop1': faker.random_number}) \
            .duplicate_last_list_element('list1') \

        element1, element2 = builder.get('list1')
        self.assertNotEqual(element1, element2)

    def test_keep_old_values_when_setting_a_prop(self):
        faker = Faker()
        builder = FixtureBuilder.create({'prop1': faker.random_number, 'prop2': faker.random_number})
        self.assertEqual(builder.data, builder.data)

        new_data = builder.set('prop1', 'newvalue').data
        self.assertEqual(new_data['prop1'], 'newvalue')
        self.assertEqual(new_data['prop2'], builder.get('prop2'))

    def test_keep_old_values_when_adding_a_prop(self):
        faker = Faker()
        builder = FixtureBuilder.create({'prop1': faker.random_number, 'prop2': faker.random_number})
        self.assertEqual(builder.data, builder.data)

        new_data = builder.add('prop3', 'newvalue').data
        self.assertEqual(new_data['prop1'], builder.get('prop1'))
        self.assertEqual(new_data['prop2'], builder.get('prop2'))
        self.assertEqual(new_data['prop3'], 'newvalue')

    def test_copy_fixturebuilder(self):
        faker = Faker()
        builder = FixtureBuilder.create({'prop1': 123, 'prop2': faker.random_number})
        self.assertEqual(builder.data, builder.data)

        builder2 = builder.copy()
        self.assertEqual(builder2.data, builder2.data)
        self.assertEqual(builder.get('prop1'), builder2.get('prop1'))
        self.assertNotEqual(builder.get('prop2'), builder2.get('prop2'))

    def test_raise_not_implemented_error_when_copying_child_builder(self):
        with self.assertRaises(NotImplementedError):
            self.builder.with_dict('dict1').copy()

class FixtureCollectionTest(TestCase):
    DATA1 = {
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

    DATA2 = {
        'attr1': 'attrval1',
        'attr2': 'attrval2',
    }

    def setUp(self):
        self.builder1 = FixtureBuilder.create(self.DATA1)
        self.builder2 = FixtureBuilder.create(self.DATA2)
        self.collection = FixtureCollection.create()

    def test_add_builder_to_collection(self):
        new_collection = self.collection.add_fixture('table1', self.builder1)
        self.assertDictEqual({}, self.collection.fixtures)
        self.assertEqual([self.builder1], new_collection.get_fixture('table1'))

    def test_add_data_to_collection(self):
        new_collection = self.collection.add_fixture('table1', self.DATA1)
        self.assertDictEqual({}, self.collection.fixtures)
        self.assertEqual(self.DATA1, new_collection.get_fixture('table1')[0].data)

    def test_add_multiple_builders_to_collection(self):
        new_collection = self.collection \
            .add_fixture('table1', self.builder1) \
            .add_fixture('table2', self.builder2)
        self.assertEqual(new_collection.get_fixture('table1'), [self.builder1])
        self.assertEqual(new_collection.get_fixture('table2'), [self.builder2])

    def test_add_multiple_rows_to_single_fixture(self):
        second_row = self.builder1.set('prop1', 'anothervalue')
        new_collection = self.collection \
            .add_fixture('table1', self.builder1) \
            .add_fixture('table1', second_row)
        self.assertEqual(new_collection.get_fixture('table1'), [self.builder1, second_row])

    def test_get_fixture_data(self):
        data = self.collection \
            .add_fixture('table1', self.builder1) \
            .add_fixture('table2', self.builder2) \
            .data
        self.assertDictEqual(
            {
                'table1': [self.DATA1],
                'table2': [self.DATA2],
            },
            data
        )

    def test_create_link_between_fixtures(self):
        data = self.collection \
            .add_fixture('table1', self.builder1) \
            .add_fixture('table2', self.builder2) \
            .add_link('table2.table1_id', 'table1.prop1=') \
            .data
        result_data = deepcopy(self.DATA2)
        result_data['table1_id'] = self.DATA1['prop1']
        self.assertDictEqual(
            {
                'table1': [self.DATA1],
                'table2': [result_data],
            },
            data
        )

    def test_create_multiple_links_between_fixtures(self):
        data = self.collection \
            .add_fixture('table1', self.builder1) \
            .add_fixture('table2', self.builder2) \
            .add_link('table2.table1_id', 'table1.prop1') \
            .add_link('table2.table1_second_id', 'table1.prop2') \
            .data
        result_data = deepcopy(self.DATA2)
        result_data['table1_id'] = self.DATA1['prop1']
        result_data['table1_second_id'] = self.DATA1['prop2']
        self.assertDictEqual(
            {
                'table1': [self.DATA1],
                'table2': [result_data],
            },
            data
        )

    def test_create_links_between_fixtures_in_lists(self):
        second_row = self.builder1.set('prop1', 'anothervalue')
        data = self.collection \
            .add_fixture('table1', self.builder1) \
            .add_fixture('table1', second_row) \
            .add_fixture('table2', self.builder2) \
            .add_link('table2.table1_id', 'table1.prop1=anothervalue') \
            .data
        result_data = deepcopy(self.DATA2)
        result_data['table1_id'] = second_row.get('prop1')
        self.assertDictEqual(
            {
                'table1': [self.DATA1, second_row.data],
                'table2': [result_data],
            },
            data
        )

    def test_create_links_between_fixtures_in_lists_when_the_target_is_int(self):
        second_row = self.builder1.set('prop1', 12)
        data = self.collection \
            .add_fixture('table1', self.builder1) \
            .add_fixture('table1', second_row) \
            .add_fixture('table2', self.builder2) \
            .add_link('table2.table1_id', 'table1.prop1=12') \
            .data
        result_data = deepcopy(self.DATA2)
        result_data['table1_id'] = second_row.get('prop1')
        self.assertDictEqual(
            {
                'table1': [self.DATA1, second_row.data],
                'table2': [result_data],
            },
            data
        )

    def test_create_links_between_fixtures_in_lists_when_the_target_is_float(self):
        second_row = self.builder1.set('prop1', 12.4)
        data = self.collection \
            .add_fixture('table1', self.builder1) \
            .add_fixture('table1', second_row) \
            .add_fixture('table2', self.builder2) \
            .add_link('table2.table1_id', 'table1.prop1=12.4') \
            .data
        result_data = deepcopy(self.DATA2)
        result_data['table1_id'] = second_row.get('prop1')
        self.assertDictEqual(
            {
                'table1': [self.DATA1, second_row.data],
                'table2': [result_data],
            },
            data
        )

    def test_create_links_between_fixtures_in_lists_when_the_target_is_boolean(self):
        second_row = self.builder1.set('prop1', True)
        data = self.collection \
            .add_fixture('table1', self.builder1) \
            .add_fixture('table1', second_row) \
            .add_fixture('table2', self.builder2) \
            .add_link('table2.table1_id', 'table1.prop1=True') \
            .data
        result_data = deepcopy(self.DATA2)
        result_data['table1_id'] = second_row.get('prop1')
        self.assertDictEqual(
            {
                'table1': [self.DATA1, second_row.data],
                'table2': [result_data],
            },
            data
        )

    def test_create_links_between_fixtures_in_lists_when_the_target_is_datetime(self):
        second_row = self.builder1.set('prop1', datetime.strptime('2017-02-01 04:05:06', '%Y-%m-%d %H:%M:%S'))
        data = self.collection \
            .add_fixture('table1', self.builder1) \
            .add_fixture('table1', second_row) \
            .add_fixture('table2', self.builder2) \
            .add_link('table2.table1_id', 'table1.prop1=2017-02-01 04:05:06') \
            .data
        result_data = deepcopy(self.DATA2)
        result_data['table1_id'] = second_row.get('prop1')
        self.assertDictEqual(
            {
                'table1': [self.DATA1, second_row.data],
                'table2': [result_data],
            },
            data
        )

    def test_raise_value_error_if_link_name_is_invalid(self):
        with self.assertRaises(ValueError):
            self.collection.add_link('something', 'table1.value1=67')

    def test_raise_value_error_if_linked_field_is_invalid(self):
        with self.assertRaises(ValueError):
            self.collection.add_link('table2.field1', 'invalid')
