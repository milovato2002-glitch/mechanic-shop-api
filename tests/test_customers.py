import unittest
from app import create_app
from app.extensions import db
from app.models.customer import Customer
from app.utils.auth import encode_token


class TestCustomers(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    # ---------- POST /customers/ ----------
    def test_create_customer(self):
        response = self.client.post('/customers/', json={
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '555-1234'
        })
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['name'], 'John Doe')
        self.assertEqual(data['email'], 'john@example.com')

    def test_create_customer_missing_fields(self):
        response = self.client.post('/customers/', json={
            'name': 'John Doe'
        })
        self.assertEqual(response.status_code, 400)

    def test_create_customer_empty_body(self):
        response = self.client.post('/customers/', json={})
        self.assertEqual(response.status_code, 400)

    # ---------- GET /customers/ ----------
    def test_get_customers_empty(self):
        response = self.client.get('/customers/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])

    def test_get_customers_with_data(self):
        self.client.post('/customers/', json={
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '555-1234'
        })
        with self.app.app_context():
            from app.extensions import cache
            cache.clear()
        response = self.client.get('/customers/')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 1)

    def test_get_customers_pagination(self):
        for i in range(15):
            self.client.post('/customers/', json={
                'name': f'Customer {i}',
                'email': f'c{i}@example.com',
                'phone': '555-0000'
            })
        with self.app.app_context():
            from app.extensions import cache
            cache.clear()
        response = self.client.get('/customers/?page=1&per_page=5')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 5)

    # ---------- PUT /customers/<id> ----------
    def test_update_customer(self):
        self.client.post('/customers/', json={
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '555-1234'
        })
        response = self.client.put('/customers/1', json={
            'name': 'John Updated',
            'email': 'john@example.com',
            'phone': '555-9999'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['name'], 'John Updated')

    def test_update_customer_not_found(self):
        response = self.client.put('/customers/999', json={
            'name': 'Nobody',
            'email': 'nobody@example.com',
            'phone': '555-0000'
        })
        self.assertEqual(response.status_code, 404)

    def test_update_customer_missing_required_fields(self):
        self.client.post('/customers/', json={
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '555-1234'
        })
        response = self.client.put('/customers/1', json={})
        self.assertIn(response.status_code, [200, 400])

    # ---------- DELETE /customers/<id> ----------
    def test_delete_customer(self):
        self.client.post('/customers/', json={
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '555-1234'
        })
        response = self.client.delete('/customers/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn('deleted', response.get_json()['message'])

    def test_delete_customer_not_found(self):
        response = self.client.delete('/customers/999')
        self.assertEqual(response.status_code, 404)

    # ---------- POST /customers/login ----------
    def test_login_success(self):
        self.client.post('/customers/', json={
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '555-1234'
        })
        response = self.client.post('/customers/login', json={
            'email': 'john@example.com',
            'password': 'anything'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.get_json())

    def test_login_invalid_email(self):
        response = self.client.post('/customers/login', json={
            'email': 'nonexistent@example.com',
            'password': 'anything'
        })
        self.assertEqual(response.status_code, 401)

    def test_login_missing_fields(self):
        response = self.client.post('/customers/login', json={
            'email': 'john@example.com'
        })
        self.assertEqual(response.status_code, 400)

    # ---------- GET /customers/my-tickets ----------
    def test_my_tickets_with_token(self):
        self.client.post('/customers/', json={
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '555-1234'
        })
        with self.app.app_context():
            token = encode_token(1)
        response = self.client.get('/customers/my-tickets', headers={
            'Authorization': f'Bearer {token}'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), list)

    def test_my_tickets_missing_token(self):
        response = self.client.get('/customers/my-tickets')
        self.assertEqual(response.status_code, 401)
        self.assertIn('Missing token', response.get_json()['message'])

    def test_my_tickets_invalid_token(self):
        response = self.client.get('/customers/my-tickets', headers={
            'Authorization': 'Bearer invalidtoken123'
        })
        self.assertEqual(response.status_code, 401)
        self.assertIn('Invalid', response.get_json()['message'])

    # ---------- GET /customers/test-token ----------
    def test_test_token_endpoint(self):
        response = self.client.get('/customers/test-token', headers={
            'Authorization': 'Bearer sometoken'
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('authorization_header', data)
        self.assertEqual(data['authorization_header'], 'Bearer sometoken')


if __name__ == '__main__':
    unittest.main()
