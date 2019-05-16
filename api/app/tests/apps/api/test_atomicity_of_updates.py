"""
Test and document the behavior of the Signal instance updates via patches.
"""
import os, json, unittest

from signals.apps.signals.models import Attachment, Category, History, Signal, StatusMessageTemplate
from signals.apps.signals import workflow

from tests.apps.signals import factories
from tests.test import SIAReadUserMixin, SIAReadWriteUserMixin, SignalsBaseApiTestCase

from rest_framework.reverse import reverse

from urllib.parse import urlparse

from unittest import mock
from django.core.exceptions import ValidationError

THIS_DIR = os.path.dirname(__file__)


class TestPrivateSignalViewSet(SIAReadWriteUserMixin, SignalsBaseApiTestCase):
    """
    Test basic properties of the V1 /signals/v1/private/signals endpoint.

    Note: we check both the list endpoint and associated detail endpoint.
    """

    def assertUrlPathMatch(self, url1, url2):
        path1 = urlparse(url1).path
        path2 = urlparse(url2).path

        self.assertEqual(path1, path2)

    def setUp(self):


        self.list_endpoint = '/signals/v1/private/signals/'
        self.detail_endpoint = '/signals/v1/private/signals/{pk}'
        self.history_endpoint = '/signals/v1/private/signals/{id}/history'

        self.signal = factories.SignalFactoryWithImage.create(
            status__state=workflow.GEMELD,
            status__text='INITIAL',
        )

        self.test_cat_main = factories.CategoryFactory.create(
            parent=None,
            name='CAT_MAIN',
            handling=Category.HANDLING_REST,
        )
        self.test_cat_sub = factories.CategoryFactory.create(
            parent=self.test_cat_main,
            name='CAT_SUB',
            handling=Category.HANDLING_REST,
        )

        self.link_test_cat_sub = reverse(
            'v1:category-detail', kwargs={
                'slug': self.test_cat_main.slug,
                'sub_slug': self.test_cat_sub.slug,
            }
        )

        # Payload for signal PATCH requests
        self.payload = {
            'status': {
                'state': workflow.BEHANDELING,
                'text': 'TEST STATUS UPDATE',
            },
            'category': {
                'sub_category': self.link_test_cat_sub,
                'text': 'TEST CATEGORY ASSIGNMENT UPDATE',
            }
        }

    def test_update_status_and_category(self):
        """
        Test happy flow PATCH update to status and category assignment.
        """
        self.client.force_authenticate(user=self.sia_read_write_user)
        detail_endpoint = self.detail_endpoint.format(pk=self.signal.id)

        response = self.client.patch(detail_endpoint, data=self.payload, format='json')
        self.assertEqual(response.status_code, 200)
        response_data = response.json()

        # Check that our double update worked
        self.assertEqual(response_data['status']['state'], self.payload['status']['state'])
        self.assertEqual(response_data['status']['text'], response_data['status']['text'])

        self.assertUrlPathMatch(
            response_data['category']['category_url'], self.payload['category']['sub_category'])
        self.assertEqual(response_data['category']['text'], self.payload['category']['text'])

    @unittest.skip('PATCHES on several top level properties are not atomic')
    @mock.patch("signals.apps.api.v1.serializers.PrivateSignalSerializerDetail._update_category_assignment")  # noqa: E501
    def test_update_status_and_failed_category(self, mocked):
        self.client.force_authenticate(user=self.sia_read_write_user)
        detail_endpoint = self.detail_endpoint.format(pk=self.signal.id)

        mocked.side_effect = ValidationError('SOME FAILURE')
        response = self.client.patch(detail_endpoint, data=self.payload, format='json')
        self.assertEqual(response.status_code, 400)

        # Check the state / category after this failed patch (desired behavior
        # is that the update fails in full).
        response = self.client.get(detail_endpoint)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(
            response_data['status']['state'],
            workflow.GEMELD
        )
