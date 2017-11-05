
fixturebuilder_py
=================


Install
-------

.. code-block:: bash

    $ pip install fixturebuilder


Usage
-----

.. code-block:: python

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
