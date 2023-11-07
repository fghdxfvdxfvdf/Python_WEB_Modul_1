import re
from collections import UserDict
from datetime import datetime, date
from abc import ABC, abstractmethod


class Field(ABC):
    def __init__(self, value):
        super().__init__() 
        self._value = None
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    def __str__(self):
        return str(self._value)


class Name(Field):
    @Field.value.setter
    def value(self, value):
        if 2 < len(value) < 15:
            self._value = value
        else:
            raise ValueError("Ім'я повинно бути від 3 до 15 символів")


class Phone(Field):
    @Field.value.setter
    def value(self, value):
        if value is not None:
            if len(value) == 10 and value.isdigit():
                if re.match(r'\b067|050|068|096|097|098|063|093|099|095\b', value):
                    self._value = value
                else:
                    raise ValueError('неправильно введено код оператора, має бути: 067, 050, 068, 096,'
                                 '097, 098, 063, 093, 099, 095')    
            else:
                raise ValueError('Номер телефону має бути: код_оператора ХХХХХХ\nКод оператора: 067, 050, 068, 096,'
                                 '097, 098, 063, 093, 099, 095')


class Birthday(Field):
    @Field.value.setter
    def value(self, value: str):
        if value is not None:
            try:
                self._value = datetime.strptime(value, '%d.%m.%Y').date()
            except ValueError:
                raise ValueError('Невірний формат дати. Введіть у форматі dd.mm.yyyy')

    def __str__(self):
        return f"{self._value.strftime('%d.%m.%Y')}"


class Email(Field):
    @Field.value.setter
    def value(self, value):
        if value is not None:
            if re.match(r'\b[A-Za-z0-9._%+-]{2,}@[A-Za-z0-9-]+\.[A-Z|a-z]{2,3}\b', value):
                self._value = value
            else:
                raise ValueError(f'Невірний формат емейла {value} повинно бути у форматі example@email.com')


class Address(Field):
    @Field.value.setter
    def value(self, value):
        if value is not None:
            self._value = value


class Record:
    def __init__(self, name, birthday=None, email=None, address=None):
        self.name = Name(name)  # застосування асоціації під назваю композиція. Об'єкт Name існує поки є об'єкт Record
        self.birthday = Birthday(birthday)
        self.phones = []
        self.email = Email(email)
        self.address = Address(address)

    def add_phone(self, number):
        if number is None:
            return
        elif number in map(lambda num: num.value, self.phones):
            return ' номер вже є'  # Якщо такий номер вже є у контакта
        else:
            self.phones.append(Phone(number))
            return ' номер додано'

    def remove_phone(self, number):
        for phone in self.phones:
            if number == phone.value:
                self.phones.remove(phone)
                return f'Номер {self.name.value} видалено'
        return f'{self.name.value} такого номеру не знайдено'

    def edit_phone(self, old_number, new_number):
        for phone in self.phones:
            if phone.value == old_number:
                index = self.phones.index(phone)
                self.phones[index] = Phone(new_number)
                return
        raise ValueError('Такого номеру немає у контакта')

    def find_phone(self, num):
        for phone in self.phones:
            if phone.value == num:
                return phone

    def add_birthday(self, birthday):
        if self.birthday.value is None:
            self.birthday = Birthday(birthday)
            return '\nдату народження додано'
        else:
            return '\nдата народження вже є'

    def add_email(self, email):
        if self.email.value is None:
            self.birthday = Email(email)
            return '\nemail додано'
        else:
            return '\nemail вже є'

    def add_address(self, address):
        if self.address.value is None:
            self.birthday = Address(address)
            return '\nадресу додано'
        else:
            return '\nадреса вже є'

    def days_to_birthday(self):
        today = date.today()
        current_birthday = datetime(today.year, self.birthday.value.month, self.birthday.value.day).date()
        if current_birthday < today:
            current_birthday = datetime(today.year + 1, self.birthday.value.month, self.birthday.value.day).date()
        delta = current_birthday - today
        return delta.days

    def __str__(self):
        result = f'{self.name.value}:\n\tPhone: {"; ".join(p.value for p in self.phones)}'
        if self.birthday.value is not None:
            result += f'\n\tbirthday: {self.birthday}, days to birthday: {self.days_to_birthday()}'
        if self.email.value is not None:
            result += f'\n\temail: {self.email}'
        if self.address.value is not None:
            result += f'\n\taddress: {self.address}'
        return result


class AddressBook(UserDict):
    def add_record(self, user: Record):                            # асоціація під назвою агригація
        self.data[user.name.value] = user

    def find(self, name):
        if name not in self.data:
            raise KeyError("Немає контакту з таким ім'ям")     # Викликаємо помилку, якщо контакт з таким ім'ям не існує.
        return self.data.get(name)

    def find_birthday_users(self, days):
        users = []
        result = ''
        for record in self.data.values():
            if record.birthday.value is None:
                continue
            if record.days_to_birthday() <= int(days):
                users.append(record)
        if len(users) == 0:
            result += f"Найближчі {days} днів іменинників немає"
        else:
            sorted_users = sorted(users, key=lambda record: record.days_to_birthday())
            for record in sorted_users:
                result += f'{record}'
        return result

    def delete(self, name):
        if name not in self.data:
            raise KeyError("Немає контакту з таким ім'ям")    # Викликаємо помилку, якщо контакт з таким ім'ям не існує.
        self.data.pop(name)

    def iterator(self, page_size):
        print(self.data)
        keys = list(self.data.keys())
        total_pages = (len(keys) + page_size - 1) // page_size
        keys.sort()

        for page_number in range(total_pages):
            start = page_number * page_size
            end = (page_number + 1) * page_size
            page = {k: self.data[k] for k in keys[start:end]}
            yield page

    def find_match(self, string):
        if not self.data:
            return f'Немає жодного контакту'                               # Якщо немає контактів
        result = ''
        for record in self.data.values():
            if string.lower() in record.name.value.lower():
                result += f'{record}\n'

            for number in record.phones:
                if number.value is not None and string in number.value:
                    result += f'{record}\n'

            if record.birthday.value is not None and string in str(record.birthday.value):
                result += f'{record}\n'
        if len(result) == 0:
            result += 'Нічого не знайдено'
        return result
