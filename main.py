import json
import os
import time
from datetime import datetime

from bidding_classes import Auction, Seller, AuctionItem, Bidder, Bid, Payment, ItemSpecification, SuccessfulWinner

# The program saves information in these files.
payment_file = "bidder_payments.json"
bidder_file = "registered_bidders.json"
item_file = "bids_items.json"
seller_file = "registered_sellers.json"
bid_history_file = "bid_history.json"
auction_results_file = "auction_results.json"


def clear_screen():
    os.system("cls")


def wait_for_menu():
    while True:
        answer = input("\nEnter k to return to the menu: ").strip().lower()
        if answer == "k":
            return True
        print("Please enter k to return to the menu.")


def redirect_to_main_menu():
    print("Redirecting to main menu...")
    time.sleep(3)


def get_currency():
    while True:
        print("1. UGX\n2. KSH\n3. EURO")
        answer = input("Choose currency: ").strip()
        if answer == "1":
            return "UGX"
        elif answer == "2":
            return "KSH"
        elif answer == "3":
            return "EURO"
        else:
            print("Please type 1, 2, or 3.")


def get_payment_method():
    while True:
        print("1. Mobile Money\n2. Credit Card")
        answer = input("Choose payment method: ").strip()
        if answer == "1":
            return "Mobile Money"
        elif answer == "2":
            return "Credit Card"
        else:
            print("Please type 1 or 2.")


def get_birth_date():
    while True:
        date = input("Birth date (DD-MM-YYYY), or k to cancel: ").strip()
        if date.lower() == "k":
            return None
        try:
            datetime.strptime(date, "%d-%m-%Y")
            return date
        except ValueError:
            print("Use DD-MM-YYYY, for example 25-08-2000.")


def save_json(file_name, data):
    with open(file_name, "w") as file:
        json.dump(data, file, indent=4)
        


