from .cookie_store import RecentList, WishList
from store.models import Category
def global_context(request)->dict:
    
    return {
        'all_categories': Category.objects.all(),
        'wishlist': WishList(request).to_objects(),
        'recentlist': RecentList(request).to_objects(),
    }