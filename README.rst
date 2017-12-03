
fixturebuilder_py
=================

Library to generate test data to use as database fixtures
and provide simple syntax to set the database to it's initial state at the start of each test.

The library provides two main components:

FixtureBuilder: a simple builder to configure the contents of a single table
FixtureCollection: a builder to combine multiple FixtureBuilders to a complete database setup, including foreign key relationships.


Design goals
------------

Immutablility
^^^^^^^^^^^^^
Test data should always be completely isolated.
Changes to a dataset should only affect a single use, without any effects on other uses.

Easy setup of complex schemas
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Example data for different test cases oftentimes only differs in a couple of values.
The bulk of the example values can be random values or even identical throughout testcases.
With traditional tools the developer has to do a lot of busy work to maintain example data.
Fixturebuilder aims to provide a simple interface that only requires to maintain the values that actually matter.

Interoperability
^^^^^^^^^^^^^^^^
It should be easy to integrate fixturebuilder into existing tool chains.



Installt
-------

.. code-block:: bash

    $ pip install fixturebuilder


Usage FixtureBuilder
--------------------

.. code-block:: python

    from fixturebuilder import FixtureBuilder

    # define the data structure to be worked on
    start_data = {
        'prop1': 'value1',
        'prop2': 'value2',
        'dict1': {
            'dictprop1': 'dictvalue1'
        },
        'list1': [
            'listvalue1',
            'listvalue2'
        ],
        'list2': [
            {'listdictprop1': 'listdictprop1', 'listdictlist1': ['listdictlistvalue1']}
        ]
    }

    # initialize a new builder
    builder = FixtureBulder.create(start_data)

    # retrieve the data unchanged
    test_data1 = builder.data

    # set a new value on a property and retrieve the updated data
    test_data2 = builder.set('prop1', 1).data

    # do complex manipulation on the start_data and retrieve the modified data
    test_data3 = builder
        .with_dict('dict1')  # descend into 'dict1' and work on it's properties
            .set('dictprop1', 12)
            .set('newlist', ['value'])
            .add('newlist', 'additional value')  # add a new value to a list
            .set('newdict', {'someprop': 'some value'})
            .with_dict('newdict')
                .set('someprop', 'change previously created value')
            .done()  # finish working on 'newdict' and return to 'dict1'
        .done()  # finish working on 'dict1' and return to the root
        .data


    test_data4 = builder
        .duplicate_last_list_entry('list2')  # append a duplicated dict to the list
        .with_dict_list_element('list2')     # descend into the last list element to work on it's properties
            .add('listdictlist1', 'new value1')
            .set('listdictprop1', False)
        .done()  # finish working on the list element and return to the root
        .data

    # retrieve the original unmodified data
    original_data = builder.data

    # setting new property raises an error
    builder.set('newprop', 'newvalue')

    # adding a new property adds it to the builder's data structure
    builder.add('newprop', 'newvalue')


Usage FixtureCollection
-----------------------

.. code-block:: python

    from fixturebuilder import FixtureBuilder, FixtureCollection

    # define the data structure to be worked on
    table1 = {
        'id': 10,
        'prop1': 'value1',
        'prop2': 'value2',
    }

    table2 = {
        'id': 20,
        'attr1': 'attrval1',
        'attr2': 'attrval2',
    }

    builder1 = FixtureBuilder.create(table1)
    builder2 = FixtureBuilder.create(table2)

    collection = FixtureCollection.create() \
        .add_fixture('table1', builder1) \
        .add_fixture('table2', builder2) \
        .add_link('table2.table1_id', 'table1.id=1')

    # get the raw data represented by this collection
    print(collection.data)
    # get the raw data for a single fixture. All links are resolved to their actual values
    print(collection.get_fixture('table2').data)
