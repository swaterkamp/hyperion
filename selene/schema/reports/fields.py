# -*- coding: utf-8 -*-
# Copyright (C) 2019-2021 Greenbone Networks GmbH
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

from selene.schema.resolver import text_resolver, int_resolver
from selene.schema.base import BaseObjectType
from selene.schema.entity import EntityUserTags
from selene.schema.severity import SeverityType

from selene.schema.utils import (
    get_text,
    get_owner,
    get_boolean_from_element,
    get_datetime_from_element,
    get_int_from_element,
    get_text_from_element,
)
from selene.schema.parser import parse_uuid, parse_int
from selene.schema.tasks.fields import Task
from selene.schema.results.queries import Result
from selene.schema.hosts.fields import ReportHost
from selene.schema.nvts.fields import ScanConfigNVT
from selene.schema.permissions.fields import Permission


class CountType(graphene.ObjectType):
    class Meta:
        default_resolver = int_resolver

    total = graphene.Int()
    filtered = graphene.Int()
    current = graphene.Int()

    @staticmethod
    def resolve_total(root, _info):
        return get_int_from_element(root, 'full')

    @staticmethod
    def resolve_current(root, _info):
        _current = get_int_from_element(root, 'count')
        if _current is None:
            return parse_int(root.text)
        return _current


class ReportSeverity(graphene.ObjectType):
    class Meta:
        default_resolver = text_resolver

    total = SeverityType()
    filtered = SeverityType()

    @staticmethod
    def resolve_total(root, _info):
        return get_text_from_element(root, 'full')


class ReportResultCount(CountType):
    class Meta:
        default_resolver = int_resolver

    high = graphene.Field(CountType)
    info = graphene.Field(CountType)
    log = graphene.Field(CountType)
    warning = graphene.Field(CountType)
    false_positive = graphene.Field(CountType)

    @staticmethod
    def resolve_high(root, _info):
        return root.find('hole')

    @staticmethod
    def resolve_info(root, _info):
        return root.find('info')

    @staticmethod
    def resolve_log(root, _info):
        return root.find('log')

    @staticmethod
    def resolve_warning(root, _info):
        return root.find('warning')

    @staticmethod
    def resolve_false_positive(root, _info):
        return root.find('false_positive')


class ReportEntities(graphene.ObjectType):
    """Report entities object type. Is part of the Report object.
    Includes the counts for the corresponding entities.
    """

    counts = graphene.Field(CountType)

    @staticmethod
    def resolve_counts(root, _info):
        return root


class ReportPort(graphene.ObjectType):
    """Port object type. Is part of the Result object."""

    class Meta:
        default_resolver = text_resolver

    port = graphene.String()
    host = graphene.String()
    severity = SeverityType()
    threat = graphene.String()

    @staticmethod
    def resolve_port(root, _info):
        return get_text(root)


class DeltaReport(graphene.ObjectType):
    """DeltaReport object type. Is part of the Delta object."""

    uuid = graphene.UUID(name='id')
    scan_run_status = graphene.String()

    timestamp = graphene.DateTime()

    scan_start = graphene.DateTime()
    scan_end = graphene.DateTime()

    @staticmethod
    def resolve_uuid(root, _info):
        return root.get('id')

    @staticmethod
    def resolve_scan_run_status(root, _info):
        return get_text_from_element(root, 'scan_run_status')

    @staticmethod
    def resolve_timestamp(root, _info):
        return get_datetime_from_element(root, 'timestamp')

    @staticmethod
    def resolve_scan_start(root, _info):
        return get_datetime_from_element(root, 'scan_start')

    @staticmethod
    def resolve_scan_end(root, _info):
        return get_datetime_from_element(root, 'scan_end')


class ErrorHost(graphene.ObjectType):
    """ErrorHost object type. Is part of the Error object."""

    name = graphene.String()
    asset_id = graphene.UUID(name="id")

    @staticmethod
    def resolve_name(root, _info):
        return get_text(root)

    @staticmethod
    def resolve_asset_id(root, _info):
        asset = root.find('asset')
        return parse_uuid(asset.get('asset_id'))


