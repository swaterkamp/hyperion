# -*- coding: utf-8 -*-
# Copyright (C) 2020-2021 Greenbone Networks GmbH
#
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from unittest.mock import patch

from gvm.protocols.next import AssetType

from selene.tests import SeleneTestCase, GmpMockFactory

from selene.tests.pagination import (
    make_test_counts,
    make_test_after_first,
    make_test_page_info,
    make_test_edges,
    make_test_before_last,
    make_test_after_first_before_last,
)
from selene.tests.entity import make_test_get_entities

from selene.schema.operating_systems.queries import GetOperatingSystems


@patch('selene.views.Gmp', new_callable=GmpMockFactory)
class OperatingSystemsTestCase(SeleneTestCase):
    def test_require_authentication(self, _mock_gmp: GmpMockFactory):
        response = self.query(
            '''
            query {
                operatingSystems {
                    nodes {
                        id
                        name
                    }
                }
            }
            '''
        )

        self.assertResponseAuthenticationRequired(response)

    def test_get_operating_systems(self, mock_gmp: GmpMockFactory):
        mock_gmp.mock_response(
            'get_assets',
            '''
            <get_assets_response>
                <asset id="15085a9a-3d24-11ea-944a-6f78adc016ea">
                    <name>a</name>
                </asset>
                <asset id="230f47a2-3d24-11ea-bd0b-db49f50db5ae">
                    <name>b</name>
                </asset>
            </get_assets_response>
            ''',
        )

        self.login('foo', 'bar')

        response = self.query(
            '''
            query {
                operatingSystems {
                    nodes {
                        id
                        name
                    }
                }
            }
            '''
        )

        json = response.json()

        self.assertResponseNoErrors(response)

        operating_systems = json['data']['operatingSystems']['nodes']

        self.assertEqual(len(operating_systems), 2)

        operating_system1 = operating_systems[0]
        operating_system2 = operating_systems[1]

        self.assertEqual(operating_system1['name'], 'a')
        self.assertEqual(
            operating_system1['id'], '15085a9a-3d24-11ea-944a-6f78adc016ea'
        )
        self.assertEqual(operating_system2['name'], 'b')
        self.assertEqual(
            operating_system2['id'], '230f47a2-3d24-11ea-bd0b-db49f50db5ae'
        )

    def test_get_filtered_operating_systems(self, mock_gmp: GmpMockFactory):
        mock_gmp.mock_response(
            'get_assets',
            '''
            <get_assets_response>
                <asset id="f650a1c0-3d23-11ea-8540-e790e17c1b00">
                    <name>a</name>
                </asset>
                <asset id="0778ac90-3d24-11ea-b722-fff755412c48">
                    <name>b</name>
                </asset>
            </get_assets_response>
            ''',
        )

        self.login('foo', 'bar')

        response = self.query(
            '''
            query {
                operatingSystems (
                    filterString: "lorem",
                ) {
                    nodes {
                        id
                        name
                    }
                }
            }
            '''
        )

        json = response.json()

        self.assertResponseNoErrors(response)

        operating_systems = json['data']['operatingSystems']['nodes']

        self.assertEqual(len(operating_systems), 2)

        operating_system1 = operating_systems[0]
        operating_system2 = operating_systems[1]

        self.assertEqual(operating_system1['name'], 'a')
        self.assertEqual(
            operating_system1['id'], 'f650a1c0-3d23-11ea-8540-e790e17c1b00'
        )
        self.assertEqual(operating_system2['name'], 'b')
        self.assertEqual(
            operating_system2['id'], '0778ac90-3d24-11ea-b722-fff755412c48'
        )


class OperatingSystemsPaginationTestCase(SeleneTestCase):
    entity_name = 'asset'
    selene_name = 'operatingSystem'
    test_pagination_with_after_and_first = make_test_after_first(
        entity_name,
        selene_name=selene_name,
        asset_type=AssetType.OPERATING_SYSTEM,
    )
    test_counts = make_test_counts(entity_name, selene_name=selene_name)
    test_page_info = make_test_page_info(
        entity_name, selene_name=selene_name, query=GetOperatingSystems
    )
    test_edges = make_test_edges(entity_name, selene_name=selene_name)
    test_pagination_with_before_and_last = make_test_before_last(
        entity_name,
        selene_name=selene_name,
        asset_type=AssetType.OPERATING_SYSTEM,
    )
    test_after_first_before_last = make_test_after_first_before_last(
        entity_name,
        selene_name=selene_name,
        asset_type=AssetType.OPERATING_SYSTEM,
    )


class OperatingSystemGetEntitiesTestCase(SeleneTestCase):
    gmp_name = 'asset'
    selene_name = 'operatingSystem'
    test_get_entities = make_test_get_entities(
        gmp_name, selene_name=selene_name, asset_type=AssetType.OPERATING_SYSTEM
    )
