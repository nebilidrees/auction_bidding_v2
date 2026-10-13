import time

class Auction:
    def __init__(self, auction_id, date, start_time, end_time, location, auction_name):
        self.auction_id = auction_id
        self.date = date
        self.start_time = start_time
        self.end_time = end_time
        self.location = location
        self.auction_name = auction_name

    def start_auction(self):
        print(f"Auction '{self.auction_name}' has started at {self.location}!")

    def end_auction(self):
        print(f"Auction '{self.auction_name}' has ended.")

    def find_highest_bid(self, bids_list):
        if not bids_list:
            return None

        highest_bid = bids_list[0]
        for bid in bids_list:
            if bid.amount > highest_bid.amount:
                highest_bid = bid

        return highest_bid

    def announce_winner(self, winning_bid):
        if winning_bid:
            print(
                f"Winner: {winning_bid.bidder.name} wins {winning_bid.auction_item.item_name} with a bid of ${winning_bid.amount}!"
            )
        else:
            print("No bids were placed. No winner announced.")


class Seller:
    def __init__(
        self, seller_id, name, company, contact, email_address, seller_status, Auction
    ):
        self.seller_id = seller_id
        self.name = name
        self.company = company
        self.contact = contact
        self.email_address = email_address
        self.seller_status = seller_status
        self.Auction = Auction

    def reserve_price(self, item, price):
        print(f"Reserve price set to ${price} for item {item.item_name}.")

    def change_reserved_price(self, item, new_price):
        print(f"Reserved price updated for item {item.item_name}.")

    def set_description_of_item(self, item, description):
        print(f"Description set for {item.item_name}: {description}")

    def set_starting_price(self, item, price):
        item.starting_price = price
        print(f"Starting price for {item.item_name} set to ${price}.")


class AuctionItem:
    def __init__(
        self,
        item_id,
        item_name,
        category,
        condition,
        starting_price,
        reserved_price,
        status,
        seller,
        auction,
    ):
        self.item_id = item_id
        self.item_name = item_name
        self.category = category
        self.condition = condition
        self.starting_price = starting_price
        self.__reserved_price = reserved_price
        self.status = status
        self.__seller = seller
        self.auction = auction
        # An item has no specification at first. It will later store an
        # ItemSpecification object when the item is loaded.
        self.specification: "ItemSpecification | None" = None

    def update_item_status(self, new_status):
        self.status = new_status
        print(f"Item '{self.item_name}' status updated to: {self.status}")

    def verify_reserve_price(self, bid_amount):
        return bid_amount >= self.__reserved_price


class ItemSpecification:
    def __init__(self, item_name, condition, base_price, status):
        self.item_name = item_name
        self.condition = condition
        self.base_price = base_price
        self.status = status

    def display_specification(self):
        print(f"Item: {self.item_name}")
        print(f"Condition: {self.condition}")
        print(f"Base Price: {self.base_price}")
        print(f"Status: {self.status}")


class Bidder:
    def __init__(self, name, contact, address, bidders_id, gender, birth_year, Auction):
        self.name = name
        self.contact = contact
        self.address = address
        self.__bidders_id = bidders_id
        self.gender = gender
        self.birth_year = birth_year
        self.Auction = Auction

    def __str__(self):
        return f"Name: {self.name}\nContact: {self.contact}\nAddress: {self.address}\nID: {self.__bidders_id}\nGender:{self.gender}\nBirth year:{self.birth_year}"

    @property
    def bidders_id(self):
        return self.__bidders_id

    def place_bid(self, item, amount):
        print(f"{self.name} placed a bid of ${amount} on {item.item_name}.")

    def withdraw_bid(self, item):
        print(f"{self.name} withdrew their bid on {item.item_name}.")

    def register(self):
        print(f"Bidder {self.name} is successfully registered.")


class Bid:
    def __init__(self, bid_amount, date, time, bidder, auction_item):
        self.amount = bid_amount
        self.date = date
        self.time = time
        self.bidder = bidder
        self.auction_item = auction_item

    def place_bid(self):
        if self.validate_amount():
            print(
                f"Valid bid of ${self.amount} placed by {self.bidder.name} on {self.auction_item.item_name}."
            )
        else:
            print("Bid amount is lower than the item's starting price!")

    def validate_amount(self):
        return self.amount >= self.auction_item.starting_price

    def update_status(self):
        print("Bid status updated successfully.")

    def show_highest_bidder(self, highest_bidder_name, highest_amount):
        print(f"Current Highest Bidder: {highest_bidder_name} with ${highest_amount}")

    def check_if_activity(self):
        return True


class SuccessfulWinner(Bidder):
    def __init__(self, winner_id, bidder, winning_item, final_bid):
        super().__init__(
            bidder.name,
            bidder.contact,
            bidder.address,
            bidder.bidders_id,
            bidder.gender,
            bidder.birth_year,
            bidder.Auction,
        )
        self.winner_id = winner_id
        self.bidder = bidder
        self.winning_item = winning_item
        self.final_bid = final_bid

    def display_winner_details(self):
        print(f"\n--- Winner Summary ---")
        print(f"Winner ID: {self.winner_id}")
        print(f"Name: {self.bidder.name}")
        print(f"Won Item: {self.winning_item.item_name}")
        print(f"Final Winning Bid: ${self.final_bid}")


class Payment:
    def __init__(
        self, payment_id, amount, bid, transaction_id, currency, payment_method
    ):
        self.payment_id = payment_id
        self.amount = amount
        self.bid = bid
        self.transaction_id = transaction_id
        self.currency = currency
        self.payment_method = payment_method

    def process_payment(self):
        print(
            f"Processing payment of {self.amount} {self.currency} via {self.payment_method} (Transaction ID: {self.transaction_id})..."
        )
        time.sleep(2)
        print("Payment Successful!")

    def refund(self):
        print(f"Refund of {self.amount} {self.currency} processed successfully.")


