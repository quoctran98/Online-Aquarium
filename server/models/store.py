from server.helper import settings, save_to_s3
import uuid, datetime, pickle
import numpy as np

class Store():
    def __init__(self):
        self.items = {} # {label: StoreItem}

    def add_item(self, item_type, item_dict):
        new_item = StoreItem(self, item_type, item_dict)
        self.items[new_item.label] = new_item
        return(new_item)

    def add_contribution(self, item_label, username, amount) -> bool:
        fully_funded  = self.items[item_label].contribute(username, amount)
        return(fully_funded)

    def save(self, save_dir=settings.S3_STORE_SAVE_DIR):
        filename = f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_aquarium.pkl"
        pickle_obj = pickle.dumps(self)
        # save_to_s3(pickle_obj, filename, save_dir) # DON'T SAVE A NON-LATEST VERSION -- WASTE OF SPACE 
        # # (this should eventualy be tied to the normal aquarium save in the simulation loop)
        # Maybe not the best way, but let's also save a "latest" version!!
        save_to_s3(pickle_obj, "latest.pkl", save_dir)

    @property
    def summarize(self):
        # Don't include out of stock items!
        return([item.summarize for item in self.items.values() if item.stock > 0])

class StoreItem():
    def __init__(self, store, item_type, item_dict):
        self.store = store
        self.label = str(uuid.uuid4())
        self.item_type = item_type

        # Unpack the item_type from the store_items dictionary
        # item_name, description, price, stock, image_file
        for key, value in item_dict.items():
            setattr(self, key, value)

        if (self.stock == -1):
            self.stock = np.inf

        # Keep track of how much money is has been raised for this item
        self.money_raised = 0.0
        self.contributors = [] # with dicts of username, amount, and timestamp
        self.times_bought = 0

    def contribute(self, username, amount) -> bool:
        amount = round(amount, 2) # Just in case but handled by in events/store.py (also prevents overfunding)
        self.money_raised = round(self.money_raised + amount, 2)
        self.contributors.append({
            "username": username,
            "amount": amount,
            "timestamp": datetime.datetime.now().timestamp()
        })
        
        if self.fully_funded:
            self.stock -= 1
            self.times_bought += 1
            # Ideally we eventually do something with the contributors too :)
            # If we still have stock, reset the money_raised and contributors
            if (self.stock > 0):
                self.money_raised = 0.0
                self.contributors = []
            return(True) # To tell Store() to add the item to the aquarium
    
    @property
    def fully_funded(self):
        return(self.money_raised >= self.price)

    @property
    def summarize(self):
        return_dict = {
            "label": self.label,
            "item_type": self.item_type,
            "item_name": self.item_name,
            "price": self.price,
            "stock": self.stock if self.stock != np.inf else "∞",
            "image_file": self.image_file,
            "money_raised": self.money_raised,
            # "contributors": self.contributors
        }
        return(return_dict)
    