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

# pylint: disable=no-self-argument, no-member

import graphene

from gvm.protocols.next import (
    get_alert_event_from_string,
    get_alert_condition_from_string,
    get_alert_method_from_string,
)

from selene.schema.alerts.helper import (
    append_alert_condition_data,
    append_alert_event_data,
    append_alert_method_data,
)

from selene.schema.alerts.fields import (
    AlertCondition,
    AlertEvent,
    AlertMethod,
    DeltaType,
    FeedEvent,
    SecInfoType,
    SeverityDirection,
    TaskStatus,
)

from selene.schema.entities import (
    create_export_by_filter_mutation,
    create_export_by_ids_mutation,
    create_delete_by_ids_mutation,
    create_delete_by_filter_mutation,
)

from selene.schema.severity import SeverityType

from selene.schema.utils import (
    get_gmp,
    require_authentication,
)


class ConditionData(graphene.InputObjectType):
    at_least_count = graphene.Int(name='at_least_count')
    at_least_filter_id = graphene.UUID(name='at_least_filter_id')
    count = graphene.Int()
    direction = SeverityDirection()
    severity = SeverityType()
    filter_id = graphene.UUID(name="filter_id")


class EventData(graphene.InputObjectType):
    status = TaskStatus()
    feed_event = FeedEvent(name='feed_event')
    secinfo_type = SecInfoType(name='secinfo_type')


class MethodData(graphene.InputObjectType):
    URL = graphene.String()
    composer_include_notes = graphene.Boolean(name="composer_include_notes")
    composer_include_overrides = graphene.Boolean(
        name="composer_include_overrides"
    )
    defense_center_ip = graphene.String(name="defense_center_ip")
    defense_center_port = graphene.Int(name="defense_center_port")
    delta_report_id = graphene.UUID(name="delta_report_id")
    delta_type = DeltaType(name="delta_type")
    details_url = graphene.String(name="details_url")
    from_address = graphene.String(name="from_address")
    message = graphene.String()
    message_attach = graphene.String(name="message_attach")
    notice = graphene.String()
    notice_attach_format = graphene.UUID(name="notice_attach_format")
    notice_report_format = graphene.UUID(name="notice_report_format")
    pkcs12 = graphene.String()
    pkcs12_credential = graphene.UUID(name="pkcs12_credential")
    recipient_credential = graphene.UUID(name="recipient_credential")
    scp_credential = graphene.UUID(name="scp_credential")
    scp_host = graphene.String(name="scp_host")
    scp_known_hosts = graphene.String(name="scp_known_hosts")
    scp_path = graphene.String(name="scp_path")
    scp_report_format = graphene.UUID(name="scp_report_format")
    send_host = graphene.String(name="send_host")
    send_port = graphene.Int(name="send_port")
    send_report_format = graphene.UUID(name="send_report_format")
    smb_credential = graphene.UUID(name="smb_credential")
    smb_file_path = graphene.String(name="smb_file_path")
    smb_report_format = graphene.UUID(name="smb_report_format")
    smb_share_path = graphene.String(name="smb_share_path")
    snmp_agent = graphene.String(name="snmp_agent")
    snmp_community = graphene.String(name="snmp_community")
    snmp_message = graphene.String(name="snmp_message")
    start_task_task = graphene.UUID(name="start_task_task")
    subject = graphene.String(name="subject")
    submethod = graphene.String()
    to_address = graphene.String(name="to_address")
    tp_sms_credential = graphene.UUID(name="tp_sms_credential")
    tp_sms_hostname = graphene.String(name="tp_sms_hostname")
    tp_sms_tls_certificate = graphene.String(name="tp_sms_tls_certificate")
    tp_sms_tls_workaround = graphene.Int(name="tp_sms_tls_workaround")
    verinice_server_credential = graphene.UUID(
        name="verinice_server_credential"
    )
    verinice_server_report_format = graphene.UUID(
        name="verinice_server_report_format"
    )
    verinice_server_url = graphene.String(name="verinice_server_url")
    vfire_base_url = graphene.String(name="vfire_base_url")
    vfire_call_description = graphene.String(name="vfire_call_description")
    vfire_call_impact_name = graphene.String(name="vfire_call_impact_name")
    vfire_call_partition_name = graphene.String(
        name="vfire_call_partition_name"
    )
    vfire_call_template_name = graphene.String(name="vfire_call_template_name")
    vfire_call_type_name = graphene.String(name="vfire_call_type_name")
    vfire_call_urgency_name = graphene.String(name="vfire_call_urgency_name")
    vfire_client_id = graphene.String(name="vfire_client_id")
    vfire_credential = graphene.String(name="vfire_credential")
    vfire_session_type = graphene.String(name="vfire_session_type")


