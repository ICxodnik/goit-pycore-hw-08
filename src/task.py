from collections import UserDict
import re
from datetime import datetime, timedelta

class Field[T]:

    def __init__(self, value):
        self.value = self._validate(value)
    
    def __str__(self):
        return str(self.value)
    
    def _validate(self, value) -> T:
        """Метод валідації, перевизначається в підклассах."""
        pass

class Name(Field[str]):

    def _validate(self, value):
        if not value.strip():
            raise ValueError("Імʼя не може бути порожнім")
        return value

class Phone(Field[str]):

    def _validate(self, value):
        if not re.fullmatch(r"\d{10}", value):
            raise ValueError("Номер телефону має мати 10 символів")
        return value

class Birthday(Field[datetime]):
        
    def _validate(self, value):
        try:
            return datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:

    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))
    
    def remove_phone(self, phone):
        phone_obj = self.find_phone(phone)
        if phone_obj:
            self.phones.remove(phone_obj)
        else:
            raise ValueError(f"Номер {phone} не знайдено")
    
    def edit_phone(self, old_phone, new_phone):
        for p in self.phones:
            if p.value == old_phone:
                p.value = Phone(new_phone).value
                return
        raise ValueError("Номер не знайдено")
    
    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None
    
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)
    
    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"

class AddressBook(UserDict):
    
    MAX_CONG_RANGE = 7

    def add_record(self, record):
        self.data[record.name.value] = record
    
    def find(self, name):
        return self.data.get(name)
    
    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def list_records(self):
        if not self.data:
            return "Немає записів"
        return "\n".join(str(record) for record in self.data.values())
    
    #дає список привітань на цей робочий тиждень
    def get_upcoming_birthdays(self, today = datetime.today().date()):
        max_range = today + timedelta(days = self.MAX_CONG_RANGE)
        # список привітальників
        cong_list = []

        for user in self.data.values():
            birthday = user.birthday.value.replace(year = today.year)
            
            # Переносимо день народження тих хто народився в субботу
            if birthday.weekday() == 5:
                birthday = birthday + timedelta(days = 2)

            # Переносимо день народження тих хто народився в неділю
            if birthday.weekday() == 6:
                birthday = birthday + timedelta(days = 1)

            # Відсіюємо дні народження лише після врахування коректування дня вітання
            if birthday < today or birthday > max_range:
                continue

            cong_list.append({"name": user.name.value, "congratulation_date": birthday.strftime("%Y.%m.%d")})

        return cong_list

if __name__ == "__main__":
# Створення нової адресної книги
    book = AddressBook()

    # Створення запису для John
    john_record = Record("John")
    john_record.add_phone("1234567890")
    john_record.add_phone("5555555555")
    john_record.add_birthday("05.04.2000")
    # Додавання запису John до адресної книги
    book.add_record(john_record)

    # Створення та додавання нового запису для Jane
    jane_record = Record("Jane")
    jane_record.add_phone("9876543210")
    jane_record.add_birthday("29.03.2000")
    book.add_record(jane_record)

    # Виведення всіх записів у книзі
    for name, record in book.data.items():
        print(record)

    # Знаходження та редагування телефону для John
    john = book.find("John")
    john.edit_phone("1234567890", "1112223333")

    print(john)  # Виведення: Contact name: John, phones: 1112223333; 5555555555

    # Пошук конкретного телефону у записі John
    found_phone = john.find_phone("5555555555")
    print(f"{john.name}: {found_phone}")  # Виведення: 5555555555
    
    # Виведення списку привітань на цей робочий тиждень
    upcoming_birthdays = book.get_upcoming_birthdays(datetime(2025, 3, 27))
    
    print(f"Список привітань на цей робочий тиждень:")
    for user in upcoming_birthdays:
        print(f"{user['name']} - {user['congratulation_date']}")

    # Видалення запису Jane
    book.delete("Jane")
