# Create your tests here.
from typing import List
from django.test import TestCase
from .sms import SmsApi
from .models import Contact, Sms, User



class SmsModelTest(TestCase):
    def test_get_recipients_count(self):
        sms: Sms = Sms.objects.create(
            message="test message",
        )
        sms.recipients.set(
            [
                User.objects.create(username="user1", phone_number="0123456789"),
                User.objects.create(username="user2", phone_number="0123456790"),
            ],
        )
        self.assertEqual(sms.get_recipients_count(), 2)

    def test_get_other_numbers_list(self):
        sms: Sms = Sms.objects.create(
            message="test message",
        )
        sms.recipients.set(
            [
                User.objects.create(username="user1", phone_number="0123456789"),
                User.objects.create(username="user2", phone_number="0123456790"),
            ],
        )
        self.assertEqual(sms.get_other_numbers_list(), [])

    def test_get_absolute_url(self):
        sms: Sms = Sms.objects.create(
            message="test message",
        )
        sms.recipients.set(
            [
                User.objects.create(username="user1", phone_number="0123456789"),
                User.objects.create(username="user2", phone_number="0123456790"),
            ],
        )
        self.assertEqual(sms.get_absolute_url(), "/messaging/sms-list/1/")

    def test_sms_with_no_recipients(self):
        sms: Sms = Sms.objects.create(
            message="test message",
        )

        self.assertEqual(sms.get_recipients_count(), 0)
        self.assertEqual(sms.get_other_numbers_list(), [])
        self.assertEqual(sms.other_recipients.count(), 0)
        self.assertEqual(sms.recipients.count(), 0)

    def test_sms_with_only_other_recipient_contacts(self):
        sms: Sms = Sms.objects.create(message="test message", )
        sms.other_recipients.set(
            [
                Contact.objects.create(
                    name="contact1", email="email1@email.com", phone_number="1111111111"
                ),
                Contact.objects.create(
                    name="contact2", email="email2@email.com", phone_number="2222222222"
                ),
            ],
        )

        self.assertEqual(sms.get_other_numbers_list(), [])
        self.assertEqual(sms.other_recipients.count(), 2)
        self.assertEqual(sms.is_draft, False)
        self.assertEqual(sms.sent, False)
        self.assertEqual(sms.recipients.count(), 0)
        self.assertEqual(sms.get_recipients_count(), 2)

    def test_sms_with_only_other_numbers(self):
        sms: Sms = Sms.objects.create(
            message="test message",
            other_numbers="1111111111, 2222222222, 3333333333, 4444444444",
        )

        self.assertEqual(len(sms.get_other_numbers_list()), 4)
        self.assertEqual(
            sms.get_other_numbers_list(),
            ["1111111111", "2222222222", "3333333333", "4444444444"],
        )
        self.assertEqual(sms.other_recipients.count(), 0)
        self.assertEqual(sms.is_draft, False)
        self.assertEqual(sms.sent, False)
        self.assertEqual(sms.recipients.count(), 0)
        self.assertEqual(sms.get_recipients_count(), 4)

    def test_sms_with_all_contact_options(self):
        sms: Sms = Sms.objects.create(
            message="test message",
            other_numbers="1111111111, 2222222222, 3333333333, 4444444444",
        )
        sms.recipients.set(
            [
                User.objects.create(username="user1", phone_number="0123456789"),
                User.objects.create(username="user2", phone_number="0123456790"),
            ]
        )
        sms.other_recipients.set(
            [
                Contact.objects.create(
                    name="contact1", email="email1@email.com", phone_number="1111111111"
                ),
                Contact.objects.create(
                    name="contact2", email="email2@email.com", phone_number="2222222222"
                ),
            ],
        )

        self.assertEqual(sms.is_draft, False)
        self.assertEqual(sms.sent, False)
        self.assertEqual(sms.recipients.count(), 2)
        self.assertEqual(sms.other_recipients.count(), 2)
        self.assertEqual(len(sms.get_other_numbers_list()), 4)
        self.assertEqual(sms.get_recipients_count(), 8)
