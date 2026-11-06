import os
import tempfile
import unittest
from datetime import date
import app

class TaskFlowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        app.DB_PATH = __import__('pathlib').Path(self.tmp.name) / 'test.db'
        app.initialize()

    def tearDown(self):
        self.tmp.cleanup()

    def test_crud_and_summary(self):
        task = {'title':'完成專題','category':'專題','due_date':'2026-11-02','priority':'高','notes':'測試'}
        task_id = app.add_task(task)
        self.assertEqual(len(app.list_tasks()), 1)
        self.assertTrue(app.update_task(task_id, {**task,'title':'更新專題'}))
        self.assertEqual(app.list_tasks()[0]['title'], '更新專題')
        self.assertTrue(app.toggle_task(task_id))
        self.assertEqual(app.summary(app.list_tasks())['rate'], 100)
        self.assertTrue(app.delete_task(task_id))
        self.assertEqual(app.list_tasks(), [])

    def test_validation_and_due(self):
        with self.assertRaises(ValueError):
            app.add_task({'title':'','due_date':'2026-11-02'})
        with self.assertRaises(ValueError):
            app.add_task({'title':'hi','due_date':'2026-13-44'})
        tasks=[{'due_date':'2026-10-29','completed':0},{'due_date':'2026-11-01','completed':0},{'due_date':'2026-10-20','completed':1}]
        s=app.summary(tasks, date(2026,10,30))
        self.assertEqual(s['overdue'],1)
        self.assertEqual(s['soon'],1)

if __name__ == '__main__':
    unittest.main()
