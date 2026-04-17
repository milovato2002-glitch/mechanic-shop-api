import unittest
from app import create_app
from app.extensions import db


class TestInventory(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def _create_item(self, name='Oil Filter', price=12.99):
        return self.client.post('/inventory/', json={
            'name': name,
            'price': price
        })

    # ---------- POST /inventory/ ----------
    def test_create_inventory(self):
        response = self._create_item()
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['name'], 'Oil Filter')
        self.assertEqual(data['price'], 12.99)

    def test_create_inventory_missing_fields(self):
        response = self.client.post('/inventory/', json={
            'name': 'Oil Filter'
        })
        self.assertEqual(response.status_code, 400)

    def test_create_inventory_invalid_price(self):
        response = self.client.post('/inventory/', json={
            'name': 'Oil Filter',
            'price': 'not-a-number'
        })
        self.assertEqual(response.status_code, 400)

    # ---------- GET /inventory/ ----------
    def test_get_inventory_empty(self):
        response = self.client.get('/inventory/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])

    def test_get_inventory_with_data(self):
        self._create_item()
        response = self.client.get('/inventory/')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 1)

    # ---------- PUT /inventory/<id> ----------
    def test_update_inventory(self):
        self._create_item()
        response = self.client.put('/inventory/1', json={
            'name': 'Premium Oil Filter',
            'price': 24.99
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['name'], 'Premium Oil Filter')
        self.assertEqual(data['price'], 24.99)

    def test_update_inventory_not_found(self):
        response = self.client.put('/inventory/999', json={
            'name': 'Ghost Part',
            'price': 9.99
        })
        self.assertEqual(response.status_code, 404)

    def test_update_inventory_invalid_data(self):
        self._create_item()
        response = self.client.put('/inventory/1', json={
            'name': '',
            'price': 'bad'
        })
        self.assertEqual(response.status_code, 400)

    # ---------- DELETE /inventory/<id> ----------
    def test_delete_inventory(self):
        self._create_item()
        response = self.client.delete('/inventory/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn('deleted', response.get_json()['message'])

    def test_delete_inventory_not_found(self):
        response = self.client.delete('/inventory/999')
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
