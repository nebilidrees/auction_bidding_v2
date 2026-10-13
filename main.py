import json
import os
import time
from datetime import datetime

from bidding_classes import Auction, Seller, AuctionItem, Bidder, Bid, Payment, ItemSpecification, SuccessfulWinner

# The program saves information in these files.
payment_file = "bidder_payments.json"
bidder_file = "registered_bidders.json"
item_file = "bids_items.json"


def clear_screen():
    os.system("cls")


def wait_for_menu():
    while True:
        answer = input("\nEnter k to return to the menu: ").strip().lower()
        if answer == "k":
            return True
        print("Please enter k to return to the menu.")


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


def load_items_from_file(seller, auction):
    items = []
    number = 1
    saved_items = read_json(item_file, {})
    for name, details in saved_items.items():
        price = details.get("base price", 0)
        item = AuctionItem(f"ITM0{number}", name.title(), "General", details.get("condition", "New"),
                           price, price + 50000, details.get("status", "AVAILABLE"), seller, auction)
        item.specification = ItemSpecification(item.item_name, item.condition, price, item.status)
        items.append(item)
        number += 1
    return items


def find_bidder(bidders, bidder_id):
    for bidder in bidders:
        if bidder.bidders_id.lower() == bidder_id.lower():
            return bidder
    return None


def generate_bidder_id(bidders):
    number = 1
    while find_bidder(bidders, f"B{number:03}") is not None:
        number += 1
    return f"B{number:03}"


def find_item(items, word):
    for item in items:
        if item.item_id.lower() == word.lower():
            return item
        if item.item_name.lower() == word.lower():
            return item
    return None


def highest_bid_for_item(bids, item):
    highest = None
    for bid in bids:
        if bid.auction_item == item:
            if highest is None or bid.amount > highest.amount:
                highest = bid
    return highest


def create_bid(amount, bidder, item):
    placed_at = datetime.now()
    return Bid(
        amount,
        placed_at.strftime("%d-%m-%Y"),
        placed_at.strftime("%I:%M:%S %p"),
        bidder,
        item,
    )


def update_payment_records(bids, payment_statuses):
    # Keep entries saved in earlier program runs so a new bid does not erase them.
    records = read_json(payment_file, {})
    for bid in bids:
        bidder_id = bid.bidder.bidders_id
        if bidder_id not in records:
            records[bidder_id] = {"name": bid.bidder.name, "contact": bid.bidder.contact,
                                  "gender": bid.bidder.gender, "address": bid.bidder.address, "items": []}
        highest_bid = highest_bid_for_item(bids, bid.auction_item)
        if bid == highest_bid:
            status = payment_statuses.get(bid.auction_item.item_id, "Pending")
        else:
            status = "Not a winning bid"
        bid_details = {
            "item_id": bid.auction_item.item_id,
            "item": bid.auction_item.item_name,
            "bid": bid.amount,
            "date_placed": bid.date,
            "time_placed": bid.time,
            "payment_status": status,
        }
        saved_item = None
        for item in records[bidder_id]["items"]:
            if item["item_id"] == bid.auction_item.item_id:
                saved_item = item
                break
        if saved_item is None:
            records[bidder_id]["items"].append(bid_details)
        else:
            saved_item.update(bid_details)
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


def register_bidder(bidders, auction):
    name = input("Enter Name , or k to cancel: ").strip()
    if name.lower() == "k":
        return
    contact = input("Enter Contact, or k to cancel: ").strip()
    if contact.lower() == "k":
        return
    address = input("Enter Address, or k to cancel: ").strip()
    if address.lower() == "k":
        return
    gender = input("Enter Gender, or k to cancel: ").strip()
    if gender.lower() == "k":
        return
    birth_date = get_birth_date()
    if birth_date is None:
        return
    bidder_id = generate_bidder_id(bidders)
    bidder = Bidder(name, contact, address, bidder_id, gender, birth_date, auction)
    bidders.append(bidder)
    save_bidders(bidders)
    print(f"Bidder registered. Their ID is {bidder_id}.")


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
            chosen = input("Item ID/name, or w to withdraw a bid: ").strip()

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


def close_auction(auction, bids, payment_statuses):
    if not bids:
        print("The auction closed with no bids.")
        return
    seen_items = []
    for bid in bids:
        item = bid.auction_item
        if item in seen_items:
            continue
        seen_items.append(item)
        winner = highest_bid_for_item(bids, item)
        if winner is None:
            continue
        SuccessfulWinner("W01", winner.bidder, item, winner.amount).display_winner_details()
        while True:
            payment_choice = input(
                f"Pay for {item.item_name} now or skip it? (pay/skip): "
            ).strip().lower()
            if payment_choice == "pay":
                currency = get_currency()
                payment_method = get_payment_method()
                clear_screen()
                Payment(
                    "PAY01", winner.amount, winner, "TXN12345", currency, payment_method
                ).process_payment()
                payment_statuses[item.item_id] = "Completed"
                break
            if payment_choice == "skip":
                payment_statuses[item.item_id] = "Not Completed"
                print(f"Payment for {item.item_name} was skipped.")
                break
            print("Please enter pay or skip.")
    update_payment_records(bids, payment_statuses)
    auction.end_auction()


