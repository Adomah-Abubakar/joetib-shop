from .cookie_store import RecentList, WishList

def global_context(request)->dict:
    
    return {
        'wishlist': WishList(request).to_objects(),
        'recentlist': RecentList(request).to_objects(),
    }