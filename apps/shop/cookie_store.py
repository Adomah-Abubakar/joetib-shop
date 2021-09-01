

from apps.store.models import Product



class SpecialList:
    def __init__(self, request, name, items_count=None):
        self.session = request.session
        self.items_count = items_count
        self.session_name = name
        self._list = self.session.get(self.session_name)
        if not self._list:
            self._list = self.session[self.session_name] = []
            
    
    def add(self, item):
        if not item.id in self._list:
            self._list.insert(0, item.id)
            print(self._list)
            self.save()
    
    def remove(self, item):
        if item.id in self._list:
            self._list.remove(item.id)
            self.save()
    
    def save(self):
        if self.items_count:
            self._list = self.session[self.session_name] = self._list[:self.items_count]
        self.session.modified = True
    
    
    
    def to_objects(self):
        if len(self._list) == 0:
            return None
        items = []
        for i in self._list:
            try:
                items.append( Product.objects.get(id=i))
            except Exception as e:
                self._list.remove(i)
                self.save()
                print(e)
        return items

class WishList(SpecialList):
    def __init__(self, request):
        super(WishList, self).__init__(request, 'wishlist')

class RecentList(SpecialList):
    def __init__(self, request):
        super().__init__(request, 'recentlist', 6)