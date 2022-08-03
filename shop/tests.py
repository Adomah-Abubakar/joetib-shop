from django.test import Client, TestCase, RequestFactory, override_settings
from django.contrib.sessions.middleware import SessionMiddleware
from django.urls import reverse
from config.tests import TEST_MEDIA_ROOT, CustomTestClass, createImage
from store.models import Category, Order, OrderItem, Product, User
from http import HTTPStatus

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
        special_list = SpecialList(request=request, name="dummy", items_count=10)
        special_list.add(MockItem(1))
        special_list.add(MockItem(2))
        session = special_list.session
        self.assertEqual(session["dummy"], special_list._list)
        self.assertEqual(special_list._list, [2, 1])
        self.assertEqual(session.get("dummy"), [2, 1])

    def test_remove_item_from_list(self):
        request = Client()
        special_list = SpecialList(request=request, name="dummy", items_count=10)
        special_list.add(MockItem(1))
        special_list.add(MockItem(2))
        special_list.remove(MockItem(2))
        session = special_list.session
        self.assertEqual(session["dummy"], special_list._list)
        self.assertEqual(special_list._list, [1])
        self.assertEqual(session.get("dummy"), [1])
        self.assertEqual(special_list.to_objects(), [])

    def test_item_to_objects_when_product_exists(self):
        request = Client()
        special_list = SpecialList(request=request, name="dummy", items_count=10)
        category = Category.objects.create(name="test category")
        product: Product = Product.objects.create(
            name="Test Product",
            category=category,
            price=100,
            image=createImage(),
            description="some description",
        )
        special_list.add(product)
        session = special_list.session
        self.assertEqual(session["dummy"], special_list._list)
        self.assertEqual(special_list._list, [1])
        self.assertEqual(session.get("dummy"), [1])
        self.assertEqual(special_list.to_objects(), [product])

    def test_item_list_should_not_have_duplicate_values(self):
        request = Client()
        special_list = SpecialList(request=request, name="dummy", items_count=10)
        category = Category.objects.create(name="test category")
        product: Product = Product.objects.create(
            name="Test Product",
            category=category,
            price=100,
            image=createImage(),
            description="some description",
        )
        special_list.add(product)
        special_list.add(product)
        special_list.add(product)
        special_list.add(product)
        special_list.add(product)
        session = special_list.session
        self.assertEqual(session["dummy"], special_list._list)
        self.assertEqual(special_list._list, [1])
        self.assertEqual(session.get("dummy"), [1])
        self.assertEqual(special_list.to_objects(), [product])

class TestWishList(TestCase):
    def test_wish_list_with_two_items(self):
        request = Client()
        wish_list = WishList(request)
        wish_list.add(MockItem(1))
        wish_list.add(MockItem(2))
        session = wish_list.session
        self.assertEqual(session["wishlist"], wish_list._list)
        self.assertEqual(wish_list._list, [2, 1])
        self.assertEqual(session.get("wishlist"), [2, 1])


class TestWishList(TestCase):
    def test_recent_list_with_two_items(self):
        request = Client()
        recent_list = RecentList(request)
        recent_list.add(MockItem(1))
        recent_list.add(MockItem(2))
        session = recent_list.session
        self.assertEqual(session["recentlist"], recent_list._list)
        self.assertEqual(recent_list._list, [2, 1])
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
        self.assertEqual(session["recentlist"], recent_list._list)
        self.assertEqual(recent_list._list, [7, 6, 5, 4, 3, 2])
        self.assertEqual(session.get("recentlist"), [7, 6, 5, 4, 3, 2])


@override_settings(
    STATICFILES_STORAGE="whitenoise.storage.CompressedStaticFilesStorage"
)
@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class TestHomePage(CustomTestClass):
    """Test to see that no exceptions are raised when trying to access the homepage"""

    def test_homepage_works_with_no_http_errors(self):
        response = self.client.get("")
        self.assertEqual(response.status_code, HTTPStatus.OK, "Homepage is not working")
        self.assertEqual(response.context['banners'].count(), 0)
        self.assertEqual(response.context['all_products_count'], 0)
        self.assertEqual(response.context['categories'].count(), 0)

    def test_homepage_works_when_there_is_a_category_and_product(self):
        category = Category.objects.create(name="test category")
        product: Product = Product.objects.create(
            name="Test Product",
            category=category,
            price=100,
            image=createImage(),
            description="some description",
        )
        response = self.client.get("")

        self.assertEqual(response.status_code, HTTPStatus.OK, "Homepage is not working")
        self.assertEqual(response.context['banners'].count(), 0)
        self.assertEqual(response.context['all_products_count'], 1)
        self.assertEqual(response.context['categories'].count(), 1)
        self.assertEqual(response.context['categories'].first(), category)
        self.assertEqual(response.context['categories'].first().products.first(), product)

