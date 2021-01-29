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

from uuid import uuid4

from unittest.mock import patch

from selene.tests import SeleneTestCase, GmpMockFactory


@patch('selene.views.Gmp', new_callable=GmpMockFactory)
class ExportTargetsByFilterTestCase(SeleneTestCase):
    def test_require_authentication(self, _mock_gmp: GmpMockFactory):
        response = self.query(
            '''
            mutation {
                exportTargetsByFilter(filterString: "lorem=ipsum") {
                   exportedEntities
                }
            }
            '''
        )

        self.assertResponseAuthenticationRequired(response)

    def test_export_targets_by_filter(self, mock_gmp: GmpMockFactory):
        self.login('foo', 'bar')

        id1 = uuid4()
        id2 = uuid4()
        mock_xml = (
            '<get_targets_response status="200" status_text="OK">'
            f'<target id="{id1}">'
            '<name>some_name1</name>'
            '</target>'
            f'<target id="{id2}">'
            '<name>some_name2</name>'
            '</target>'
            '</get_targets_response>'
        )

        mock_gmp.mock_response('get_targets', bytes(mock_xml, 'utf-8'))

        response = self.query(
            '''
            mutation {
                exportTargetsByFilter
                    (filterString: "uuid={id1} uuid={id2}") {
                   exportedEntities
                }
            }
            '''
        )

        json = response.json()

        self.assertResponseNoErrors(response)

        xml = json['data']['exportTargetsByFilter']['exportedEntities']

        self.assertEqual(mock_xml, xml)
        mock_gmp.gmp_protocol.get_targets.assert_called_with(
            filter="uuid={id1} uuid={id2}"
        )
