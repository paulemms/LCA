from unittest import TestCase
from tempfile import NamedTemporaryFile

import mola.specification5 as sp
import mola.build as mb
import mola.utils as mu
import json

# TODO add a SimpleSpecification test


class TestScheduleSpecification(TestCase):
    spec = sp.GeneralSpecification()
    config = mb.get_config('test_model_config.json')

    def test_populate(self):
        # from a model config file write out sets and parameters to two temporary files
        # for the DataPortal in populate
        json_list = mb.config_to_json(self.config)
        model_instance = self.spec.populate(json_list)
        self.assertGreater(len(model_instance), 0)

    def test_populate_dummy(self):
        sets = self.config['sets']
        parameters = self.config['parameters']
        # using non-db sets
        sets['P_m'] = ['pm1']
        sets['P_s'] = ['pt1']
        sets['P_t'] = ['ps1']
        parameters = mb.build_parameters(sets, parameters, self.spec, index_value=True)
        # should we use config_to_json here - need to write back to config
        sets_json = NamedTemporaryFile(suffix='.json', delete=False)
        parameters_json = NamedTemporaryFile(suffix='.json', delete=False)
        with open(sets_json.name, 'w') as fp:
            json.dump(sets, fp)
        with open(parameters_json.name, 'w') as fp:
            json.dump(parameters, fp)
        sets_json.close()
        parameters_json.close()
        model_instance = self.spec.populate([sets_json.name, parameters_json.name],
                                            elementary_flow_ref_ids=['e1, e2, e3'])
        self.assertGreater(len(model_instance), 0)

    def test_populate_cost(self):
        # separate set and parameter files for cost
        self.spec.settings['distance_calculated'] = False
        model_instance = self.spec.populate(['test_cost_set_data.json', 'test_cost_parameters_data.json'])
        self.assertGreater(len(model_instance), 0)

    def test_populate_calculated_distance(self):
        # need to set X and Y coords to something meaningful for task
        config = self.config.copy()
        config['parameters']['X'] = [{'index': ['k1', 't1'], 'value': 0.0}]
        config['parameters']['Y'] = [{'index': ['k1', 't1'], 'value': 0.0}]

        json_list = mb.config_to_json(config)
        self.spec.settings['distance_calculated'] = True
        model_instance = self.spec.populate(json_list)

        # get the calculated distance
        d = list(model_instance.dd.extract_values().values())

        self.assertEqual(int(d[0]), 4487)
