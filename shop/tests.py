from django.test import Client, TestCase, RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware

middleware = SessionMiddleware(lambda x: x)

from shop.cookie_store import RecentList, SpecialList, WishList

# Create your tests here.

class MockItem:
    def __init__(self, id) -> None:
        self.id = id

    def __str__(self):
        return "some id"

class TestSpecialList(TestCase):
    def test_special_list_with(self):
        request = Client()
        special_list = SpecialList(
            request=request ,name="dummy", items_count=10
        )
        special_list.add(MockItem(1))
        special_list.add(MockItem(2))
        session = special_list.session
        self.assertEqual(session['dummy'], special_list._list)
        self.assertEqual(special_list._list, [2,1])
        self.assertEqual(session.get("dummy"), [2, 1])


class TestWishList(TestCase):
    def test_wish_list_with_two_items(self):
        request = Client()
        wish_list = WishList(request)
        wish_list.add(MockItem(1))
        wish_list.add(MockItem(2))
        session = wish_list.session
        self.assertEqual(session['wishlist'], wish_list._list)
        self.assertEqual(wish_list._list, [2,1])
        self.assertEqual(session.get("wishlist"), [2, 1])


class TestWishList(TestCase):
    def test_recent_list_with_two_items(self):
        request = Client()
        recent_list = RecentList(request)
        recent_list.add(MockItem(1))
        recent_list.add(MockItem(2))
        session = recent_list.session
        self.assertEqual(session['recentlist'], recent_list._list)
        self.assertEqual(recent_list._list, [2,1])
        self.assertEqual(session.get("recentlist"), [2, 1])
    
    def test_recent_list_with_more_than_six_items(self):
        request = Client()
        recent_list = RecentList(request)
        recent_list.add(MockItem(1))
        recent_list.add(MockItem(2))
        recent_list.add(MockItem(3))
        recent_list.add(MockItem(4))
        recent_list.add(MockItem(5))
        recent_list.add(MockItem(6))
        recent_list.add(MockItem(7))
        session = recent_list.session
        self.assertEqual(session['recentlist'], recent_list._list)
        self.assertEqual(recent_list._list, [7,6,5,4,3,2])
        self.assertEqual(session.get("recentlist"), [7,6,5,4,3,2])
