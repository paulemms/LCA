from unittest import TestCase
import mola.sqlgenerator as sq
import mola.dataimport as di
import pandas as pd


class TestSQLGenerator(TestCase):
    conn = di.get_sqlite_connection()

    def test_build_process_elementary_flow(self):
        p_m = ['f22f5f6e-1bdc-3cb5-8f48-8a04d8f9b768']
        p_t = ['44ad59ca-4fe0-394c-a6d9-5dea68783c23']
        pe_sql = sq.build_process_elementary_flow(process_ref_ids=p_m + p_t)
        z = pd.read_sql(pe_sql, self.conn)
        self.assertGreater(len(z), 0)

    def test_build_location(self):
        p_m = ['64867712-23c4-3be5-a50e-3631e74571a6']
        loc_sql = sq.build_location(process_ref_ids=p_m)
        z = pd.read_sql(loc_sql, self.conn)
        self.assertGreater(len(z), 0)

    def test_build_product_flow(self):
        p_m = ['f22f5f6e-1bdc-3cb5-8f48-8a04d8f9b768']
        bp_sql = sq.build_product_flow(process_ref_ids=p_m)
        z = pd.read_sql(bp_sql, self.conn)
        self.assertGreater(len(z), 0)

    def test_build_product_flow_cost(self):
        p_m = ['f22f5f6e-1bdc-3cb5-8f48-8a04d8f9b768']
        pfc_sql = sq.build_product_flow_cost(process_ref_ids=p_m, time=['t0'])
        z = pd.read_sql(pfc_sql, self.conn)
        self.assertGreater(len(z), 0)

    def test_build_impact_category_elementary_flow(self):
        # ReCiPe Midpoint (H) V1.13 / climate change - GWP100 from 3.6 methods
        kpi = ['42b1e910-3bd2-3741-85ce-a3966798440b']
        ice_sql = sq.build_impact_category_elementary_flow(ref_ids=kpi)
        z = pd.read_sql(ice_sql, self.conn)
        self.assertGreater(len(z), 0)
        # no environmental kpi, but costs
        kpi = []
        ice_sql = sq.build_impact_category_elementary_flow(ref_ids=kpi)
        z = pd.read_sql(ice_sql, self.conn)
        self.assertEqual(len(z), 0)