def read_json(file_name, empty_value):
    try:
        with open(file_name, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return empty_value


def save_bidders(bidders):
    data = []
    for bidder in bidders:
        data.append({"name": bidder.name, "contact": bidder.contact, "address": bidder.address,
                     "bidders_id": bidder.bidders_id, "gender": bidder.gender, "birth_year": bidder.birth_year})
    save_json(bidder_file, data)


def load_bidders_from_file(auction):
    bidders = []
    saved_bidders = read_json(bidder_file, [])
    for saved_bidder in saved_bidders:
        name = saved_bidder["name"]
        contact = saved_bidder["contact"]
        address = saved_bidder["address"]
        bidder_id = saved_bidder["bidders_id"]
        gender = saved_bidder.get("gender", "Not provided")
        birth_year = saved_bidder.get("birth_year", "Not provided")
        bidder = Bidder(name, contact, address, bidder_id, gender, birth_year, auction)
        bidders.append(bidder)
    return bidders


def save_sellers(sellers):
    data = []
    for seller in sellers:
        data.append({
            "seller_id": seller.seller_id,
            "name": seller.name,
            "company": seller.company,
            "contact": seller.contact,
            "email_address": seller.email_address,
            "seller_status": seller.seller_status,
        })
    save_json(seller_file, data)


def load_sellers_from_file(auction):
    sellers = []
    saved_sellers = read_json(seller_file, [])
    for saved_seller in saved_sellers:
        seller = Seller(
            saved_seller.get("seller_id", ""),
            saved_seller.get("name", ""),
            saved_seller.get("company", ""),
            saved_seller.get("contact", ""),
            saved_seller.get("email_address", ""),
            saved_seller.get("seller_status", "Registered"),
            auction,
        )
        sellers.append(seller)
    return sellers


def display_sellers_and_items(sellers):
    if not sellers:
        print("No registered sellers yet.")
        return

    saved_items = read_json(item_file, {})
    for seller in sellers:
        print(f"\nSeller ID: {seller.seller_id}")
        print(f"Name: {seller.name}")
        print(f"Company: {seller.company}")
        print(f"Contact: {seller.contact}")
        print(f"Email: {seller.email_address}")
        print(f"Status: {seller.seller_status}")
        print("Items:")

        seller_items = []
        for item_details in saved_items.values():
            if item_details.get("seller_id") == seller.seller_id:
                seller_items.append(item_details.get("name", "Unnamed item"))

        if seller_items:
            for item_name in seller_items:
                print(f"  - {item_name}")
        else:
            print("  No items registered.")


def generate_item_id(saved_items):
    highest_number = 0
    for item_id in saved_items:
        if item_id.startswith("ITM-") and item_id[4:].isdigit():
            number = int(item_id[4:])
            if number > highest_number:
                highest_number = number
    return f"ITM-{highest_number + 1:04}"


def load_items_from_file(seller, auction):
    items = []
    saved_items = read_json(item_file, {})
    for item_id, details in saved_items.items():
        price = details.get("base price", 0)
        item_name = details.get("name", item_id).title()
        item = AuctionItem(item_id, item_name, details.get("category", "General"), details.get("condition", "New"),
                           price, price + 50000, details.get("status", "AVAILABLE"), seller, auction)
        item.specification = ItemSpecification(item.item_name, item.condition, price, item.status)
        items.append(item)
    return items


def find_bidder(bidders, bidder_id):
    for bidder in bidders:
        if bidder.bidders_id.lower() == bidder_id.lower():
            return bidder
    return None


def find_item(items, word):
    for item in items:
        if item.item_id.lower() == word.lower():
            return item
    matching_items = []
    for item in items:
        if item.item_name.lower() == word.lower():
            matching_items.append(item)
    if len(matching_items) == 1:
        return matching_items[0]
    if len(matching_items) > 1:
        print("More than one item has that name. Please use the Item ID.")
    return None


def highest_bid_for_item(bids, item):
    highest = None
    for bid in bids:
        if bid.auction_item == item:
            if highest is None or bid.amount > highest.amount:
                highest = bid
    return highest


def display_item(item, bids):
    """Show one item once in the browse-items list."""
    print(f"{item.item_id} - {item.item_name.upper()}")
    print(f"       Condition: {item.condition}")
    print(f"       Starting price: {item.starting_price:,.0f}")
    print(f"       Status: {item.status}")
    print()


def display_bidders_table(bidders):
    """Display registered bidders in a readable table."""
    headers = ["Bidder ID", "Name", "Telephone", "Gender", "Birth year"]
    rows = []

    for bidder in bidders:
        rows.append([
            bidder.bidders_id,
            bidder.name,
            bidder.contact,
            bidder.gender,
            bidder.birth_year,
        ])

    widths = []
    for position in range(len(headers)):
        width = len(headers[position])
        for row in rows:
            if len(str(row[position])) > width:
                width = len(str(row[position]))
        widths.append(width)

    print(" | ".join(headers[position].ljust(widths[position]) for position in range(len(headers))))
    print("-+-".join("-" * width for width in widths))
    for row in rows:
        print(" | ".join(str(row[position]).ljust(widths[position]) for position in range(len(row))))


def display_payment_history(history, title):
    """Display every bid record separately so terminal output stays readable."""
    if not history:
        print("No bidding history yet.")
        return
    print(f"\n{title}")
    print("=" * 45)
    for number, record in enumerate(history, start=1):
        print(f"Bid record {number}")
        print(f"  Auction ID:     {record.get('auction_id', 'Not recorded')}")
        print(f"  Bidder ID:      {record.get('bidder_id', 'Unknown')}")
        print(f"  Bidder name:    {record.get('bidder_name', 'Unknown')}")
        print(f"  Item:           {record.get('item_id', '')} - {record.get('item_name', 'Unknown')}")
        print(f"  Bid amount:     {record.get('amount', 0):,.0f}")
        print(f"  Date placed:    {record.get('date', 'Not recorded')}")
        print(f"  Time placed:    {record.get('time', 'Not recorded')}")
        print(f"  Bid status:     {record.get('bid_status', 'Active')}")
        print(f"  Payment status: {record.get('payment_status', 'Not applicable')}")
        if number != len(history):
            print("-" * 45)


def create_bid(amount, bidder, item):
    placed_at = datetime.now()
    return Bid(
        amount,
        placed_at.strftime("%d-%m-%Y"),
        placed_at.strftime("%I:%M:%S %p"),
        bidder,
        item,
    )


def record_bid_history(bid, auction):
    """Append one accepted bid; no earlier history is overwritten."""
    history = read_json(bid_history_file, [])
    history.append({
        "auction_id": auction.auction_id,
        "bidder_id": bid.bidder.bidders_id,
        "bidder_name": bid.bidder.name,
        "item_id": bid.auction_item.item_id,
        "item_name": bid.auction_item.item_name,
        "amount": bid.amount,
        "date": bid.date,
        "time": bid.time,
        "bid_status": "Active",
        "payment_status": "Not applicable",
    })
    save_json(bid_history_file, history)


def mark_bid_withdrawn(bid):
    history = read_json(bid_history_file, [])
    for record in reversed(history):
        if (record.get("bidder_id") == bid.bidder.bidders_id and
                record.get("item_id") == bid.auction_item.item_id and
                record.get("date") == bid.date and record.get("time") == bid.time and
                record.get("bid_status") == "Active"):
            record["bid_status"] = "Withdrawn"
            record["payment_status"] = "Not applicable"
            break
    save_json(bid_history_file, history)


def load_bid_history():
    """Show new bid records and older payment-file records without deleting either."""
    history = read_json(bid_history_file, [])
    legacy_records = read_json(payment_file, {})
    for bidder_id, bidder_record in legacy_records.items():
        for item in bidder_record.get("items", []):
            history.append({
                "auction_id": "AUC-2026-ART-",
                "bidder_id": bidder_id,
                "bidder_name": bidder_record.get("name", "Unknown"),
                "item_id": item.get("item_id", "Unknown"),
                "item_name": item.get("item", "Unknown"),
                "amount": item.get("bid", 0),
                "date": item.get("date_placed", "Not recorded"),
                "time": item.get("time_placed", "Not recorded"),
                "bid_status": "Earlier saved record",
                "payment_status": item.get("payment_status", "Not recorded"),
            })
    return history


def update_payment_records(bids, payment_statuses):
    """Keep the original payment file intact while updating its known payment entries."""
    records = read_json(payment_file, {})
    save_json(payment_file, records)
    return records


def show_menu():
    print("\n================ ONLINE AUCTION ================")
    print("1. Browse auction items")
    print("2. Search for an item")
    print("3. Register bidder")
    print("4. View registered bidders")
    print("5. Start auction")
    print("6. Place or withdraw a bid")
    print("7. View current highest bids")
    print("8. View bidding history")
    print("9. Close auction")
    print("10. View auction results")
    print("11. Search bidder")
    print("12. Complete pending payment")
    print("13. Exit")
    print("14. Register New Seller")
    print("15. View sellers and their items")


def register_bidder(bidders, auction):
    name = input("Enter Name , or k to cancel: ").strip()
    if name.lower() == "k":
        redirect_to_main_menu()
        return True
    contact = input("Enter Contact, or k to cancel: ").strip()
    if contact.lower() == "k":
        redirect_to_main_menu()
        return True
    address = input("Enter Address, or k to cancel: ").strip()
    if address.lower() == "k":
        redirect_to_main_menu()
        return True
    gender = input("Enter Gender, or k to cancel: ").strip()
    if gender.lower() == "k":
        redirect_to_main_menu()
        return True
    birth_date = get_birth_date()
    if birth_date is None:
        redirect_to_main_menu()
        return True
    bidder = Bidder(name, contact, address, None, gender, birth_date, auction)
    bidder_id = bidder.generate_bidder_id(bidders)
    bidders.append(bidder)
    save_bidders(bidders)
    print(f"Bidder successfully registered. Assigned Bidder ID :{bidder_id}.")
    return False


def register_seller_items(seller, items, auction):
    registered_item_ids = []
    while True:
        item_name = input("Enter item name: ").strip()
        condition = input("Enter item condition (New/Used): ").strip().title()
        category = input("Enter item category: ").strip().title()
        try:
            base_price = float(input("Enter base price: ").strip())
        except ValueError:
            print("Base price must be a number.")
            continue

        if not item_name or not category or condition not in ["New", "Used"] or base_price <= 0:
            print("Enter an item name, category, New or Used condition, and a positive price.")
            continue

        saved_items = read_json(item_file, {})
        item_id = generate_item_id(saved_items)
        item = AuctionItem(item_id, item_name.title(), category, condition, base_price,
                           base_price, "AVAILABLE", seller, auction)
        item.specification = ItemSpecification(item.item_name, item.condition, base_price, item.status)
        items.append(item)
        saved_items[item_id] = {
            "name": item.item_name,
            "condition": item.condition,
            "category": item.category,
            "base price": item.starting_price,
            "status": item.status,
            "seller_id": seller.seller_id,
            "seller_name": seller.name,
            "event_name": auction.auction_name,
            "event_location": auction.location,
        }
        save_json(item_file, saved_items)
        registered_item_ids.append(item_id)

        print("\nITEM REGISTERED SUCCESSFULLY")
        print(f"Item ID: {item_id}")
        print(f"Item Name: {item.item_name}")
        print(f"Seller: {seller.name}")
        print(f"Condition: {item.condition}")
        print(f"Base Price: {item.starting_price:,.0f}")

        while True:
            answer = input("Do you want to register another item? (yes/no): ").strip().lower()
            if answer == "yes":
                break
            if answer == "no":
                print(f"\nSeller ID: {seller.seller_id}")
                print(f"Items registered this session: {len(registered_item_ids)}")
                print(f"Item IDs: {', '.join(registered_item_ids)}")
                print("Registration completed successfully. Returning to the main menu in 3 seconds...")
                time.sleep(3)
                return
            print("Please enter yes or no.")


def register_new_seller(sellers, items, auction):
    seller_name = input("Enter seller name, or k to cancel: ").strip()
    if seller_name.lower() == "k":
        return True
    company = input("Enter company name: ").strip()
    contact = input("Enter contact: ").strip()
    email_address = input("Enter email address: ").strip()
    if not seller_name or not company or not contact or not email_address:
        print("All seller details are required.")
        return False

    for saved_seller in sellers:
        if saved_seller.email_address.lower() == email_address.lower():
            print("A seller with that email address is already registered.")
            return False

    seller = Seller("", seller_name, company, contact, email_address, "Registered", auction)
    seller_id = seller.generate_seller_id(sellers)
    sellers.append(seller)
    save_sellers(sellers)
    print("\nSELLER REGISTERED SUCCESSFULLY")
    print(f"Seller Name: {seller.name}")
    print(f"Seller ID: {seller_id}")
    register_seller_items(seller, items, auction)
    return True


def place_or_withdraw_bid(bidders, items, bids, auction, payment_statuses):
    while True:
        bidder_id = input("Enter Bidder ID, or k to return to the main menu: ").strip()
        if bidder_id.lower() == "k":
            return
        bidder = find_bidder(bidders, bidder_id)
        if bidder is None:
            print("That bidder ID is not registered.")
            continue

        while True:
            print("Available items:")
            for item in items:
                if item.status == "AVAILABLE":
                    print(f"{item.item_id}: {item.item_name} ({item.starting_price:,})")
            chosen = input("Enter Item ID/name, or w to withdraw a bid: ").strip()

            if chosen.lower() == "w":
                chosen = input("Enter item ID/name to withdraw: ").strip()
                for bid in reversed(bids):
                    is_bidder_bid = bid.bidder == bidder
                    is_correct_item = bid.auction_item.item_id.lower() == chosen.lower()
                    is_correct_name = bid.auction_item.item_name.lower() == chosen.lower()
                    if is_bidder_bid and (is_correct_item or is_correct_name):
                        withdrawn_item = bid.auction_item
                        bidder.withdraw_bid(bid.auction_item)
                        bids.remove(bid)
                        mark_bid_withdrawn(bid)
                        update_payment_records(bids, payment_statuses)
                        print("Your latest bid on that item was withdrawn.")

                        another_bid = input(
                            f"Do you want to place another bid on {withdrawn_item.item_name}? (yes/no): "
                        ).strip().lower()
                        if another_bid == "yes":
                            try:
                                amount = float(input(f"Bid amount (at least {withdrawn_item.starting_price:,}): ").strip())
                            except ValueError:
                                print("Please enter a number.")
                            else:
                                new_bid = create_bid(amount, bidder, withdrawn_item)
                                if not new_bid.validate_amount():
                                    print(f"Your bid must be at least {withdrawn_item.starting_price:,}.")
                                else:
                                    bids.append(new_bid)
                                    new_bid.place_bid()
                                    record_bid_history(new_bid, auction)
                                    update_payment_records(bids, payment_statuses)
                        return
                else:
                    print("You do not have a bid on that item.")
            else:
                item = find_item(items, chosen)
                if item is None or item.status != "AVAILABLE":
                    print("That item is not available.")
                else:
                    try:
                        amount = float(input(f"Bid amount (at least {item.starting_price:,}): ").strip())
                    except ValueError:
                        print("Please enter a number.")
                    else:
                        bid = create_bid(amount, bidder, item)
                        while not bid.validate_amount():
                            print(f"Your bid must be at least {item.starting_price:,}.")
                            another_amount = input(
                                "Do you wish to place another bid? (yes/no): "
                            ).strip().lower()
                            if another_amount != "yes":
                                break
                            try:
                                amount = float(input(f"Enter another bid for {item.item_name} (at least {item.starting_price:,}): ").strip())
                            except ValueError:
                                print("Please enter a number.")
                                continue
                            bid = create_bid(amount, bidder, item)
                        if not bid.validate_amount():
                            break
                        bids.append(bid)
                        bid.place_bid()
                        record_bid_history(bid, auction)
                        update_payment_records(bids, payment_statuses)

            continue_bidding = input(
                "Do you want to place a bid on another item? (yes/no): "
            ).strip().lower()
            if continue_bidding != "yes":
                break

        another_bidder = input(
            "Are there other bidders who want to place bids? (yes/no): "
        ).strip().lower()
        if another_bidder != "yes":
            return


def auction_has_saved_results(auction):
    results = read_json(auction_results_file, [])
    return any(result.get("auction_id") == auction.auction_id for result in results)


def next_auction_id():
    results = read_json(auction_results_file, [])
    highest_number = 100
    for result in results:
        auction_id = result.get("auction_id", "")
        if auction_id.startswith("A") and auction_id[1:].isdigit():
            auction_number = int(auction_id[1:])
            if auction_number > highest_number:
                highest_number = auction_number
    return f"A{highest_number + 1:03}"


def create_auction(auction_id):
    return Auction(
        auction_id,
        "2026-09-22",
        "10:00 AM",
        "04:00 PM",
        "Kampala",
        "Tech & Gadgets Expo",
    )


def update_history_after_closure(auction, winning_bids, payment_statuses):
    history = read_json(bid_history_file, [])
    for record in history:
        if record.get("auction_id") != auction.auction_id or record.get("bid_status") == "Withdrawn":
            continue
        winner = winning_bids.get(record.get("item_id"))
        if winner and (record.get("bidder_id") == winner.bidder.bidders_id and
                       record.get("date") == winner.date and record.get("time") == winner.time):
            record["bid_status"] = "Winning bid"
            record["payment_status"] = payment_statuses[winner.auction_item.item_id]
        else:
            record["bid_status"] = "Outbid"
            record["payment_status"] = "Not applicable"
    save_json(bid_history_file, history)


def close_auction(auction, items, bids, payment_statuses):
    if auction_has_saved_results(auction):
        print("This auction already has saved results and cannot be closed again.")
        return

    result = {
        "auction_id": auction.auction_id,
        "auction_name": auction.auction_name,
        "date": auction.date,
        "location": auction.location,
        "items": [],
    }
    winning_bids = {}
    for item in items:
        winner = highest_bid_for_item(bids, item)
        item_result = {
            "item_id": item.item_id,
            "item_name": item.item_name,
            "starting_price": item.starting_price,
            "valid_bid_count": sum(1 for bid in bids if bid.auction_item == item),
        }
        if winner is None:
            item_result.update({"sale_status": "Unsold", "payment_status": "Not applicable"})
        else:
            SuccessfulWinner("W01", winner.bidder, item, winner.amount).display_winner_details()
            while True:
                payment_choice = input(f"Pay for {item.item_name} now or skip it? (pay/skip): ").strip().lower()
                if payment_choice == "pay":
                    currency = get_currency()
                    payment_method = get_payment_method()
                    Payment("PAY01", winner.amount, winner, "TXN12345", currency, payment_method).process_payment()
                    payment_statuses[item.item_id] = "Completed"
                    break
                if payment_choice == "skip":
                    payment_statuses[item.item_id] = "Pending"
                    print(f"Payment for {item.item_name} is pending.")
                    break
                print("Please enter pay or skip.")
            winning_bids[item.item_id] = winner
            item_result.update({
                "sale_status": "Sold",
                "winner_id": winner.bidder.bidders_id,
                "winner_name": winner.bidder.name,
                "final_bid": winner.amount,
                "payment_status": payment_statuses[item.item_id],
            })
        result["items"].append(item_result)

    results = read_json(auction_results_file, [])
    results.append(result)
    save_json(auction_results_file, results)
    update_history_after_closure(auction, winning_bids, payment_statuses)
    update_payment_records(bids, payment_statuses)
    auction.end_auction()


def display_auction_results():
    results = read_json(auction_results_file, [])
    if not results:
        print("No closed auction results have been saved yet.")
        return
    for result in results:
        print(f"\nAuction: {result['auction_id']} - {result['auction_name']}")
        print(f"Date: {result['date']} | Location: {result['location']}")
        print("=" * 45)
        for item in result.get("items", []):
            print(f"{item['item_id']} - {item['item_name']}")
            print(f"  Starting price: {item['starting_price']:,.0f}")
            print(f"  Valid bids: {item['valid_bid_count']}")
            print(f"  Sale status: {item['sale_status']}")
            if item['sale_status'] == "Sold":
                print(f"  Winner: {item['winner_name']} ({item['winner_id']})")
                print(f"  Final bid: {item['final_bid']:,.0f}")
            print(f"  Payment status: {item['payment_status']}\n")


def show_bidder_profile(bidders, bids, records, payment_statuses):
    bidder_id = input("Enter Bidder ID, or k to go back: ").strip()
    bidder = find_bidder(bidders, bidder_id)
    if bidder is None:
        print("Bidder not found.")
        return
    print("\n" + str(bidder))
    history = load_bid_history()
    bidder_history = [record for record in history if record.get("bidder_id") == bidder.bidders_id]
    if bidder_history:
        display_payment_history(bidder_history, "BIDDER BIDDING HISTORY")
    else:
        print("This bidder has not placed a bid in the new history yet.")


def complete_pending_payment(bidders, records, payment_statuses):
    bidder_id = input("Enter Bidder ID, or k to return to the main menu: ").strip()
    if bidder_id.lower() == "k":
        return
    bidder = find_bidder(bidders, bidder_id)
    if bidder is None:
        print("Bidder not found.")
        return
    results = read_json(auction_results_file, [])
    pending_items = []
    for result in results:
        for item in result.get("items", []):
            if item.get("winner_id") == bidder.bidders_id and item.get("payment_status") == "Pending":
                pending_items.append((result, item))
    if not pending_items:
        print("This bidder has no pending payments.")
        return

    print(f"Pending payments for {bidder.name}:")
    for _, item in pending_items:
        print(f"  {item['item_id']} - {item['item_name']}: {item['final_bid']:,.0f}")
    selected_item_id = input("Enter the Item ID to pay for, or k to cancel: ").strip().upper()
    if selected_item_id == "K":
        return
    selected = None
    for result, item in pending_items:
        if item["item_id"] == selected_item_id:
            selected = (result, item)
            break
    if selected is None:
        print("That item does not have a pending payment for this bidder.")
        return

    _, item = selected
    currency = get_currency()
    payment_method = get_payment_method()
    clear_screen()
    Payment("PAY01", item["final_bid"], None, "TXN12345", currency, payment_method).process_payment()
    item["payment_status"] = "Completed"
    payment_statuses[item["item_id"]] = "Completed"
    save_json(auction_results_file, results)

    history = read_json(bid_history_file, [])
    for record in history:
        if (record.get("auction_id") == selected[0]["auction_id"] and
                record.get("item_id") == item["item_id"] and
                record.get("bidder_id") == bidder.bidders_id and
                record.get("bid_status") == "Winning bid"):
            record["payment_status"] = "Completed"
    save_json(bid_history_file, history)
    print("Payment completed for the selected item.")


def run_auction_program():
    auction = create_auction(next_auction_id())
    seller = Seller("S01", "Mark", "GadgetHub", "0771234567", "mark@gadgethub.com", "Verified", auction)
    items = load_items_from_file(seller, auction)
    sellers = load_sellers_from_file(auction)
    bidders = load_bidders_from_file(auction)
    bids = []
    records = read_json(payment_file, {})
    payment_statuses = {}
    auction_running = False
    while True:
        clear_screen()
        show_menu()
        choice = input("Choose an option: ").strip()
        clear_screen()
        if choice == "1":
            for item in items:
                display_item(item, bids)
        elif choice == "2":
            while True:
                word = input("Enter Item name to search: ").strip().lower()
                if word == "k":
                    redirect_to_main_menu()
                    break
                found_item = False
                for item in items:
                    if word in item.item_name.lower():
                        display_item(item, bids)
                        found_item = True
                if not found_item:
                    print("Item not found.")

                while True:
                    search_again = input("\nSearch for another item? (yes/k): ").strip().lower()
                    if search_again == "yes":
                        break
                    if search_again == "k":
                        redirect_to_main_menu()
                        break
                    print("Please enter yes or k.")
                if search_again == "k":
                    break
            continue
        elif choice == "3":
            if register_bidder(bidders, auction):
                continue
        elif choice == "4":
            if not bidders:
                print("No registered bidders yet.")
            else:
                display_bidders_table(bidders)
        elif choice == "5":
            if auction_has_saved_results(auction):
                auction = create_auction(next_auction_id())
                seller.Auction = auction
                for registered_seller in sellers:
                    registered_seller.Auction = auction
                for bidder in bidders:
                    bidder.Auction = auction
                for item in items:
                    item.auction = auction
                bids.clear()
                payment_statuses.clear()
            auction_running = True
            auction.start_auction()
        elif choice == "6":
            if auction_running:
                place_or_withdraw_bid(bidders, items, bids, auction, payment_statuses)
                # The bidding session already provides its own menu-return choices.
                continue
            else: print("Start the auction first using option 5.")
        elif choice == "7":
            if not bids:
                print("No bids placed yet.")
            else:
                for item in items:
                    winner = highest_bid_for_item(bids, item)
                    if winner:
                        print(f"{item.item_name}: {winner.amount:,} by {winner.bidder.name}")
        elif choice == "8":
            display_payment_history(load_bid_history(), "BIDDING HISTORY")
        elif choice == "9":
            if auction_running:
                close_auction(auction, items, bids, payment_statuses)
                auction_running = False
                records = read_json(payment_file, {})
            else: print("The auction is not running.")
        elif choice == "10":
            display_auction_results()
        elif choice == "11":
            show_bidder_profile(bidders, bids, records, payment_statuses)
        elif choice == "12":
            complete_pending_payment(bidders, records, payment_statuses)
        elif choice == "13":
            print("Thank you for using the Online Auction System.")
            time.sleep(3)
            clear_screen()
            print("Your session has ended securely. We look forward to serving you again.")
            break
        elif choice == "14":
            if register_new_seller(sellers, items, auction):
                continue
        elif choice == "15":
            display_sellers_and_items(sellers)
        else:
            print("Choose a number from 1 to 15.")
        wait_for_menu()



if __name__ == "__main__":
    run_auction_program()
