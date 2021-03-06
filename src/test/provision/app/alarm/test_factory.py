from mock import MagicMock, ANY

from spacel.provision.app.alarm.endpoint.factory import AlarmEndpointFactory
from spacel.provision.app.alarm.factory import AlarmFactory
from spacel.provision.app.alarm.trigger.factory import TriggerFactory
from test import BaseSpaceAppTest


class TestAlarmFactory(BaseSpaceAppTest):
    def setUp(self):
        super(TestAlarmFactory, self).setUp()
        self.endpoints = MagicMock(spec=AlarmEndpointFactory)
        self.triggers = MagicMock(spec=TriggerFactory)
        self.template = {}
        self.alarm_factory = AlarmFactory(self.endpoints, self.triggers)

    def test_add_alarms(self):
        self.alarm_factory.add_alarms(self.app_region, self.template)

        self.endpoints.add_endpoints.assert_called_with(self.template, ANY)
        self.triggers.add_triggers.assert_called_with(self.template, ANY, ANY)

    def test_get(self):
        alarm_factory = AlarmFactory.get(None, None, None)
        self.assertIsInstance(alarm_factory, AlarmFactory)
