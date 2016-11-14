import unittest

from spacel.model.app import SpaceApp, SpaceDockerService
from spacel.model.base import NAME, REGIONS
from test import BaseSpaceAppTest
from test import ORBIT_REGIONS, APP_NAME, TWO_REGIONS

CONTAINER = 'pwagner/elasticsearch-aws'
SERVICE_NAME = 'elasticsearch.service'
SERVICE_NAME_NO_EXT = 'elasticsearch'


class TestSpaceApp(BaseSpaceAppTest):
    def test_constructor_default_regions(self):
        app = SpaceApp(self.orbit)
        self.assertEqual(ORBIT_REGIONS, app.regions)

    def test_constructor_custom_regions(self):
        app = SpaceApp(self.orbit, {
            REGIONS: TWO_REGIONS
        })
        # us-west-1 is blocked since it's not in the orbit:
        self.assertEqual(ORBIT_REGIONS, app.regions)

    def test_public_ports_default(self):
        app = SpaceApp(self.orbit)

        self.assertEqual(1, len(app.public_ports))
        self.assertEqual('HTTP', app.public_ports[80].scheme)
        self.assertEquals(('0.0.0.0/0',), app.public_ports[80].sources)

    def test_public_ports_https(self):
        app = SpaceApp(self.orbit, {
            'public_ports': {
                443: {
                }
            }
        })
        self.assertEqual('HTTPS', app.public_ports[443].scheme)

    def test_public_ports_custom_sources(self):
        custom_sources = ('10.0.0.0/8', '192.168.0.0/16')
        app = SpaceApp(self.orbit, {
            'public_ports': {
                80: {
                    'sources': custom_sources
                }
            }
        })

        self.assertEqual('HTTP', app.public_ports[80].scheme)
        self.assertEquals(custom_sources, app.public_ports[80].sources)

    def test_services_docker(self):
        app = SpaceApp(self.orbit, {
            'services': {
                SERVICE_NAME: {
                    'image': CONTAINER,
                    'ports': {
                        9200: 9200,
                        9300: 9300
                    }
                }
            }
        })

        self.assertEqual(1, len(app.services))
        self.assertIsNotNone(app.services[SERVICE_NAME].unit_file)

    def test_services_service_extension(self):
        app = SpaceApp(self.orbit, {
            'services': {
                SERVICE_NAME_NO_EXT: {
                    'unit_file': '[Unit]'
                }
            }
        })

        self.assertEqual(1, len(app.services))
        self.assertEqual(app.services[SERVICE_NAME].unit_file, '[Unit]')

    def test_services_units(self):
        app = SpaceApp(self.orbit, {
            'services': {
                SERVICE_NAME: {
                    'unit_file': '[Unit]'
                }
            }
        })

        self.assertEqual(1, len(app.services))
        self.assertEqual(app.services[SERVICE_NAME].unit_file, '[Unit]')

    def test_services_empty_unit(self):
        app = SpaceApp(self.orbit, {
            'services': {
                SERVICE_NAME: {}
            }
        })

        self.assertEqual(0, len(app.services))

    def test_spot(self):
        app = SpaceApp(self.orbit, {})

        spot_bool = {'spot': True}
        spot_string = {'spot': 'true'}
        spot_dict = {'spot': {'very': 'testy'}}
        self.assertEqual(app._spot(spot_bool), {})
        self.assertEqual(app._spot(spot_string), {})
        self.assertEqual(app._spot(spot_dict), spot_dict['spot'])

    def test_full_name(self):
        app = SpaceApp(self.orbit, {
            NAME: APP_NAME
        })
        self.assertEquals(app.full_name, 'test-orbit-test-app')

    def test_no_elb(self):
        app = SpaceApp(self.orbit, {'elb_availability': 'disabled'})
        self.assertEqual(False, app.loadbalancer)

    def test_files_raw_string(self):
        app = SpaceApp(self.orbit, {
            'files': {
                'test-file': 'meow'
            }
        })

        self.assertEquals(1, len(app.files))
        self.assertEquals({'body': 'bWVvdw=='}, app.files['test-file'])

    def test_files_raw_encoded(self):
        encoded_body = {'body': 'bWVvdw=='}
        app = SpaceApp(self.orbit, {
            'files': {
                'test-file': encoded_body
            }
        })

        self.assertEquals(1, len(app.files))
        self.assertEquals(encoded_body, app.files['test-file'])

    def test_files_encrypted(self):
        encrypted_payload = {
            'iv': '',
            'key': '',
            'key_region': '',
            'ciphertext': '',
            'encoding': ''
        }
        app = SpaceApp(self.orbit, {
            'files': {
                'test-file': encrypted_payload
            }
        })

        self.assertEquals(1, len(app.files))
        self.assertEquals(encrypted_payload, app.files['test-file'])


class TestSpaceDockerService(unittest.TestCase):
    def test_constructor_ports(self):
        service = SpaceDockerService(SERVICE_NAME,
                                     CONTAINER,
                                     ports={
                                         9200: 9200,
                                         9300: 9300
                                     })
        self.assertIn('-p 9200:9200', service.unit_file)
        self.assertIn('-p 9300:9300', service.unit_file)
        self.assertIn(' %s' % CONTAINER, service.unit_file)
        self.assertIn('elasticsearch.service', service.name)
