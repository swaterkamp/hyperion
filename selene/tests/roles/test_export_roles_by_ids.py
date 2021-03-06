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

import string

from uuid import uuid4

from unittest.mock import patch

from selene.tests import SeleneTestCase, GmpMockFactory


@patch('selene.views.Gmp', new_callable=GmpMockFactory)
class ExportRolesByIdsTestCase(SeleneTestCase):
    def setUp(self):
        self.id1 = uuid4()
        self.id2 = uuid4()
        self.roles_mock_xml = f'''
        <get_roles_response status="200" status_text="OK">
          <role id="{self.id1}">
            <owner>
              <name>myuser</name>
            </owner>
            <name>test</name>
            <comment>test</comment>
            <creation_time>2020-09-04T12:53:52Z</creation_time>
            <modification_time>2020-11-10T13:19:36Z</modification_time>
            <writable>1</writable>
            <in_use>0</in_use>
            <permissions>
              <permission>
                <name>Everything</name>
              </permission>
            </permissions>
            <users>hyperion_test_user, myuser</users>
          </role>
          <role id="{self.id2}">
            <owner>
              <name/>
            </owner>
            <name>User</name>
            <comment>Standard user.</comment>
            <creation_time>2020-08-04T19:55:31Z</creation_time>
            <modification_time>2020-08-04T19:55:31Z</modification_time>
            <writable>0</writable>
            <in_use>0</in_use>
            <permissions>
              <permission>
                <name>get_roles</name>
              </permission>
              <permission>
                <name>get_roles</name>
              </permission>
            </permissions>
            <users/>
          </role>
        </get_roles_response>
        '''

    def test_require_authentication(self, _mock_gmp: GmpMockFactory):
        response = self.query(
            f'''
            mutation {{
                exportRolesByIds(ids: ["{self.id1}", "{self.id2}"]) {{
                   exportedEntities
                }}
            }}
            '''
        )

        self.assertResponseAuthenticationRequired(response)

    def test_export_roles_by_ids(self, mock_gmp: GmpMockFactory):
        self.login('foo', 'bar')

        mock_gmp.mock_response('get_roles', self.roles_mock_xml)

        response = self.query(
            f'''
            mutation {{
                exportRolesByIds(ids: ["{self.id1}", "{self.id2}"]) {{
                   exportedEntities
                }}
            }}
            '''
        )

        json = response.json()

        self.assertResponseNoErrors(response)

        roles_xml = json['data']['exportRolesByIds']['exportedEntities']

        self.assertEqual(
            self.roles_mock_xml.translate(
                str.maketrans('', '', string.whitespace)
            ),
            roles_xml.translate(str.maketrans('', '', string.whitespace)),
        )
        mock_gmp.gmp_protocol.get_roles.assert_called_with(
            filter=f'uuid={self.id1} uuid={self.id2} '
        )

    def test_export_empty_ids_array(self, mock_gmp: GmpMockFactory):
        self.login('foo', 'bar')

        mock_gmp.mock_response('get_roles', self.roles_mock_xml)

        response = self.query(
            '''
            mutation {
                exportRolesByIds(ids: []) {
                   exportedEntities
                }
            }
            '''
        )

        json = response.json()

        self.assertResponseNoErrors(response)

        roles_xml = json['data']['exportRolesByIds']['exportedEntities']

        self.assertEqual(
            self.roles_mock_xml.translate(
                str.maketrans('', '', string.whitespace)
            ),
            roles_xml.translate(str.maketrans('', '', string.whitespace)),
        )

        mock_gmp.gmp_protocol.get_roles.assert_called_with(filter='')
