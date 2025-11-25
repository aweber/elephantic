"""Tests for Subscription Pydantic models."""

import unittest

import pydantic

from elephantic.models import subscription


class TestSubscription(unittest.TestCase):
    """Test Subscription model."""

    def test_subscription_requires_name(self):
        """Test that name is required."""
        with self.assertRaises(pydantic.ValidationError):
            subscription.Subscription(
                connection='host=publisher',
                publications=['pub1'],
            )

    def test_subscription_requires_connection(self):
        """Test that connection is required."""
        with self.assertRaises(pydantic.ValidationError):
            subscription.Subscription(
                name='sub_test',
                publications=['pub1'],
            )

    def test_subscription_requires_publications(self):
        """Test that publications is required."""
        with self.assertRaises(pydantic.ValidationError):
            subscription.Subscription(
                name='sub_test',
                connection='host=publisher',
            )

    def test_subscription_with_required_fields(self):
        """Test creating subscription with required fields."""
        sub = subscription.Subscription(
            name='sub_test',
            connection='host=publisher dbname=test',
            publications=['pub1', 'pub2'],
        )
        self.assertEqual(sub.name, 'sub_test')
        self.assertEqual(len(sub.publications), 2)


if __name__ == '__main__':
    unittest.main()
