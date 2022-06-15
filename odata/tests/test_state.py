# -*- coding: utf-8 -*-

import unittest

from odata.state import EntityState
from odata.tests import Product, ProductPart


class TestSate(unittest.TestCase):

    def test_new_entity(self):
        uuid = '3d46cd74-a3af-4afd-af94-512b5cee1ef0'

        product = Product()
        product.id = uuid
        product.name = u'Defender'
        product.category = u'Cars'
        product.price = 40000.00

        state = EntityState(product)

        data = dict(state.data_for_insert())

        assert data['ProductID'] == uuid
        assert data['ProductName'] == 'Defender'
        assert data['Category'] == 'Cars'
        assert data['Price'] == 40000.00

        assert state.dirty == []

        product.name = 'Toyota Carola'
        product.price = 32500.00

        data = dict(state.data_for_update())

        assert data['ProductName'] == 'Toyota Carola'
        assert data['Category'] == 'Cars'
        assert data['Price'] == 32500.00
