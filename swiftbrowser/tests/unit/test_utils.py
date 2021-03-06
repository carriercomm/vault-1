# -*- coding: utf-8 -*-

from mock import patch
from unittest import TestCase

from swiftclient import client

from swiftbrowser import utils

from vault.tests.fakes import fake_request
from swiftbrowser.tests import fakes


class TestSwiftbrowserUtils(TestCase):

    def test_remove_duplicates_from_acl(self):
        given = 'projectfake:userfake,projectfake2:userfake2,projectfake:userfake'
        expected = 'projectfake:userfake,projectfake2:userfake2'
        computed = utils.remove_duplicates_from_acl(given)

        self.assertEqual(expected, computed)

    def test_remove_duplicates_from_acl_empty_acls(self):
        given = ''
        expected = ''
        computed = utils.remove_duplicates_from_acl(given)

        self.assertEqual(expected, computed)

    def test_remove_duplicates_from_acl_no_duplicated_acls(self):
        given = 'projectfake:userfake,projectfake2:userfake2'
        expected = 'projectfake:userfake,projectfake2:userfake2'
        computed = utils.remove_duplicates_from_acl(given)

        self.assertEqual(expected, computed)

    def test_replace_hyphens(self):
        fake_dict = {'content-length': '147', 'content-type': 'application/json'}
        expected = {'content_length': '147', 'content_type': 'application/json'}
        modified = utils.replace_hyphens(fake_dict)

        self.assertEqual(modified, expected)

    @patch('swiftbrowser.utils.client.get_account')
    def test_get_temp_key(self, mock_get_account):
        expected_key = 'asgdia7239rgahsjbfhsd'
        mock_get_account.return_value = [
            {'x-account-meta-temp-url-key': expected_key}
        ]

        computed_key = utils.get_temp_key('http://fakeurl', 'faketoken', False)

        self.assertEqual(expected_key, computed_key)

    @patch('swiftbrowser.utils.client.get_account')
    def test_get_temp_key_get_account_exception(self, mock_get_account):
        mock_get_account.side_effect = client.ClientException('')
        computed_key = utils.get_temp_key('http://fakeurl', 'faketoken', False)
        self.assertIsNone(computed_key)

    @patch('swiftbrowser.utils.client.post_account')
    @patch('swiftbrowser.utils.client.get_account')
    def test_get_temp_key_get_account_no_key_retrieved_on_get_account(self, mock_get_account, mock_post_account):
        mock_get_account.return_value = [{}]
        retrieved_key = utils.get_temp_key('http://fakeurl', 'faketoken', False)

        name, args, kargs = mock_post_account.mock_calls[0]
        computed_key = kargs['headers']['x-account-meta-temp-url-key']

        self.assertEqual(retrieved_key, computed_key)

    @patch('swiftbrowser.utils.client.post_account')
    @patch('swiftbrowser.utils.client.get_account')
    def test_get_temp_key_post_account_exception(self, mock_get_account, mock_post_account):
        mock_get_account.return_value = [{}]
        mock_post_account.side_effect = client.ClientException('')

        computed_key = utils.get_temp_key('http://fakeurl', 'faketoken', False)

        self.assertIsNone(computed_key)

    def test_get_endpoint_urls(self):
        user = fakes.FakeUser(1, 'user')
        request = fake_request(user=user)

        admin_url = utils.get_endpoint(request, 'adminURL')
        expected_admin_url = 'https://fake.api.globoi.com/v1/AUTH_1'

        public_url = utils.get_endpoint(request, 'publicURL')
        expected_public_url = 'http://fake.s3.glbimg.com/v1/AUTH_1'

        internal_url = utils.get_endpoint(request, 'internalURL')
        expected_internal_url = 'http://fake.i.s3.glbimg.com/v1/AUTH_1'

        self.assertEqual(admin_url, expected_admin_url)
        self.assertEqual(public_url, expected_public_url)
        self.assertEqual(internal_url, expected_internal_url)

    def test_get_endpoint_not_found_return_none(self):
        user = fakes.FakeUser(1, 'user')
        request = fake_request(user=user)
        endpoint = utils.get_endpoint(request, 'Invalid')
        self.assertEqual(endpoint, None)

    def test_get_endpoint_without_service_catalog(self):
        user = fakes.FakeUser(1, 'user')
        request = fake_request(user=user)
        request.session['service_catalog'] = None

        with self.assertRaises(ValueError):
            utils.get_endpoint(request, 'internalURL')
