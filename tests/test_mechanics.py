import unittest
from app import create_app
from app.extensions import db


class TestMechanics(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def _create_mechanic(self, name='Jane Smith', email='jane@shop.com',
                         phone='555-5678', salary=55000.0):
        return self.client.post('/mechanics/', json={
            'name': name,
            'email': email,
            'phone': phone,
            'salary': salary
        })

    # ---------- POST /mechanics/ ----------
    def test_create_mechanic(self):
        response = self._create_mechanic()
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['name'], 'Jane Smith')
        self.assertEqual(data['salary'], 55000.0)

    def test_create_mechanic_missing_fields(self):
        response = self.client.post('/mechanics/', json={
            'name': 'Jane Smith'
        })
        self.assertEqual(response.status_code, 400)

    def test_create_mechanic_duplicate_email(self):
        self._create_mechanic()
        # Duplicate email causes an IntegrityError (unhandled → 500)
        self.app.config['PROPAGATE_EXCEPTIONS'] = False
        self.app.config['TESTING'] = False
        response = self._create_mechanic(name='Another', email='jane@shop.com',
                                         phone='555-9999', salary=40000.0)
        self.assertEqual(response.status_code, 500)

    # ---------- GET /mechanics/ ----------
    def test_get_mechanics_empty(self):
        response = self.client.get('/mechanics/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])

    def test_get_mechanics_with_data(self):
        self._create_mechanic()
        response = self.client.get('/mechanics/')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 1)

    # ---------- PUT /mechanics/<id> ----------
    def test_update_mechanic(self):
        self._create_mechanic()
        response = self.client.put('/mechanics/1', json={
            'name': 'Jane Updated',
            'email': 'jane@shop.com',
            'phone': '555-0000',
            'salary': 60000.0
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['name'], 'Jane Updated')
        self.assertEqual(response.get_json()['salary'], 60000.0)

    def test_update_mechanic_not_found(self):
        response = self.client.put('/mechanics/999', json={
            'name': 'Nobody',
            'email': 'nobody@shop.com',
            'phone': '555-0000',
            'salary': 40000.0
        })
        self.assertEqual(response.status_code, 404)

    def test_update_mechanic_invalid_data(self):
        self._create_mechanic()
        response = self.client.put('/mechanics/1', json={
            'name': '',
            'email': 'bad-email',
            'phone': '555-0000',
            'salary': 'not-a-number'
        })
        self.assertEqual(response.status_code, 400)

    # ---------- DELETE /mechanics/<id> ----------
    def test_delete_mechanic(self):
        self._create_mechanic()
        response = self.client.delete('/mechanics/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn('deleted', response.get_json()['message'])

    def test_delete_mechanic_not_found(self):
        response = self.client.delete('/mechanics/999')
        self.assertEqual(response.status_code, 404)

    # ---------- GET /mechanics/most-tickets ----------
    def test_most_tickets_empty(self):
        response = self.client.get('/mechanics/most-tickets')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])

    def test_most_tickets_with_data(self):
        self._create_mechanic()
        response = self.client.get('/mechanics/most-tickets')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertIn('ticket_count', data[0])
        self.assertEqual(data[0]['ticket_count'], 0)


if __name__ == '__main__':
    unittest.main()
