import json
import os
import shutil
from datetime import datetime, timedelta

DATA_FILE = 'library_data.json'
BACKUP_FILE = 'library_data_backup.json'
FINE_PER_DAY = 5  
BORROW_DAYS = 14  

class Library:
    def __init__(self):
        self.data = {"books": {}, "users": {}, "transactions": []}
        self.load_data()

    def load_data(self):
        """Load library data from the JSON file."""
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                self.data = json.load(f)

    def save_data(self):
        """Save the current state to the JSON file."""
        with open(DATA_FILE, 'w') as f:
            json.dump(self.data, f, indent=4)

    def add_book(self, book_id, title, author, total_copies):
        """Add a new book or update existing copies."""
        if book_id in self.data["books"]:
            self.data["books"][book_id]["total"] += total_copies
            self.data["books"][book_id]["available"] += total_copies
        else:
            self.data["books"][book_id] = {
                "title": title,
                "author": author,
                "total": total_copies,
                "available": total_copies
            }
        self.save_data()
        print(f"Added book: '{title}' by {author}")

    def add_user(self, user_id, name):
        """Register a new user."""
        self.data["users"][user_id] = {"name": name}
        self.save_data()
        print(f"User '{name}' registered successfully.")

    def issue_book(self, book_id, user_id):
        """Issue a book to a user and set a due date."""
        if book_id not in self.data["books"] or user_id not in self.data["users"]:
            print("Error: Invalid Book ID or User ID.")
            return

        book = self.data["books"][book_id]
        if book["available"] <= 0:
            print("Sorry, this book is currently out of stock.")
            return

        issue_date = datetime.now()
        due_date = issue_date + timedelta(days=BORROW_DAYS)

        transaction = {
            "book_id": book_id,
            "user_id": user_id,
            "issue_date": issue_date.strftime("%Y-%m-%d"),
            "due_date": due_date.strftime("%Y-%m-%d"),
            "return_date": None,
            "fine": 0
        }
        
        self.data["transactions"].append(transaction)
        book["available"] -= 1  
        self.save_data()
        
        print(f"Book issued to {self.data['users'][user_id]['name']}.")
        print(f"Due date is: {due_date.strftime('%Y-%m-%d')}")

    def return_book(self, book_id, user_id):
        """Return a book, calculate fine if late, and update records."""
        for trans in self.data["transactions"]:
            if trans["book_id"] == book_id and trans["user_id"] == user_id and trans["return_date"] is None:
                return_date = datetime.now()
                due_date = datetime.strptime(trans["due_date"], "%Y-%m-%d")
                
            
                fine = 0
                if return_date > due_date:
                    days_late = (return_date - due_date).days
                    fine = days_late * FINE_PER_DAY
                
        
                trans["return_date"] = return_date.strftime("%Y-%m-%d")
                trans["fine"] = fine
                self.data["books"][book_id]["available"] += 1
                self.save_data()
                
                print(f"Book returned successfully.")
                if fine > 0:
                    print(f"WARNING: Late return! Fine to pay: ${fine}")
                return
                
        print("No active issue record found for this user and book.")

    def search_books(self, query):
        """Search books by title or author."""
        query = query.lower()
        results = []
        for b_id, details in self.data["books"].items():
            if query in details["title"].lower() or query in details["author"].lower():
                results.append((b_id, details))
        
        if results:
            print(f"\n--- Search Results for '{query}' ---")
            for b_id, b in results:
                print(f"ID: {b_id} | Title: {b['title']} | Author: {b['author']} | Available: {b['available']}/{b['total']}")
        else:
            print("No books found matching your query.")

    def display_books(self, filter_type="all"):
        """Display all, available, or issued books."""
        print(f"\n--- Library Inventory ({filter_type.upper()}) ---")
        for b_id, b in self.data["books"].items():
            if filter_type == "available" and b["available"] == 0:
                continue
            if filter_type == "issued" and b["available"] == b["total"]:
                continue
            
            status = f"Available: {b['available']}/{b['total']}"
            print(f"ID: {b_id} | '{b['title']}' by {b['author']} | {status}")

    def backup_data(self):
        """Create a backup of the database file."""
        if os.path.exists(DATA_FILE):
            shutil.copy(DATA_FILE, BACKUP_FILE)
            print(f"Backup created successfully: {BACKUP_FILE}")
        else:
            print("No data file exists yet to backup.")

    def restore_data(self):
        """Restore the database from the backup file."""
        if os.path.exists(BACKUP_FILE):
            shutil.copy(BACKUP_FILE, DATA_FILE)
            self.load_data()  # Reload memory from the restored file
            print("Data restored successfully from backup.")
        else:
            print("No backup file found to restore.")


def main():
    lib = Library()
    
    while True:
        print("\n" + "="*30)
        print("  LIBRARY MANAGEMENT SYSTEM")
        print("="*30)
        print("1. Add Book")
        print("2. Add User")
        print("3. Issue Book")
        print("4. Return Book")
        print("5. Search Books")
        print("6. Display Available Books")
        print("7. Display Issued Books")
        print("8. Backup Data")
        print("9. Restore Data")
        print("0. Exit")
        
        choice = input("Enter your choice: ")
        
        if choice == '1':
            b_id = input("Enter Book ID: ")
            title = input("Enter Title: ")
            author = input("Enter Author: ")
            copies = int(input("Enter number of copies: "))
            lib.add_book(b_id, title, author, copies)
            
        elif choice == '2':
            u_id = input("Enter User ID: ")
            name = input("Enter User Name: ")
            lib.add_user(u_id, name)
            
        elif choice == '3':
            b_id = input("Enter Book ID: ")
            u_id = input("Enter User ID: ")
            lib.issue_book(b_id, u_id)
            
        elif choice == '4':
            b_id = input("Enter Book ID: ")
            u_id = input("Enter User ID: ")
            lib.return_book(b_id, u_id)
            
        elif choice == '5':
            q = input("Enter title or author to search: ")
            lib.search_books(q)
            
        elif choice == '6':
            lib.display_books("available")
            
        elif choice == '7':
            lib.display_books("issued")
            
        elif choice == '8':
            lib.backup_data()
            
        elif choice == '9':
            lib.restore_data()
            
        elif choice == '0':
            print("Exiting system. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()