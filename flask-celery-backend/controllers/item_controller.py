# make Python do floating-point division by default
from __future__ import division
# make string literals be Unicode strings
from __future__ import unicode_literals

from models.model import Item

class ItemController():
    
    @staticmethod
    def items_list():
        '''
        Get a list of all item names
        '''
        return Item.query.all()
        
    @staticmethod
    def item_add(name, quantity, price, url, image_url):
        '''
        Create a new item with the specified properties (administrative only)
        '''
        item = Item(name=name, quantity_in_stock=quantity, base_price=price, product_url=url, image_url=image_url)
        item.add()
    
    @staticmethod
    def item_get_info(name):
        '''
        Get the quantity, base price, product url, and image url for the
        specified item
        '''
        item = Item.get(name)
        return item
        
    @staticmethod
    def item_update_price(name, new_price):
        '''
        Update the price of the specified item (administrative only)
        '''
        item = Item.get(name)
        item.update_price(new_price)
        
    @staticmethod
    def item_update_quantity(name, new_quantity):
        '''
        Update the quantity of the specified item (administrative only)
        '''
        item = Item.get(name)
        item.update_quantity(new_quantity)
        
    @staticmethod
    def item_list_auctions(name):
        '''
        List all auctions that have occurred for the specified item
        '''
        item = Item.get(name)
        return item.auctions