class CreateAlertInput(graphene.InputObjectType):
    """Input object for createAlert.

    Args:
        name (str): Name of the new alert
        event (AlertEvent): The event that must happen for the alert to occur,
            one of ‘TASK_RUN_STATUS_CHANGED’, ‘UPDATED_SECINFO_ARRIVED’ or
            ‘NEW_SECINFO_ARRIVED’
        condition (AlertCondition): The condition that must be satisfied for
            the alert to occur; if the event is either ‘UPDATED_SECINFO_ARRIVED’
            or ‘NEW_SECINFO_ARRIVED’, condition must be 'ALWAYS'. Otherwise,
            condition can also be on of ‘SEVERITY_AT_LEAST’,
            ‘FILTER_COUNT_CHANGED’ or ‘FILTER_COUNT_AT_LEAST’.
        method (AlertMethod): The method by which the user is alerted, one
            of ‘SCP’, 'SEND, ‘SMB’, ‘SNMP’, 'SYSLOG' or 'EMAIL'; if the event is
            neither ‘UPDATED_SECINFO_ARRIVED’ nor ‘NEW_SECINFO_ARRIVED’, method
            can also be one of ‘START_TASK’, ‘HTTP_GET’, ‘SOURCEFIRE_CONNECTOR’
            or ‘VERINICE_CONNECTOR’.
        event_data (dict, optional): Data that defines the event
        condition_data (dict, optional): Data that defines the condition
        method_data (dict, optional): Data that defines the method
        filter_id (UUID, optional): Filter to apply when executing alert
        comment (str, optional): Comment for the alert
    """

    name = graphene.String(required=True, description="Name of the new alert")
    event = AlertEvent(
        required=True,
        description="The event that must be satisfied for the alert to occur",
    )
    condition = AlertCondition(
        required=True,
        description=(
            "The condition that must be satisfied" "for the alert to occur"
        ),
    )
    method = AlertMethod(
        required=True, description="The method by which the user is alerted"
    )
    event_data = EventData(description="Data that defines the event")
    method_data = MethodData(description="Data that defines the method")
    condition_data = ConditionData(
        description="Data that defines the condition"
    )
    comment = graphene.String(description="Comment for the alert")
    filter_id = graphene.UUID(
        description="Filter to apply when executing alert"
    )
    report_formats = graphene.List(
        graphene.UUID, description="List of UUIDs to use with Alemba vFire"
    )


class CreateAlert(graphene.Mutation):
    """Creates an alert

    Args:
        input (CreateAlertInput): Input object for CreateAlert.
    """

    class Arguments:
        input_object = CreateAlertInput(required=True, name='input')

    alert_id = graphene.UUID(name='id')

    @require_authentication
    def mutate(root, info, input_object):
        gmp = get_gmp(info)

        if input_object.event_data is not None:
            event_data = append_alert_event_data(
                input_object.event, input_object.event_data
            )
        else:
            event_data = None

        if input_object.method_data is not None:
            method_data = append_alert_method_data(
                input_object.method,
                input_object.method_data,
                report_formats=input_object.report_formats,
            )
        else:
            method_data = None

        if input_object.condition_data is not None:
            condition_data = append_alert_condition_data(
                input_object.condition, input_object.condition_data
            )
        else:
            condition_data = None

        if input_object.filter_id is not None:
            filter_id = str(input_object.filter_id)
        else:
            filter_id = None

        resp = gmp.create_alert(
            input_object.name,
            get_alert_condition_from_string(input_object.condition),
            get_alert_event_from_string(input_object.event),
            get_alert_method_from_string(input_object.method),
            comment=input_object.comment,
            method_data=method_data,
            condition_data=condition_data,
            event_data=event_data,
            filter_id=filter_id,
        )

        return CreateAlert(alert_id=resp.get('id'))


class ModifyAlertInput(graphene.InputObjectType):
    """Input object for createAlert.

    Args:
        id (UUID): UUID of the alert that will be modified
        name (str, optional): Name of the new alert
        event (AlertEvent, optional): The event that must happen for the alert
            to occur, one of ‘TASK_RUN_STATUS_CHANGED’,
            ‘UPDATED_SECINFO_ARRIVED’ or ‘NEW_SECINFO_ARRIVED’
        condition (AlertCondition, optional): The condition that must be
            satisfied for the alert to occur; if the event is either
            ‘UPDATED_SECINFO_ARRIVED’ or ‘NEW_SECINFO_ARRIVED’, condition must
            be 'ALWAYS'. Otherwise, condition can also be on of
            ‘SEVERITY_AT_LEAST’, ‘FILTER_COUNT_CHANGED’ or
            ‘FILTER_COUNT_AT_LEAST’.
        method (AlertMethod, optional): The method by which the user is alerted,
            one of ‘SCP’, 'SEND, ‘SMB’, ‘SNMP’, 'SYSLOG' or 'EMAIL'; if the
            event is neither ‘UPDATED_SECINFO_ARRIVED’ nor ‘NEW_SECINFO_ARRIVED’
            method can also be one of ‘START_TASK’, ‘HTTP_GET’,
            ‘SOURCEFIRE_CONNECTOR’ or ‘VERINICE_CONNECTOR’.
        event_data (dict, optional): Data that defines the event
        condition_data (dict, optional): Data that defines the condition
        method_data (dict, optional): Data that defines the method
        filter_id (UUID, optional): Filter to apply when executing alert
        comment (str, optional): Comment for the alert
    """

    alert_id = graphene.UUID(required=True, name='id')
    name = graphene.String(description="Name of the new alert")
    event = AlertEvent(
        description="The event that must be satisfied for the alert to occur",
    )
    condition = AlertCondition(
        description=(
            "The condition that must be satisfied" "for the alert to occur"
        ),
    )
    method = AlertMethod(description="The method by which the user is alerted")
    event_data = EventData(description="Data that defines the event")
    method_data = MethodData(description="Data that defines the method")
    condition_data = ConditionData(
        description="Data that defines the condition"
    )
    comment = graphene.String(description="Comment for the alert")
    filter_id = graphene.UUID(
        description="Filter to apply when executing alert"
    )
    report_formats = graphene.List(
        graphene.UUID, description="List of UUIDs to use with Alemba vFire"
    )


