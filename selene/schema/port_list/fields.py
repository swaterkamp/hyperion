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

import graphene

from gvm.protocols.next import PortRangeType as GvmPortRangeType

from selene.schema.base import BaseObjectType
from selene.schema.entity import EntityObjectType

from selene.schema.parser import parse_uuid

from selene.schema.resolver import find_resolver

from selene.schema.utils import get_text_from_element, get_int_from_element


class PortRangeType(graphene.Enum):
    """PortRange type. Either TCP or UDP"""

    class Meta:
        enum = GvmPortRangeType


class PortRange(graphene.ObjectType):
    """A range of ports in a port list"""

    uuid = graphene.UUID(name='id', description='ID of the port range')
    start = graphene.Int(description='Starting port of the range')
    end = graphene.Int(description='Ending port of the range')
    port_range_type = graphene.Field(
        PortRangeType, name='type', description='Type of the port range'
    )

    @staticmethod
    def resolve_uuid(root, _info):
        return parse_uuid(root.get('id'))

    @staticmethod
    def resolve_start(root, _info):
        return get_int_from_element(root, 'start')

    @staticmethod
    def resolve_end(root, _info):
        return get_int_from_element(root, 'end')

    @staticmethod
    def resolve_port_range_type(root, _info):
        type_string: str = get_text_from_element(root, 'type')
        if not type_string:
            return None

        return type_string.upper()


class PortCount(graphene.ObjectType):
    """Aggregation of ports counts"""

    count_all = graphene.Int(
        name='all', description='Total number of ports'
    )  # 'all' is a built-in python method
    tcp = graphene.Int(description='Number of TCP ports')
    udp = graphene.Int(description='Number of UDP ports')

    @staticmethod
    def resolve_count_all(root, _info):
        return get_int_from_element(root, 'all')

    @staticmethod
    def resolve_tcp(root, _info):
        return get_int_from_element(root, 'tcp')

    @staticmethod
    def resolve_udp(root, _info):
        return get_int_from_element(root, 'udp')


class PortListTarget(BaseObjectType):
    """A target referenced by a PortList"""


class PortList(EntityObjectType):
    """A list of ports to scan"""

    class Meta:
        default_resolver = find_resolver

    port_ranges = graphene.List(
        PortRange, description="Port ranges in this port list"
    )
    port_count = graphene.Field(PortCount, description="Summary of ports")
    targets = graphene.List(
        PortListTarget, description="Targets using this port list"
    )

    @staticmethod
    def resolve_port_ranges(root, _info):
        port_ranges = root.find('port_ranges')
        if port_ranges is None or len(port_ranges) == 0:
            return None
        return port_ranges.findall('port_range')

    @staticmethod
    def resolve_targets(root, _info):
        targets = root.find('targets')
        if targets is None or len(targets) == 0:
            return None
        return targets.findall('target')
