"""Execute the real blueprint's templates with simulated HA helpers.

PyYAML/Jinja2 are test-only dependencies; this is not full HA schema validation.
"""
import ast
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace as Obj
import math
import unittest

try:
    import yaml
    from jinja2 import StrictUndefined
    from jinja2.nativetypes import NativeEnvironment
except ImportError:
    yaml = None

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipIf(yaml is None, "Requires PyYAML and Jinja2")
class TemperatureBlueprintTests(unittest.TestCase):
    def setUp(self):
        class Loader(yaml.SafeLoader):
            pass
        Loader.add_constructor('!input', lambda loader, node: {'input': loader.construct_scalar(node)})
        self.blueprint = yaml.load((ROOT / 'blueprints/automation/lorawan/room_external_temperature.yaml').read_text(), Loader=Loader)
        self.now = datetime(2026, 11, 6, tzinfo=UTC)
        self.inputs = dict(
            target_devices=[],
            temperature_label='primary',
            maximum_age_minutes=120,
            minimum_difference=.01,
        )
        self.labelled = ['sensor.temperature', 'sensor.other_room']
        self.areas = {'sensor.temperature': 'room', 'sensor.other_room': 'other'}
        self.devices = {'number.external': 'vicki', 'sensor.temperature': 'external-sensor'}
        self.values = {
            'sensor.temperature': Obj(state='21.46', attributes=dict(device_class='temperature', unit_of_measurement='°C'), last_reported=self.now),
            'sensor.other_room': Obj(state='25', attributes=dict(device_class='temperature', unit_of_measurement='°C'), last_reported=self.now),
            'number.external': Obj(state='20', attributes={'min': -20, 'max': 60}),
        }
        self.data = dict(area_id='room', device_id='vicki', controls=dict(external_temperature='number.external'))
        self.env = NativeEnvironment(undefined=StrictUndefined)
        outer = self
        class States:
            def __call__(self, entity):
                return outer.values[entity].state if entity in outer.values else 'unknown'
            def __getitem__(self, entity):
                return outer.values[entity]
        states = States()
        def numeric(value):
            try:
                return math.isfinite(float(value))
            except (ValueError, TypeError):
                return False
        self.env.globals.update(states=states, label_entities=lambda label: self.labelled if label == 'primary' else [],
            area_id=lambda entity: self.areas.get(entity), device_id=lambda entity: self.devices.get(entity),
            state_attr=lambda entity, attr: self.values[entity].attributes.get(attr) if entity in self.values else None,
            has_value=lambda entity: states(entity) not in ('unknown', 'unavailable'), is_number=numeric,
            now=lambda: self.now, as_timestamp=lambda value, default=None: value.timestamp() if isinstance(value, datetime) else default)

    def render(self, value, context):
        if isinstance(value, dict):
            if set(value) == {'input'}:
                return self.inputs[value['input']]
            return {key: self.render(item, context) for key, item in value.items()}
        if isinstance(value, str):
            result = self.env.from_string(value).render(**context)
            if isinstance(result, str) and ('{{' in value or '{%' in value):
                result = result.strip()
                try:
                    return ast.literal_eval(result)
                except (ValueError, SyntaxError):
                    pass
            return result
        return value

    def run_blueprint(self, manual=False):
        context = {} if manual else {'trigger': Obj(event=Obj(data=self.data))}
        context.update(self.render(self.blueprint['variables'], context))
        for action in self.blueprint['actions']:
            if 'variables' in action:
                for key, value in action['variables'].items():
                    context[key] = self.render(value, context)
            elif 'if' in action:
                if all(self.render(c['value_template'], context) for c in action['if']):
                    return {'stop': self.render(action['then'][0]['stop'], context)}
            elif 'action' in action:
                return self.render(action, context)
        self.fail('No result')

    def test_input_compatibility_and_source(self):
        meta = self.blueprint['blueprint']
        self.assertEqual(set(meta['input']), set(self.inputs))
        device_selector = meta['input']['target_devices']['selector']['device']
        self.assertTrue(device_selector['multiple'])
        self.assertEqual(
            device_selector['filter'],
            [{'integration': 'lorawan', 'model': 'Vicki'}],
        )
        self.assertEqual(meta['input']['target_devices']['default'], [])
        self.assertEqual(meta['input']['temperature_label']['selector'], {'label': {}})
        self.assertTrue(meta['source_url'].endswith('/main/blueprints/automation/lorawan/room_external_temperature.yaml'))
        self.assertEqual(self.blueprint['triggers'][0]['event_data'], {'source': 'lorawan'})

    def test_writes_rounded_temperature_to_event_control(self):
        result = self.run_blueprint()
        self.assertEqual(result['action'], 'number.set_value')
        self.assertEqual(result['target'], {'entity_id': 'number.external'})
        self.assertEqual(result['data'], {'value': 21.5})

    def test_other_room_and_label_selection(self):
        self.data['area_id'] = 'other'
        self.assertEqual(self.run_blueprint()['data']['value'], 25)
        self.inputs['temperature_label'] = 'different-label'
        self.assertIn('stop', self.run_blueprint())

    def test_optional_device_selection_keeps_all_or_restricts_trigger(self):
        self.assertEqual(self.run_blueprint()['action'], 'number.set_value')
        self.inputs['target_devices'] = ['other-device']
        self.assertIn('nicht ausgewählt', self.run_blueprint()['stop'])
        self.inputs['target_devices'] = ['vicki']
        self.assertEqual(self.run_blueprint()['action'], 'number.set_value')

    def test_ambiguous_or_own_sensor_stops(self):
        self.areas['sensor.other_room'] = 'room'
        self.assertIn('stop', self.run_blueprint())
        self.labelled = ['sensor.temperature']
        self.devices['sensor.temperature'] = 'vicki'
        self.assertIn('stop', self.run_blueprint())

    def test_invalid_unavailable_stale_or_future_values_stop(self):
        sensor = self.values['sensor.temperature']
        for state, age in [('unavailable', 0), ('unknown', 0), ('nan', 0), ('inf', 0), ('22', 7201), ('22', -10)]:
            with self.subTest(state=state, age=age):
                sensor.state = state
                sensor.last_reported = self.now - timedelta(seconds=age)
                self.assertIn('stop', self.run_blueprint())

    def test_unchanged_reported_value_not_last_changed(self):
        self.values['sensor.temperature'].last_changed = self.now - timedelta(days=3)
        self.assertEqual(self.run_blueprint()['action'], 'number.set_value')
        self.values['number.external'].state = '21.5'
        self.assertIn('stop', self.run_blueprint())

    def test_threshold_and_age_boundary(self):
        self.values['sensor.temperature'].state = '21.4'
        self.values['sensor.temperature'].last_reported = self.now - timedelta(seconds=7200)
        self.values['number.external'].state = '21.3'
        self.inputs['minimum_difference'] = .1
        self.assertEqual(self.run_blueprint()['data']['value'], 21.4)
        self.inputs['minimum_difference'] = .2
        self.assertIn('stop', self.run_blueprint())

    def test_invalid_target_room_units_or_manual_run(self):
        self.assertIn('stop', self.run_blueprint(manual=True))
        for key, value in [('controls', {}), ('area_id', None), ('device_id', 'other-device')]:
            original = self.data[key]
            self.data[key] = value
            self.assertIn('stop', self.run_blueprint())
            self.data[key] = original
        self.values['sensor.temperature'].attributes['unit_of_measurement'] = '°F'
        self.assertIn('stop', self.run_blueprint())

    def test_control_unavailable_and_out_of_range(self):
        self.values['number.external'].state = 'unavailable'
        self.assertIn('stop', self.run_blueprint())
        self.values['number.external'].state = '20'
        self.values['sensor.temperature'].state = '61'
        self.assertIn('Wertebereich', self.run_blueprint()['stop'])
