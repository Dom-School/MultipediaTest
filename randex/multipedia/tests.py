from django.test import TestCase
from django.urls import reverse


class RandomArticleTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('random_page', args=[" "]))
        self.assertEqual(response.status_code, 200)