class Error(graphene.ObjectType):
    """Error object type. Is part of the Report object."""

    host = graphene.Field(ErrorHost)
    port = graphene.String()
    description = graphene.String()
    nvt = graphene.Field(ScanConfigNVT)
    scan_nvt_version = graphene.DateTime(
        description='Used Version of the NVT for this scan (modification date)'
    )
    severity = SeverityType()

    @staticmethod
    def resolve_host(root, _info):
        return root.find('host')

    @staticmethod
    def resolve_port(root, _info):
        return get_text_from_element(root, 'port')

    @staticmethod
    def resolve_description(root, _info):
        return get_text_from_element(root, 'description')

    @staticmethod
    def resolve_nvt(root, _info):
        return root.find('nvt')

    @staticmethod
    def resolve_scan_nvt_version(root, _info):
        return get_datetime_from_element(root, 'scan_nvt_version')

    @staticmethod
    def resolve_severity(root, _info):
        return get_text_from_element(root, 'severity')


class ReportModel:
    """
    The XML Report format contains an inner Report element
    To avoid finding the inner element frequently to gather
    its information we save a second XML-Tree in this class
    """

    def __init__(self):
        self.outer_report = None
        self.inner_report = None


class Report(graphene.ObjectType):
    """
    The Report object type. It can be accessed with getReport()
    and getReports(). It contains some general Report information

    Args:
        timestamp (DateTime): Timestamp for this report
        timezone (str): Timezone
        timezone_abbreviation (str)
        port_count (List(TaskAlert)): Port count
        ports (List(Port)): Ports involved in this report
        permissions (List(Permissions)): Permissions for this report
        result_count (ResultCount): Result count
        results (List(Results)): Results in this report
        severity (Severity):
        host (Host): Host for this report
        scan_start (DateTime)
        scan_end (DateTime)
        error_count (int): Error count
        errors = (List(Error)): Errors occurred
        report_format (str): Format from this report
    """

    uuid = graphene.UUID(name='id')
    name = graphene.String()

    owner = graphene.String()
    comment = graphene.String()
    report_format = graphene.Field(BaseObjectType)

    creation_time = graphene.DateTime()
    modification_time = graphene.DateTime()

    writable = graphene.Boolean()
    in_use = graphene.Boolean()

    task = graphene.Field(Task, description="The task for this report")

    delta_report = graphene.Field(
        DeltaReport, description="The delta report information"
    )

    user_tags = graphene.Field(EntityUserTags)

    scan_run_status = graphene.String(description="Scan status of report")
    scan_start = graphene.DateTime()
    scan_end = graphene.DateTime()

    hosts_count = graphene.Field(CountType, description="Host counts")
    hosts = graphene.List(ReportHost, description="The hosts for this report")

    closed_cves = graphene.Field(ReportEntities, description="Closed CVE count")
    vulnerabilities = graphene.Field(
        ReportEntities, description="Vulnerability count"
    )
    operating_systems = graphene.Field(
        ReportEntities, description="Operating system count"
    )
    applications = graphene.Field(
        ReportEntities, description="Application count"
    )
    tls_certificates = graphene.Field(
        ReportEntities, description="TLS certificate count"
    )

    ports_count = graphene.Field(CountType, description="Port counts")
    ports = graphene.List(ReportPort, description="The ports in this report")

    results_count = graphene.Field(
        ReportResultCount, description="Result counts"
    )
    results = graphene.List(Result, description="The results for this report")

    severity = graphene.Field(ReportSeverity)

    error_count = graphene.Field(CountType)
    errors = graphene.List(Error)

    permissions = graphene.List(Permission)

    timestamp = graphene.DateTime()
    timezone = graphene.String()
    timezone_abbreviation = graphene.String()

    uuid = graphene.UUID(name='id')
    name = graphene.String()

    @staticmethod
    def resolve_uuid(root, _info):
        return parse_uuid(root.outer_report.get('id'))

    @staticmethod
    def resolve_name(root, _info):
        return get_text_from_element(root.outer_report, 'name')

    @staticmethod
    def resolve_owner(root, _info):
        return get_owner(root.outer_report)

    @staticmethod
    def resolve_comment(root, _info):
        return get_text_from_element(root.outer_report, 'comment')

    @staticmethod
    def resolve_creation_time(root, _info):
        return get_datetime_from_element(root.outer_report, 'creation_time')

    @staticmethod
    def resolve_modification_time(root, _info):
        return get_datetime_from_element(root.outer_report, 'modification_time')

    @staticmethod
    def resolve_writable(root, _info):
        return get_boolean_from_element(root.outer_report, 'writable')

    @staticmethod
    def resolve_in_use(root, _info):
        return get_boolean_from_element(root.outer_report, 'in_use')

    @staticmethod
    def resolve_user_tags(root, _info):
        user_tags = root.inner_report.find('user_tags')
        if user_tags is not None:
            return user_tags
        return None

    @staticmethod
    def resolve_delta_report(root, _info):
        delta_report = root.inner_report.find('delta/report')
        if delta_report is not None:
            return delta_report
        return None

    @staticmethod
    def resolve_report_format(root, _info):
        report_format = root.outer_report.find('report_format')
        if report_format is not None:
            return report_format
        return None

    @staticmethod
    def resolve_closed_cves(root, _info):
        closed_cves = root.inner_report.find('closed_cves')
        if closed_cves is not None:
            return closed_cves
        return None

    @staticmethod
    def resolve_task(root, _info):
        task = root.inner_report.find('task')
        if task is not None:
            return task
        return None

    @staticmethod
    def resolve_permissions(root, _info):
        permissions = root.inner_report.find('permissions')
        if permissions is not None:
            permissions = permissions.findall('permission')
            if len(permissions) > 0:
                return permissions
        return None

    @staticmethod
    def resolve_scan_run_status(root, _info):
        return get_text_from_element(root.inner_report, 'scan_run_status')

    @staticmethod
    def resolve_timezone(root, _info):
        return get_text_from_element(root.inner_report, 'timezone')

    @staticmethod
    def resolve_timezone_abbreviation(root, _info):
        return get_text_from_element(root.inner_report, 'timezone_abbrev')

    @staticmethod
    def resolve_timestamp(root, _info):
        return get_datetime_from_element(root.inner_report, 'timestamp')

    @staticmethod
    def resolve_scan_start(root, _info):
        return get_datetime_from_element(root.inner_report, 'scan_start')

    @staticmethod
    def resolve_scan_end(root, _info):
        return get_datetime_from_element(root.inner_report, 'scan_end')

    @staticmethod
    def resolve_severity(root, _info):
        return root.inner_report.find('severity')

    @staticmethod
    def resolve_applications(root, _info):
        return root.inner_report.find('apps')

    @staticmethod
    def resolve_tls_certificates(root, _info):
        return root.inner_report.find('ssl_certs')

    @staticmethod
    def resolve_operating_systems(root, _info):
        return root.inner_report.find('os')

    @staticmethod
    def resolve_vulnerabilities(root, _info):
        return root.inner_report.find('vulns')

    @staticmethod
    def resolve_ports_count(root, _info):
        return root.inner_report.find('ports')

    @staticmethod
    def resolve_ports(root, _info):
        ports = root.inner_report.find('ports')
        if ports is not None:
            ports = ports.findall('port')
            if len(ports) > 0:
                return ports
        return None

    @staticmethod
    def resolve_hosts_count(root, _info):
        hosts = root.inner_report.find('hosts')
        return hosts

    @staticmethod
    def resolve_hosts(root, _info):
        hosts = root.inner_report.findall('host')
        if hosts is not None and len(hosts) > 0:
            return hosts
        return None

    @staticmethod
    def resolve_results(root, _info):
        results = root.inner_report.find('results')
        if results is not None:
            results = results.findall('result')
            if len(results) > 0:
                return results
        return None

    @staticmethod
    def resolve_results_count(root, _info):
        return root.inner_report.find('result_count')

    @staticmethod
    def resolve_error_count(root, _info):
        errors = root.inner_report.find('errors')
        if errors is not None:
            return errors.find('count')
        return None

    @staticmethod
    def resolve_errors(root, _info):
        errors = root.inner_report.find('errors')
        if errors is not None:
            errors = errors.findall('error')
            if len(errors) > 0:
                return errors
        return None