def show_bidder_profile(bidders, bids, records, payment_statuses):
    bidder_id = input("Bidder ID, or k to go back: ").strip()
    bidder = find_bidder(bidders, bidder_id)
    if bidder is None:
        print("Bidder not found.")
        return
    print("\n" + str(bidder))
    bidder_bids = []
    for bid in bids:
        if bid.bidder == bidder:
            bidder_bids.append(bid)
    if bidder_bids:
        for bid in bidder_bids:
            winner = highest_bid_for_item(bids, bid.auction_item)
            if bid == winner:
                state = "Won (highest bid)"
                payment = payment_statuses.get(bid.auction_item.item_id, "Pending")
            else:
                state = "Lost / outbid"
                payment = "N/A"
            print(f"{bid.auction_item.item_name}: {bid.amount:,} | {state} | Payment: {payment}")
    elif bidder.bidders_id in records:
        for item in records[bidder.bidders_id]["items"]:
            print(f"{item['item']}: {item['bid']:,} | Payment: {item['payment_status']}")
    else:
        print("This bidder has not placed a bid yet.")


def complete_pending_payment(bidders, records, payment_statuses):
    bidder_id = input("Bidder ID, or k to return to the main menu: ").strip()
    if bidder_id.lower() == "k":
        return
    bidder = find_bidder(bidders, bidder_id)
    if bidder is None or bidder.bidders_id not in records:
        print("No saved pending payment was found for that bidder.")
        return
    pending_items = []
    saved_items = records[bidder.bidders_id]["items"]
    for item in saved_items:
        if item["payment_status"] == "Pending" or item["payment_status"] == "Not Completed":
            pending_items.append(item)
    if not pending_items:
        print("This bidder has no pending payments.")
        return

    print(f"Pending payments for {bidder.name}:")
    for item in pending_items:
        date_placed = item.get("date_placed", "Date not recorded")
        time_placed = item.get("time_placed", "Time not recorded")
        print(
            f"{item['item_id']} | {item['item']} | {item['bid']:,} | "
            f"Placed: {date_placed} {time_placed} | {item['payment_status']}"
        )

    total_amount = 0
    for item in pending_items:
        total_amount = total_amount + item["bid"]
    print(f"\nTotal pending payment: {total_amount:,.2f}")
    currency = get_currency()
    payment_method = get_payment_method()
    clear_screen()
    Payment("PAY01", total_amount, None, "TXN12345", currency, payment_method).process_payment()

    for item in pending_items:
        item["payment_status"] = "Completed"
        payment_statuses[item["item_id"]] = "Completed"

    save_json(payment_file, records)
    print("Payment completed.")


def run_auction_program():
    auction = Auction("A101", "2026-09-22", "10:00 AM", "04:00 PM", "Kampala", "Tech & Gadgets Expo")
    seller = Seller("S01", "Mark", "GadgetHub", "0771234567", "mark@gadgethub.com", "Verified", auction)
    items = load_items_from_file(seller, auction)
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
                print(f"{item.item_id} - {item.item_name}")
                item.specification.display_specification()
        elif choice == "2":
            word = input("Item name to search: ").strip().lower()
            found_item = False
            for item in items:
                if word in item.item_name.lower():
                    print(f"{item.item_id} | {item.item_name} | {item.starting_price:,} | {item.status}")
                    found_item = True
            if found_item is False:
                print("Item not found.")
        elif choice == "3":
            register_bidder(bidders, auction)
        elif choice == "4":
            if not bidders:
                print("No registered bidders yet.")
            else:
                for bidder in bidders:
                    print(f"{bidder.bidders_id} | {bidder.name} | {bidder.contact}")
        elif choice == "5":
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
            if not bids:
                print("No bidding history yet.")
            else:
                for bid in bids:
                    print(f"{bid.bidder.name} bid {bid.amount:,} on {bid.auction_item.item_name}")
        elif choice == "9":
            if auction_running:
                close_auction(auction, bids, payment_statuses)
                auction_running = False
                records = read_json(payment_file, {})
            else: print("The auction is not running.")
        elif choice == "10":
            if not bids:
                print("No bids were placed during the auction.")
            else:
                for bid in bids:
                    print(f"{bid.bidder.name} | {bid.auction_item.item_name} | {bid.amount:,}")
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
        else:
            print("Choose a number from 1 to 13.")
        wait_for_menu()


if __name__ == "__main__":
    run_auction_program()
