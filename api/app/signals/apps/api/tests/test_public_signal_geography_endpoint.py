# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2022 Gemeente Amsterdam
from datetime import timedelta

from django.contrib.gis.geos import Point
from django.utils import timezone
from freezegun import freeze_time

from signals.apps.signals.factories import (
    CategoryFactory,
    ParentCategoryFactory,
    SignalFactory,
    SignalFactoryValidLocation
)
from signals.apps.signals.tests.valid_locations import ARENA, STADHUIS
from signals.test.utils import SignalsBaseApiTestCase


class TestPublicSignalViewSet(SignalsBaseApiTestCase):
    geography_endpoint = "/signals/v1/public/signals/geography"

    def test_get_geojson(self):
        """
        Return the GEOJson containing all signals in the child category
        """
        parent_category = ParentCategoryFactory.create()
        child_category = CategoryFactory.create(parent=parent_category, public_name='Public category for testing',
                                                is_public_accessible=True)

        now = timezone.now()
        for x in range(5):
            with(freeze_time(now-timedelta(days=x))):
                SignalFactoryValidLocation.create(category_assignment__category=child_category)

        response = self.client.get(f'{self.geography_endpoint}/?maincategory_slug={parent_category.slug}'
                                   f'&category_slug={child_category.slug}&bbox=4.700000,52.200000,5.000000,52.500000')
        self.assertEqual(200, response.status_code)
        self.assertEqual(5, int(response.headers['X-Total-Count']))

        data = response.json()
        self.assertEqual(5, len(data['features']))

        for feature in data['features']:
            self.assertEqual(feature['properties']['category']['name'], child_category.public_name)

    def test_get_geojson_bbox_filter(self):
        """
        Return the GEOJson containing all signals in the child category in a certain bbox
        """
        parent_category = ParentCategoryFactory.create()
        child_category = CategoryFactory.create(parent=parent_category, public_name='Public category for testing',
                                                is_public_accessible=True)

        now = timezone.now()
        for x in range(5):
            with(freeze_time(now-timedelta(days=x))):
                # Should appear in the response
                SignalFactory.create(location__geometrie=Point(STADHUIS['lon'], STADHUIS['lat']),
                                     location__buurt_code=STADHUIS['buurt_code'],
                                     category_assignment__category=child_category)

                # Should not appear in the response
                SignalFactory.create(location__geometrie=Point(ARENA['lon'], ARENA['lat']),
                                     location__buurt_code=ARENA['buurt_code'],
                                     category_assignment__category=child_category)

        response = self.client.get(f'{self.geography_endpoint}/?maincategory_slug={parent_category.slug}'
                                   f'&category_slug={child_category.slug}&bbox=4.875759,52.360656,4.921221,52.37942')
        self.assertEqual(200, response.status_code)
        self.assertEqual(5, int(response.headers['X-Total-Count']))

        data = response.json()
        self.assertEqual(5, len(data['features']))

        for feature in data['features']:
            self.assertEqual(feature['properties']['category']['name'], child_category.public_name)

    def test_get_geojson_no_signals(self):
        """
        Return an empty FeatureCollection because there are no signals at all
        """
        parent_category = ParentCategoryFactory.create()
        child_category = CategoryFactory.create(parent=parent_category, public_name='Public category for testing',
                                                is_public_accessible=True)

        response = self.client.get(f'{self.geography_endpoint}/?maincategory_slug={parent_category.slug}'
                                   f'&category_slug={child_category.slug}&bbox=4.700000,52.200000,5.000000,52.500000')
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, int(response.headers['X-Total-Count']))

        data = response.json()
        self.assertIsNone(data['features'])

    def test_get_geojson_no_signals_in_category(self):
        """
        Return an empty FeatureCollection because there are no signals in the category
        """
        parent_category = ParentCategoryFactory.create()
        child_category = CategoryFactory.create(parent=parent_category, public_name='Public category for testing',
                                                is_public_accessible=True)

        SignalFactoryValidLocation.create_batch(5)

        response = self.client.get(f'{self.geography_endpoint}/?maincategory_slug={parent_category.slug}'
                                   f'&category_slug={child_category.slug}&bbox=4.700000,52.200000,5.000000,52.500000')
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, int(response.headers['X-Total-Count']))

        data = response.json()
        self.assertIsNone(data['features'])

    def test_get_no_query_parameters_provided(self):
        """
        The query parameters bbox, maincategory_slug and category_slug are required
        """
        response = self.client.get(self.geography_endpoint)
        self.assertEqual(400, response.status_code)

        data = response.json()

        self.assertIn('maincategory_slug', data.keys())
        self.assertEqual(1, len(data['maincategory_slug']))
        self.assertEqual('Dit veld is vereist.', data['maincategory_slug'][0])

        self.assertIn('category_slug', data.keys())
        self.assertEqual(1, len(data['category_slug']))
        self.assertEqual('Dit veld is vereist.', data['category_slug'][0])

    def test_get_invalid_category_in_query_parameters(self):
        """
        The query parameters category_slug should be a slug from a valid category that is public accessible
        """
        parent_category = ParentCategoryFactory.create()
        child_category = CategoryFactory.create(parent=parent_category, is_public_accessible=False)

        # Now provide a BBOX, the only error should be the invalid category
        response = self.client.get(f'{self.geography_endpoint}/?maincategory_slug={parent_category.slug}'
                                   f'&category_slug={child_category.slug}&bbox=4.700000,52.200000,5.000000,52.500000')
        self.assertEqual(400, response.status_code)

        data = response.json()
        self.assertNotIn('bbox', data.keys())
        self.assertNotIn('maincategory_slug', data.keys())

        self.assertIn('category_slug', data.keys())
        self.assertEqual(1, len(data['category_slug']))
        self.assertEqual(f'Selecteer een geldige keuze. {child_category.slug} is geen beschikbare keuze.',
                         data['category_slug'][0])

    def test_get_group_by(self):
        """
        Return the GEOJson containing the first created_at in a BBOX grouped by a category
        """
        parent_category = ParentCategoryFactory.create()
        child_category = CategoryFactory.create(parent=parent_category, public_name='Public category for testing',
                                                is_public_accessible=True)

        now = timezone.now()
        for x in range(5):
            with(freeze_time(now-timedelta(days=x))):
                # Should appear in the response
                SignalFactory.create(location__geometrie=Point(STADHUIS['lon'], STADHUIS['lat']),
                                     location__buurt_code=STADHUIS['buurt_code'],
                                     category_assignment__category=child_category)

        response = self.client.get(f'{self.geography_endpoint}/?maincategory_slug={parent_category.slug}'
                                   f'&category_slug={child_category.slug}&bbox=4.875759,52.360656,4.921221,52.37942'
                                   '&group_by=category')
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, int(response.headers['X-Total-Count']))

        data = response.json()
        self.assertEqual(1, len(data['features']))
        self.assertEqual(data['features'][0]['properties']['category']['name'], child_category.public_name)

    def test_lon_lat_parameters(self):
        """
        Return the GEOJson containing all signals in the child category
        """
        parent_category = ParentCategoryFactory.create()
        child_category = CategoryFactory.create(parent=parent_category, public_name='Public category for testing',
                                                is_public_accessible=True)

        signal = SignalFactoryValidLocation.create(category_assignment__category=child_category)
        lon = signal.location.geometrie.x
        lat = signal.location.geometrie.y

        response = self.client.get(f'{self.geography_endpoint}/?maincategory_slug={parent_category.slug}'
                                   f'&category_slug={child_category.slug}&lon={lon}&lat={lat}')

        self.assertEqual(200, response.status_code)
        self.assertEqual(1, int(response.headers['X-Total-Count']))

        data = response.json()
        self.assertEqual(1, len(data['features']))

        for feature in data['features']:
            self.assertEqual(feature['properties']['category']['name'], child_category.public_name)

    def test_missing_bbox_and_lonlat(self):
        """
        Validate that when neither bbox or lon/lat is filled in to return a non_field_error
        """
        parent_category = ParentCategoryFactory.create()
        child_category = CategoryFactory.create(parent=parent_category, is_public_accessible=False)
        response = self.client.get(f'{self.geography_endpoint}/?maincategory_slug={parent_category.slug}'
                                   f'&category_slug={child_category.slug}')

        data = response.json()
        self.assertEqual(400, response.status_code)
        self.assertIn('non_field_errors', data.keys())
        self.assertEqual(1, len(data['non_field_errors']))
        self.assertEqual('Either bbox or lon/lat must be filled in', data['non_field_errors'][0])