@override_settings(
    STATICFILES_STORAGE="whitenoise.storage.CompressedStaticFilesStorage"
)
@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class TestProductPage(CustomTestClass, TestCase):
    """Test to see that no exceptions are raised when trying to access the homepage"""

    def test_product_list_works_with_no_http_errors(self):
        response = self.client.get(reverse("shop:product-list"))
        self.assertEqual(response.status_code, HTTPStatus.OK, "Homepage is not working")

    def test_product_list_with_no_products(self):
        response = self.client.get(reverse("shop:product-list"))
        self.assertEqual(response.status_code, HTTPStatus.OK, "Homepage is not working")
        self.assertEqual(response.context["categories"].count(), 0)
        self.assertEqual(response.context["all_products_count"], 0)
        self.assertEqual(response.context["search_query"], None)
        self.assertEqual(response.context["products"].count(), 0)

    def test_product_list_with_products(self):
        category = Category.objects.create(name="test category")
        product = Product.objects.create(
            name="Test Product",
            category=category,
            price=100,
            image=createImage(),
            description="some description",
        )
        response = self.client.get(reverse("shop:product-list"))
        self.assertEqual(response.status_code, HTTPStatus.OK, "Homepage is not working")
        self.assertEqual(response.context["categories"].count(), 1)
        self.assertEqual(response.context["all_products_count"], 1)
        self.assertEqual(response.context["search_query"], None)
        self.assertEqual(response.context["products"][0], product)


    def test_product_list_with_search_query_when_there_is_no_product_match(self):
        category = Category.objects.create(name="test category")
        product = Product.objects.create(
            name="Test Product",
            category=category,
            price=100,
            image=createImage(),
            description="some description",
        )
        response = self.client.get(reverse("shop:product-list") + "?search=stringthatshouldnotmatch")
        self.assertEqual(response.status_code, HTTPStatus.OK, "Homepage is not working")
        self.assertEqual(response.context["categories"].count(), 1)
        self.assertEqual(response.context["all_products_count"], 1)
        self.assertEqual(response.context["search_query"],  "stringthatshouldnotmatch")
        self.assertEqual(response.context["products"].count(), 0)
    
    def test_product_list_with_search_query_when_there_is_a_product_match(self):
        category = Category.objects.create(name="test category")
        product = Product.objects.create(
            name="Test Product",
            category=category,
            price=100,
            image=createImage(),
            description="some description",
        )
        response = self.client.get(reverse("shop:product-list") + "?search=test")
        self.assertEqual(response.status_code, HTTPStatus.OK, "Homepage is not working")
        self.assertEqual(response.context["categories"].count(), 1)
        self.assertEqual(response.context["all_products_count"], 1)
        self.assertEqual(response.context["search_query"],  "test")
        self.assertEqual(response.context["products"].count(), 1)
        self.assertEqual(response.context["products"][0], product)




@override_settings(
    STATICFILES_STORAGE="whitenoise.storage.CompressedStaticFilesStorage"
)
@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class TestProductDetailPage(CustomTestClass, TestCase):
    """Test to see that no exceptions are raised when trying to access the homepage"""

    def test_product_list_works_with_id_that_does_not_exist(self):
        response = self.client.get(reverse("shop:product-detail", kwargs={'pk': 1}))
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND, "Product Detail view should have raised an exception")

    def test_product_detail_with_existing_products(self):
        category = Category.objects.create(name="test category")
        product: Product = Product.objects.create(
            name="Test Product",
            category=category,
            price=100,
            image=createImage(),
            description="some description",
        )
        response = self.client.get(product.get_absolute_url())
        self.assertEqual(response.status_code, HTTPStatus.OK,)
        self.assertEqual(response.context["product"], product)
        self.assertEqual(len(response.context["recentlist"]), 1)


@override_settings(
    STATICFILES_STORAGE="whitenoise.storage.CompressedStaticFilesStorage"
)
@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class TestAddToOrder(TestCase):
    def test_add_product_to_order_when_logged_out(self):
        category = Category.objects.create(name="test category")
        product: Product = Product.objects.create(
            name="Test Product",
            category=category,
            price=100,
            image=createImage(),
            description="some description",
        )
        url = reverse("shop:add-product-to-cart", kwargs={"product_pk": product.pk})
        response = self.client.get(
            url
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Order.objects.count(), 0, "User managed to add to cart despite logged out.")
        self.assertRedirects(response, reverse("account_login") + f"?next={url}", status_code=HTTPStatus.FOUND)
    
    def test_add_to_product_when_logged_in(self):
        User.objects.create_user(username="testuser", email="testemail@email.com", password="test_password")
        
        
        category = Category.objects.create(name="test category")
        product: Product = Product.objects.create(
            name="Test Product",
            category=category,
            price=100,
            image=createImage(),
            description="some description",
        )
        client = Client()
        user= User.objects.first()
        client.force_login(user)
        response = client.get(
            reverse("shop:add-product-to-cart", kwargs={"product_pk": product.pk})
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND, "Adding to cart failed")
        self.assertEqual(Order.objects.count(), 1)
        order: Order = Order.objects.first()
        self.assertEqual(order.user, user)
        self.assertEqual(order.order_items.count(), 1)
        self.assertEqual(order.order_items.first().product, product)
        self.assertRedirects(response, reverse("shop:cart"), status_code=HTTPStatus.FOUND)