class ModifyAlert(graphene.Mutation):
    """Modifies an alert

    Args:
        input (ModifyAlertInput): Input object for ModifyAlert.
    """

    class Arguments:
        input_object = ModifyAlertInput(required=True, name='input')

    ok = graphene.Boolean()

    @require_authentication
    def mutate(root, info, input_object):
        gmp = get_gmp(info)

        if input_object.event_data is not None:
            event_data = append_alert_event_data(
                input_object.event, input_object.event_data
            )
        else:
            event_data = None

        if input_object.method_data is not None:
            method_data = append_alert_method_data(
                input_object.method,
                input_object.method_data,
                report_formats=input_object.report_formats,
            )
        else:
            method_data = None

        if input_object.condition_data is not None:
            condition_data = append_alert_condition_data(
                input_object.condition, input_object.condition_data
            )
        else:
            condition_data = None

        if input_object.filter_id is not None:
            filter_id = str(input_object.filter_id)
        else:
            filter_id = None

        gmp.modify_alert(
            alert_id=str(input_object.alert_id),
            name=input_object.name,
            condition=get_alert_condition_from_string(input_object.condition),
            event=get_alert_event_from_string(input_object.event),
            method=get_alert_method_from_string(input_object.method),
            comment=input_object.comment,
            method_data=method_data,
            condition_data=condition_data,
            event_data=event_data,
            filter_id=filter_id,
        )

        return ModifyAlert(ok=True)


class CloneAlert(graphene.Mutation):
    """Clones an alert

    Args:
        id (UUID): UUID of alert to clone.

    Returns:
        ok (Boolean)
    """

    class Arguments:
        copy_id = graphene.UUID(
            required=True,
            name='id',
            description='UUID of the alert to clone.',
        )

    alert_id = graphene.UUID(name='id')

    @require_authentication
    def mutate(root, info, copy_id):
        gmp = get_gmp(info)
        resp = gmp.clone_alert(str(copy_id))
        return CloneAlert(alert_id=resp.get('id'))


class TestAlert(graphene.Mutation):
    """Test an alert

    Args:
        id (UUID): UUID of alert to test.

    Returns:
        ok (Boolean)
    """

    class Arguments:
        alert_id = graphene.UUID(
            required=True,
            name='id',
            description='UUID of the alert to test.',
        )

    ok = graphene.Boolean()

    @require_authentication
    def mutate(root, info, alert_id):
        gmp = get_gmp(info)
        gmp.test_alert(str(alert_id))
        return TestAlert(ok=True)


# Explicit classes needed, else we get error
# 'AssertionError: Found different types with the same name in the
#   schema: DeleteByIds, DeleteByIds.'

DeleteByIdsClass = create_delete_by_ids_mutation(entity_name='alert')


class DeleteAlertsByIds(DeleteByIdsClass):
    """Deletes a list of alerts

    Args:
        ids (List(UUID)): List of UUIDs of alert to delete.

    Returns:
        ok (Boolean)
    """


DeleteByFilterClass = create_delete_by_filter_mutation(entity_name='alert')


class DeleteAlertsByFilter(DeleteByFilterClass):
    """Deletes a filtered list of alerts
    Args:
        filterString (str): Filter string for alert list to delete.
    Returns:
        ok (Boolean)
    """


# Explicit classes needed, else we get error
# 'AssertionError: Found different types with the same name in the
#   schema: ExportByIds, ExportByIds.'

ExportByIdsClass = create_export_by_ids_mutation(entity_name='alert')


class ExportAlertsByIds(ExportByIdsClass):
    pass


ExportByFilterClass = create_export_by_filter_mutation(entity_name='alert')


class ExportAlertsByFilter(ExportByFilterClass):
    pass
