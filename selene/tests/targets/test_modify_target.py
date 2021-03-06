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

from selene.schema.targets.fields import AliveTest

from selene.tests import SeleneTestCase, GmpMockFactory


@patch('selene.views.Gmp', new_callable=GmpMockFactory)
class ModifyTargetTestCase(SeleneTestCase):
    def setUp(self):
        self.target_id = uuid4()
        self.ssh_credential_id = uuid4()
        self.snmp_credential_id = uuid4()
        self.esxi_credential_id = uuid4()
        self.smb_credential_id = uuid4()
        self.port_list_id = uuid4()

    def test_require_authentication(self, _mock_gmp: GmpMockFactory):
        response = self.query(
            f'''
            mutation {{
                modifyTarget(input: {{
                    id: "{self.target_id}",
                }}) {{
                    ok
                }}
            }}
            '''
        )

        self.assertResponseAuthenticationRequired(response)

    def test_modify_target(self, mock_gmp: GmpMockFactory):
        mock_gmp.mock_response(
            'modify_target',
            '''
            <modify_target_response status="200" status_text="OK"/>
            ''',
        )

        self.login('foo', 'bar')

        response = self.query(
            f'''
            mutation {{
                modifyTarget(input: {{
                    id: "{self.target_id}",
                    name: "bar",
                    hosts: ["127.0.0.1", "192.168.10.130"],
                    credentials: {{
                        ssh: {{
                            id: "{self.ssh_credential_id}",
                            port: 33,
                        }},
                        smb: {{
                            id: "{self.smb_credential_id}",
                        }},
                        snmp: {{
                            id: "{self.snmp_credential_id}",
                        }}
                        esxi: {{
                            id: "{self.esxi_credential_id}",
                        }},

                    }},
                    aliveTest: ICMP_PING,
                    allowSimultaneousIPs: false,
                    reverseLookupUnify: false,
                }}) {{
                    ok
                }}
            }}
            '''
        )

        json = response.json()

        self.assertResponseNoErrors(response)

        ok = json['data']['modifyTarget']['ok']

        self.assertEqual(ok, True)

        mock_gmp.gmp_protocol.modify_target.assert_called_with(
            str(self.target_id),
            alive_test=AliveTest.ICMP_PING,  # pylint: disable=no-member
            hosts=['127.0.0.1', '192.168.10.130'],
            exclude_hosts=None,
            comment=None,
            ssh_credential_id=str(self.ssh_credential_id),
            ssh_credential_port=33,
            smb_credential_id=str(self.smb_credential_id),
            snmp_credential_id=str(self.snmp_credential_id),
            esxi_credential_id=str(self.esxi_credential_id),
            allow_simultaneous_ips=False,
            name="bar",
            reverse_lookup_only=None,
            reverse_lookup_unify=False,
            port_list_id=None,
        )

    def test_modify_target_alive_test(self, mock_gmp: GmpMockFactory):
        mock_gmp.mock_response(
            'modify_target',
            '''
            <modify_target_response status="200" status_text="OK" />
            ''',
        )

        self.login('foo', 'bar')

        response = self.query(
            f'''
            mutation {{
                modifyTarget(input: {{
                    id: "{self.target_id}",
                    name: "bar",
                    aliveTest: SCAN_CONFIG_DEFAULT,
                }}) {{
                    ok
                }}
            }}
            '''
        )

        json = response.json()

        self.assertResponseNoErrors(response)

        ok = json['data']['modifyTarget']['ok']

        self.assertEqual(ok, True)

        mock_gmp.gmp_protocol.modify_target.assert_called_with(
            str(self.target_id),
            alive_test=AliveTest.SCAN_CONFIG_DEFAULT,  # pylint: disable=no-member
            hosts=None,
            exclude_hosts=None,
            comment=None,
            ssh_credential_id=None,
            name="bar",
            ssh_credential_port=None,
            smb_credential_id=None,
            snmp_credential_id=None,
            esxi_credential_id=None,
            allow_simultaneous_ips=None,
            reverse_lookup_only=None,
            reverse_lookup_unify=None,
            port_list_id=None,
        )

    def test_modify_target_port_list(self, mock_gmp: GmpMockFactory):
        mock_gmp.mock_response(
            'modify_target',
            '''
            <modify_target_response status="200" status_text="OK"/>
            ''',
        )

        self.login('foo', 'bar')

        response = self.query(
            f'''
            mutation {{
                modifyTarget(input: {{
                    id: "{self.target_id}",
                    name: "bar",
                    portListId: "{str(self.port_list_id)}"
                }}) {{
                    ok
                }}
            }}
            '''
        )

        json = response.json()

        self.assertResponseNoErrors(response)

        ok = json['data']['modifyTarget']['ok']

        self.assertEqual(ok, True)

        mock_gmp.gmp_protocol.modify_target.assert_called_with(
            str(self.target_id),
            alive_test=None,
            hosts=None,
            exclude_hosts=None,
            comment=None,
            name="bar",
            ssh_credential_id=None,
            ssh_credential_port=None,
            smb_credential_id=None,
            snmp_credential_id=None,
            esxi_credential_id=None,
            allow_simultaneous_ips=None,
            reverse_lookup_only=None,
            reverse_lookup_unify=None,
            port_list_id=str(self.port_list_id),
        )

    def test_modify_target_allow_simultaneous_ips(
        self, mock_gmp: GmpMockFactory
    ):
        mock_gmp.mock_response(
            'modify_target',
            '''
            <modify_target_response status="200" status_text="OK" />
            ''',
        )

        self.login('foo', 'bar')

        response = self.query(
            f'''
            mutation {{
                modifyTarget(input: {{
                    id: "{self.target_id}",
                    name: "bar",
                    allowSimultaneousIPs: true,
                }}) {{
                    ok
                }}
            }}
            '''
        )

        json = response.json()

        self.assertResponseNoErrors(response)

        ok = json['data']['modifyTarget']['ok']

        self.assertEqual(ok, True)

        mock_gmp.gmp_protocol.modify_target.assert_called_with(
            str(self.target_id),
            alive_test=None,
            hosts=None,
            exclude_hosts=None,
            comment=None,
            ssh_credential_id=None,
            name="bar",
            ssh_credential_port=None,
            smb_credential_id=None,
            snmp_credential_id=None,
            esxi_credential_id=None,
            allow_simultaneous_ips=True,
            reverse_lookup_only=None,
            reverse_lookup_unify=None,
            port_list_id=None,
        )

    def test_ssh_credential_port_without_credential_id(
        self, mock_gmp: GmpMockFactory
    ):
        mock_gmp.mock_response(
            'modify_target',
            f'''
            <modify_target_response
                id="{self.target_id}"
                status="200"
                status_text="OK"
            />
            ''',
        )

        self.login('foo', 'bar')

        response = self.query(
            f'''
            mutation {{
                modifyTarget(input: {{
                    id: "{self.target_id}",
                    name: "bar",
                    hosts: ["127.0.0.1"],
                    credentials: {{
                        ssh: {{
                            port: 22,
                        }}
                    }}
                    portListId: "{self.port_list_id}"
                    aliveTest: ICMP_PING,
                }}) {{
                   ok
                }}
            }}
            '''
        )

        self.assertResponseHasErrorMessage(
            response,
            "Setting a SSH credential port requires a SSH credential id",
        )
