import unittest
from app import create_app
from app.extensions import db


class TestServiceTickets(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def _create_customer(self):
        return self.client.post('/customers/', json={
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '555-1234'
        })

    def _create_mechanic(self, email='jane@shop.com'):
        return self.client.post('/mechanics/', json={
            'name': 'Jane Smith',
            'email': email,
            'phone': '555-5678',
            'salary': 55000.0
        })

    def _create_ticket(self):
        return self.client.post('/service-tickets/', json={
            'vin': '1HGCM82633A004352',
            'service_date': '2025-01-15',
            'service_desc': 'Oil change and tire rotation',
            'customer_email': 'john@example.com'
        })

    def _create_inventory(self):
        return self.client.post('/inventory/', json={
            'name': 'Oil Filter',
            'price': 12.99
        })

    # ---------- POST /service-tickets/ ----------
    def test_create_ticket(self):
        self._create_customer()
        response = self._create_ticket()
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['vin'], '1HGCM82633A004352')
        self.assertEqual(data['service_desc'], 'Oil change and tire rotation')

    def test_create_ticket_missing_fields(self):
        response = self.client.post('/service-tickets/', json={
            'vin': '1HGCM82633A004352'
        })
        self.assertEqual(response.status_code, 400)

    def test_create_ticket_invalid_data(self):
        response = self.client.post('/service-tickets/', json={
            'vin': '',
            'service_date': 'not-a-date',
            'service_desc': '',
            'customer_email': ''
        })
        self.assertEqual(response.status_code, 400)

    # ---------- GET /service-tickets/ ----------
    def test_get_tickets_empty(self):
        response = self.client.get('/service-tickets/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])

    def test_get_tickets_with_data(self):
        self._create_customer()
        self._create_ticket()
        response = self.client.get('/service-tickets/')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 1)

    # ---------- PUT /service-tickets/<id>/assign-mechanic/<id> ----------
    def test_assign_mechanic(self):
        self._create_customer()
        self._create_mechanic()
        self._create_ticket()
        response = self.client.put('/service-tickets/1/assign-mechanic/1')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data['mechanics']), 1)

    def test_assign_mechanic_duplicate(self):
        self._create_customer()
        self._create_mechanic()
        self._create_ticket()
        self.client.put('/service-tickets/1/assign-mechanic/1')
        response = self.client.put('/service-tickets/1/assign-mechanic/1')
        self.assertEqual(response.status_code, 400)
        self.assertIn('already assigned', response.get_json()['message'])

    def test_assign_mechanic_ticket_not_found(self):
        self._create_mechanic()
        response = self.client.put('/service-tickets/999/assign-mechanic/1')
        self.assertEqual(response.status_code, 404)

    def test_assign_mechanic_mechanic_not_found(self):
        self._create_customer()
        self._create_ticket()
        response = self.client.put('/service-tickets/1/assign-mechanic/999')
        self.assertEqual(response.status_code, 404)

    # ---------- PUT /service-tickets/<id>/remove-mechanic/<id> ----------
    def test_remove_mechanic(self):
        self._create_customer()
        self._create_mechanic()
        self._create_ticket()
        self.client.put('/service-tickets/1/assign-mechanic/1')
        response = self.client.put('/service-tickets/1/remove-mechanic/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()['mechanics']), 0)

    def test_remove_mechanic_not_assigned(self):
        self._create_customer()
        self._create_mechanic()
        self._create_ticket()
        response = self.client.put('/service-tickets/1/remove-mechanic/1')
        self.assertEqual(response.status_code, 400)
        self.assertIn('not assigned', response.get_json()['message'])

    def test_remove_mechanic_ticket_not_found(self):
        self._create_mechanic()
        response = self.client.put('/service-tickets/999/remove-mechanic/1')
        self.assertEqual(response.status_code, 404)

    # ---------- PUT /service-tickets/<id>/edit ----------
    def test_edit_ticket_add_mechanics(self):
        self._create_customer()
        self._create_mechanic(email='m1@shop.com')
        self._create_mechanic(email='m2@shop.com')
        self._create_ticket()
        response = self.client.put('/service-tickets/1/edit', json={
            'add_ids': [1, 2],
            'remove_ids': []
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()['mechanics']), 2)

    def test_edit_ticket_remove_mechanics(self):
        self._create_customer()
        self._create_mechanic()
        self._create_ticket()
        self.client.put('/service-tickets/1/assign-mechanic/1')
        response = self.client.put('/service-tickets/1/edit', json={
            'add_ids': [],
            'remove_ids': [1]
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()['mechanics']), 0)

    def test_edit_ticket_not_found(self):
        response = self.client.put('/service-tickets/999/edit', json={
            'add_ids': [],
            'remove_ids': []
        })
        self.assertEqual(response.status_code, 404)

    def test_edit_ticket_invalid_mechanic_id(self):
        self._create_customer()
        self._create_ticket()
        response = self.client.put('/service-tickets/1/edit', json={
            'add_ids': [999],
            'remove_ids': []
        })
        self.assertEqual(response.status_code, 404)

    # ---------- PUT /service-tickets/<id>/add-part/<id> ----------
    def test_add_part(self):
        self._create_customer()
        self._create_ticket()
        self._create_inventory()
        response = self.client.put('/service-tickets/1/add-part/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()['parts']), 1)

    def test_add_part_duplicate(self):
        self._create_customer()
        self._create_ticket()
        self._create_inventory()
        self.client.put('/service-tickets/1/add-part/1')
        response = self.client.put('/service-tickets/1/add-part/1')
        self.assertEqual(response.status_code, 400)
        self.assertIn('already added', response.get_json()['message'])

    def test_add_part_ticket_not_found(self):
        self._create_inventory()
        response = self.client.put('/service-tickets/999/add-part/1')
        self.assertEqual(response.status_code, 404)

    def test_add_part_inventory_not_found(self):
        self._create_customer()
        self._create_ticket()
        response = self.client.put('/service-tickets/1/add-part/999')
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