@override_settings(
    STATICFILES_STORAGE="whitenoise.storage.CompressedStaticFilesStorage"
)
@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class TestAddToCartJson(TestCase):
    def test_add_product_to_order_when_logged_out(self):
        category = Category.objects.create(name="test category")
        product: Product = Product.objects.create(
            name="Test Product",
            category=category,
            price=100,
            image=createImage(),
            description="some description",
        )
        url = reverse("shop:add-product-to-cart-json", kwargs={"product_pk": product.pk})
        response = self.client.get(
            url
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Order.objects.count(), 0, "User managed to add to cart despite logged out.")
        self.assertRedirects(response, reverse("account_login") + f"?next={url}", status_code=HTTPStatus.FOUND)
    
    def test_add_to_product_when_logged_in(self):
        User.objects.create_user(username="testuser", email="testemail@email.com", password="test_password")
        
        
        category = Category.objects.create(name="test category")
        product: Product = Product.objects.create(
            name="Test Product",
            category=category,
            price=100,
            image=createImage(),
            description="some description",
        )
        client = Client()
        user= User.objects.first()
        client.force_login(user)
        response = client.get(
            reverse("shop:add-product-to-cart-json", kwargs={"product_pk": product.pk})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK, "Adding to cart failed")
        self.assertEqual(Order.objects.count(), 1)
        order: Order = Order.objects.first()
        self.assertEqual(order.user, user)
        self.assertEqual(order.order_items.count(), 1)
        self.assertEqual(order.order_items.first().product, product)
        self.assertEqual(order.order_items.first().get_single_item_price(), 100)
        self.assertEqual(order.order_items.first().get_total_price(), 100)
        json_data = response.json()
        self.assertEqual(json_data['quantity'], 1)
        self.assertEqual(json_data['total'], "100.00")

    
    def test_add_to_product_when_logged_in_and_item_is_already_in_order(self):
        User.objects.create_user(username="testuser", email="testemail@email.com", password="test_password")
        category = Category.objects.create(name="test category")
        product: Product = Product.objects.create(
            name="Test Product",
            category=category,
            price=100,
            image=createImage(),
            description="some description",
        )
        client = Client()
        user= User.objects.first()
        client.force_login(user)
        order = Order.objects.get_or_create(ordered=False, user=user)[0]
        order_item: OrderItem = OrderItem.objects.create(
            order=order, product=product, quantity=1
        )
        response = client.get(
            reverse("shop:add-product-to-cart-json", kwargs={"product_pk": product.pk})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK, "Adding to cart failed")
        self.assertEqual(Order.objects.count(), 1)
        order: Order = Order.objects.first()
        self.assertEqual(order.user, user)
        self.assertEqual(order.order_items.count(), 1)
        self.assertEqual(order.order_items.first().quantity, 2)
        self.assertEqual(order.order_items.first().product, product)
        json_data = response.json()
        self.assertEqual(json_data['quantity'], 2)
        self.assertEqual(json_data['total'], "200.00")


@override_settings(
    STATICFILES_STORAGE="whitenoise.storage.CompressedStaticFilesStorage"
)
@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class CartViewTest(TestCase):
    def test_access_cart_view_without_loggin_in_should_fail(self):
        url = reverse("shop:cart")
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND, "Unauthenticated user was allowed to view cart")
        self.assertRedirects(response, reverse("account_login") + f"?next={url}" , status_code=HTTPStatus.FOUND)

    def test_access_cart_view_when_logged_in_should_succeed(self):
        User.objects.create_user(username="testuser", email="testemail@email.com", password="test_password")
        user= User.objects.first()
        self.client.force_login(user)
        response = self.client.get(reverse("shop:cart"))
        self.assertEqual(response.status_code, HTTPStatus.OK, "Authenticated User was not able to view cart")
        self.assertEqual(response.context['order'].order_items.count(), 0)


    def test_access_cart_view_when_logged_in_and_there_is_an_item_in_cart_should_succeed(self):
        User.objects.create_user(username="testuser", email="testemail@email.com", password="test_password")
        user= User.objects.first()
        self.client.force_login(user)
        category = Category.objects.create(name="test category")
        product: Product = Product.objects.create(
            name="Test Product",
            category=category,
            price=100,
            image=createImage(),
            description="some description",
        )
        order = Order.objects.get_or_create(ordered=False, user=user)[0]
        order_item: OrderItem = OrderItem.objects.create(
            order=order, product=product, quantity=1
        )
        response = self.client.get(reverse("shop:cart"))
        self.assertEqual(response.status_code, HTTPStatus.OK, "Authenticated User was not able to view cart")
        self.assertEqual(response.context['order'], order)
        self.assertEqual(response.context['order'].order_items.count(), 1)
        self.assertEqual(response.context['order'].order_items.first().quantity, 1)



    