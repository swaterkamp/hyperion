# -*- coding: utf-8 -*-
# Copyright (C) 2019-2020 Greenbone Networks GmbH
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

from uuid import UUID

import graphene

from graphql import ResolveInfo
from gvm.protocols.next import AssetType

from selene.schema.operating_systems.fields import OperatingSystem

from selene.schema.parser import FilterString

from selene.schema.relay import (
    EntityConnectionField,
    Entities,
    get_filter_string_for_pagination,
)

from selene.schema.utils import get_gmp, require_authentication, XmlElement


class GetOperatingSystem(graphene.Field):
    """Gets a single operating system.

    Args:
        id (UUID): UUID of the operating system being queried

    Example:

        .. code-block::

            query {
                operatingSystem (id: "4846b497-936b-4816-aa4a-1a997cf9ab8d"){
                        id
                        name
                }
            }

        Response:

        .. code-block::

            {
                "data": {
                    "operatingSystem": {
                        "id": "4846b497-936b-4816-aa4a-1a997cf9ab8d",
                        "name": "foo"
                    }
                }
            }

    """

    def __init__(self):
        super().__init__(
            OperatingSystem,
            operating_system_id=graphene.UUID(required=True, name='id'),
            resolver=self.resolve,
        )

    @staticmethod
    @require_authentication
    def resolve(_root, info, operating_system_id: UUID):
        gmp = get_gmp(info)

        xml = gmp.get_asset(
            str(operating_system_id), asset_type=AssetType.OPERATING_SYSTEM
        )
        return xml.find('asset')


class GetOperatingSystems(EntityConnectionField):
    """Gets a list of operating systems with pagination

    Args:
        filter_string (str, optional): Optional filter string to be
            used with query.

    Example:

        .. code-block::

            query {
                operatingSystems (filterString: "name~Foo rows=2") {
                    nodes {
                        id
                        name
                    }
                }
            }

        Response:

        .. code-block::

            {
                "data": {
                    "operatingSystems": {
                        "nodes": [
                            {
                                "id": "1fb47870-47ce-4b9f-a8f9-8b4b19624c59",
                                "name": "Foo"
                            },
                            {
                                "id": "5d07b6eb-27f9-424a-a206-34babbba7b4d",
                                "name": "Foo Bar"
                            },
                        ]
                    }
                }
            }

    """

    entity_type = OperatingSystem

    @staticmethod
    @require_authentication
    def resolve_entities(  # pylint: disable=arguments-differ
        _root,
        info: ResolveInfo,
        filter_string: FilterString = None,
        after: str = None,
        before: str = None,
        first: int = None,
        last: int = None,
    ) -> Entities:
        gmp = get_gmp(info)

        filter_string = get_filter_string_for_pagination(
            filter_string, first=first, last=last, after=after, before=before
        )

        xml: XmlElement = gmp.get_assets(
            asset_type=AssetType.OPERATING_SYSTEM,
            filter=filter_string.filter_string,
        )

        asset_elements = xml.findall('asset')
        counts = xml.find('asset_count')
        requested = xml.find('assets')

        return Entities(asset_elements, counts, requested)
