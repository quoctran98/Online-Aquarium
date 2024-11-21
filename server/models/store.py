from server.helper import settings, save_to_s3
import uuid, datetime, pickle

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
        save_to_s3(pickle_obj, filename, save_dir)
        # Maybe not the best way, but let's also save a "latest" version!!
        save_to_s3(pickle_obj, "latest.pkl", save_dir)

    @property
    def summarize(self):
        # Don't include fully funded items!
        return([item.summarize for item in self.items.values() if not item.fully_funded])

class StoreItem():
    def __init__(self, store, item_type, item_dict):
        self.store = store
        self.label = str(uuid.uuid4())
        self.item_type = item_type

        # Unpack the item_type from the store_items dictionary
        # item_name, description, price, image_file
        for key, value in item_dict.items():
            setattr(self, key, value)

        # Keep track of how much money is has been raised for this item
        self.money_raised = 0.0
        self.contributors = [] # with dicts of username, amount, and timestamp

    def contribute(self, username, amount) -> bool:
        amount = round(amount, 2)
        self.money_raised = round(self.money_raised + amount, 2)
        self.contributors.append({
            "username": username,
            "amount": amount,
            "timestamp": datetime.datetime.now().timestamp()
        })
        return(self.money_raised >= self.price)
    
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
            "image_file": self.image_file,
            "money_raised": self.money_raised,
            # "contributors": self.contributors
        }
        return(return_dict)
    