# units tests on the dataview module
from unittest import TestCase

import mola.dataview as dv
import mola.dataimport as di


class DataView(TestCase):
    # testing from full default db
    conn = di.get_sqlite_connection()

    def test_get_ids(self):
        dfr = dv.get_ids(DataView.conn, ref_ids=['64867712-23c4-3be5-a50e-3631e74571a6'],
                         table_name='TBL_PROCESSES')
        self.assertGreater(len(dfr), 0)

    def test_get_ref_ids(self):
        dfr = dv.get_ref_ids(DataView.conn, ids=[4578980], table_name='TBL_PROCESSES')
        self.assertGreater(len(dfr), 0)

    def test_get_elementary_flows(self):
        elementary_flows_dfr = dv.get_elementary_flows(DataView.conn)
        self.assertGreater(len(elementary_flows_dfr), 0)

    def test_get_impact_categories(self):
        impact_categories_dfr = dv.get_impact_categories(DataView.conn, category_name=['Climate change - GWP100%'])
        self.assertGreater(len(impact_categories_dfr), 0)

    def test_get_table(self):
        table_dfr = dv.get_table(DataView.conn, 'TBL_IMPACT_METHODS')
        self.assertGreater(len(table_dfr), 0)

    def test_get_impact_category_elementary_flow(self):
        impact_element_dfr = dv.get_impact_category_elementary_flow(
            DataView.conn, ref_ids=['42b1e910-3bd2-3741-85ce-a3966798440b'])
        self.assertGreater(len(impact_element_dfr), 0)

    def test_get_process_elementary_flow(self):
        process_element_dfr = dv.get_process_elementary_flow(
            DataView.conn, ref_ids=['64867712-23c4-3be5-a50e-3631e74571a6'])
        self.assertGreater(len(process_element_dfr), 0)

    def test_get_processes(self):
        process_dfr = dv.get_processes(DataView.conn, name=['lemon production%'], location=["Spain"])
        self.assertGreater(len(process_dfr), 0)

    def test_get_process_locations(self):
        process_dfr = dv.get_process_locations(DataView.conn, ref_ids=['64867712-23c4-3be5-a50e-3631e74571a6'])
        self.assertGreater(len(process_dfr), 0)

    def test_get_process_product_flow(self):
        process_flow1_dfr = dv.get_process_product_flow(
            DataView.conn, process_ref_ids='64867712-23c4-3be5-a50e-3631e74571a6')
        self.assertEqual(process_flow1_dfr.shape, (1, 5))
        process_flow2_dfr = dv.get_process_product_flow(
            DataView.conn, process_ref_ids=['64867712-23c4-3be5-a50e-3631e74571a6'])
        self.assertEqual(process_flow1_dfr.shape, process_flow2_dfr.shape)

    def test_get_ref_id_dicts(self):
        d = dv.get_ref_id_dicts(DataView.conn, {'flows': 'TBL_FLOWS', 'processes': 'TBL_PROCESSES'})
        self.assertGreater(len(d), 0)

    def test_get_lookup_tables(self):
        lookup = dv.get_lookup_tables(DataView.conn)
        self.assertGreater(len(lookup), 0)

    def test_get_process_product_flow_costs(self):
        ref_id = ['cd177b7d-e908-3e69-b40c-4827b4abaa4d']
        costs = dv.get_process_product_flow_costs(DataView.conn, process_ref_ids=ref_id)
        self.assertGreater(len(costs), 0)

    def test_get_process_product_flow_units(self):
        ref_id = ['cd177b7d-e908-3e69-b40c-4827b4abaa4d']
        units = dv.get_process_product_flow_units(DataView.conn, process_ref_ids=ref_id)
        self.assertGreater(len(units), 0)


class TestLookupTables(TestCase):
    conn = di.get_sqlite_connection()
    lookup = dv.LookupTables(conn)

    def test_get(self):
        pm = self.lookup.get('P_m')
        self.assertEqual(pm.shape[1], 2)
        kpi = self.lookup.get('KPI')
        self.assertEqual(kpi.shape[1], 3)

    def test_get_single_column(self):
        pm = self.lookup.get_single_column('P_m')
        self.assertEqual(pm.shape[1], 1)



