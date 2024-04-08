from collections import UserDict
from datetime import datetime

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

class Name(Field):
    def __init__(self, value):
        super().__init__(value)

class Phone(Field):
    def __init__(self, value):
        if not isinstance(value, str):
            raise ValueError("Phone number must be a string")
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must be a 10-digit string")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            self.date = datetime.strptime(value, "%d.%m.%Y")
            super().__init__(self.date.strftime("%d.%m.%Y"))
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        phone_found = False
        for p in self.phones:
            if p.value == old_phone:
                if len(new_phone) != 10 or not new_phone.isdigit():
                    raise ValueError("Invalid phone number format")
                p.value = new_phone
                phone_found = True
        if not phone_found:
            raise ValueError("Phone number not found")

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}, birthday: {self.birthday.value if self.birthday else 'Not set'}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def get_upcoming_birthdays(self, days=7):
        upcoming_birthdays = []
        today = datetime.today()
        for record in self.data.values():
            if record.birthday:
                birthday_date = record.birthday.date.replace(year=today.year)
                if birthday_date < today:
                    birthday_date = birthday_date.replace(year=today.year + 1)
                days_until_birthday = (birthday_date - today).days
                if 0 <= days_until_birthday < days:
                    upcoming_birthdays.append((record.name.value, days_until_birthday))
        return upcoming_birthdays

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Contact is already exist"
        except KeyError as e:
            return f"I can't find this contact: {e}"
        except Exception as e:
            return f"Error: {e}"
    return inner

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    if record is None:
        record = Record(name)
        if phone:
            record.add_phone(phone)
        book.add_record(record)
        return "Contact added."
    else:
        raise Exception("Contact already exists. To change contact, use 'change' command.")


@input_error
def show_phone(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record:
        phones = ', '.join(p.value for p in record.phones)
        return f"Phones for {name}: {phones}."
    else:
        raise KeyError("Contact not found.")

@input_error
def change_phone(args, book: AddressBook):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return f"Phone number changed for {name}."
    else:
        raise KeyError("Contact not found.")

@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return f"Birthday added for {name}."
    else:
        return f"Contact '{name}' not found."

@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return f"{name}'s birthday: {record.birthday.value}"
    elif record:
        return f"{name} has no birthday set."
    else:
        raise KeyError("Contact not found.")

@input_error
def birthdays(args, book):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if upcoming_birthdays:
        message = "Upcoming birthdays:\n"
        for name, days_until_birthday in upcoming_birthdays:
            message += f"{name}'s birthday is in {days_until_birthday} days.\n"
        return message
    else:
        return "No upcoming birthdays found."

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_phone(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            for record in book.data.values():
                print(record)

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
