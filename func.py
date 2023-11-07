import pickle
import classes


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as e:
            return e
        except ValueError as e:
            return e
        except IndexError:
            return "Введіть ім'я з номером телефону або з датою народження"
        except TypeError:
            return 'Give me command'

    return inner


# Декорована функція для формування сторінки с записами
@input_error
def compiling_page(page_number, contacts, total):
    result = ''   # f'\nPage number {page_number} of {total}\n'
    for name, record in contacts.items():
        result += f'{record}\n'
    return result


# Декорована функція для додавання нового контакту або оновлення існуючого.
@input_error
def add(*args, **kwargs):
    if len(args) == 1:                                                  # Якщо додається з gui
        for key in kwargs:
            if len(kwargs[key].strip()) == 0:
                kwargs[key] = None
        if kwargs['name'] is None:
            return f"Ви не ввели ім'я"
        if kwargs['name'] in phonebook.data:                              # Якщо контакт вже є
            result = f'У котакта {kwargs["name"]} '
            name_record = phonebook.find(kwargs['name'])                  # Знайдемо контакт за ім'ям
            result_phone = name_record.add_phone(kwargs['phone'])
            result_birthday = name_record.add_birthday(kwargs['birthday'])
            result_email = name_record.add_email(kwargs['email'])
            result_address = name_record.add_address(kwargs['address'])
            result = result + result_phone + result_birthday + result_email + result_address
            return result
        else:
            name_record = classes.Record(kwargs['name'], kwargs['birthday'], kwargs['email'], kwargs['address'])
            name_record.add_phone(kwargs['phone'])
            phonebook.add_record(name_record)
            return f'Успішно додано контакт '

    else:                                                                 # Якщо додається з консолі
        if args[1] in phonebook.data:                                     # Якщо контакт вже є
            name_record = phonebook.find(args[1])                         # Знайдемо контакт за ім'ям
            if '.' in args[2]:                                            # Якщо третім аргументом елемент дати
                text = name_record.add_birthday(args[2])
                return f'Дата народження {text}'                          # Повідомить про додавання дня народження
            else:
                result = name_record.add_phone(args[2])                   # Додаємо новий номер, якщо контакт вже існує.
                return f'Номер {args[2]} {result} {args[1]}'
        if len(args) == 4:
            name_record = classes.Record(args[1], args[3])
        else:
            name_record = classes.Record(args[1])
        name_record.add_phone(args[2])
        phonebook.add_record(name_record)
        return f'Контакт {args[1]} з номером {args[2]} успішно додано'  # Повідомляємо користувача про успішне додавання.


# Декорована функція для зміни номера телефону контакту.
@input_error
def change(*args):
    name_record = phonebook.find(args[1])                    # Знаходимо об'єкт Record контакту
    name_record.edit_phone(args[2], args[3])                 # Змінюємо старий номер на новий
    return f'Номер {args[2]} для {args[1]} було змінено на {args[3]}'


# Декорована функція для видалення номеру у контакта
@input_error
def remove(*args):
    name_record = phonebook.find(args[1])
    result = name_record.remove_phone(args[2])
    return result


# Декорована функція для отримання номера телефону контакту.
@input_error
def phone(*args):
    name_record = phonebook.find(args[1])
    result = f"{'; '.join(p.value for p in name_record.phones)}"
    return result                                            # Повертаємо номера телефонів контакту.


# Декорована функція для отримання всієї інформаціі о контакту, або отримання сторінки контактів
@input_error
def show(*args):
    name_record = phonebook.find(args[1])
    return name_record


# Декорована функція для виведення всіх контактів.
@input_error
def show_all(*args):
    if not phonebook:
        raise ValueError('Немає жодного контакту')                     # Якщо немає контактів
    result = ''
    chunk_size = 7                                          # Кількість контактів на сторінці за замовченням
    user_page = None
    if len(args) > 1:                                       # Якщо користувач ввів кількість контактів на сторінці
        chunk_size = int(args[1])
    total_page = ((len(phonebook.data) + chunk_size - 1) // chunk_size)     # Кількість сторінок
    if len(args) == 3:                                      # Якщо користувач ввів номер сторінки
        user_page = int(args[2])
        if user_page > total_page:
            return f'Total pages: {total_page}'
    generator = phonebook.iterator(chunk_size)
    if user_page is None:
        for page_number, page in enumerate(generator, start=1):
            result += compiling_page(page_number, page, total_page)
    else:
        page = [item for index, item in enumerate(generator, start=1) if index == user_page]
        result = compiling_page(user_page, page[0], total_page)

    return result

@input_error
def birthday(*args):
    if len(args[1]) == 0:
        days = 7
    elif args[1].isdigit():
        days = args[1]
    else:
        raise ValueError('Ви ввели не число')
    return phonebook.find_birthday_users(days)

# Декорована функція для видалення контакту
@input_error
def delete(*args):
    phonebook.delete(args[1])
    return f'Контакт {args[1]} видалено'


@input_error
def get_handler(*args):
    command = args[0].lower()
    return COMMANDS[command]


COMMANDS = {'remove': remove,           # Видаляє номер у контакта
            'add': add,                 # Додає новий контакт та до існуючого номер або дату народження.
            'change': change,           # Змінює старий номер на новий
            'phone': phone,             # Пошук номеру(номерів) телефону контакту за ім'ям
            'show all': show_all,       # Виводить всі записи(можно задати к-ть контактів на сторінці,та номер сторінки)
            'delete': delete,           # Видалення контакту
            'show': show,               # Виводить всі записи контакту за ім'ям
            'birthday': birthday}


try:
    with open('book.bin', 'rb') as file:
        phonebook = pickle.load(file)   # Завантажуємо контакти з файлу

except FileNotFoundError:
    print('Book is not. Create new book')
    phonebook = classes.AddressBook()           # Створюємо пустий словник для зберігання контактів (імена-ключі, номери
    # телефону-значення), якщо файлу не існує


def main():
    while True:
        input_user = input('Write command \t')
        list_input = []
        if input_user.lower() in ('good bay', 'close', 'exit'):
            with open('book.bin', 'wb') as file:
                pickle.dump(phonebook, file)
            print('Good bay!')
            break
        elif input_user[:8].lower() == 'show all':
            list_input.append(input_user[:8])
            list_input.extend(input_user[8:].split())
            arguments = tuple(list_input)
            print(get_handler(*arguments)(*arguments))
        else:
            list_input = input_user.split()
            arguments = tuple(list_input)
            handler = get_handler(*arguments)
            if handler not in COMMANDS.values():
                print(phonebook.find_match(input_user))
                continue
            print(handler(*arguments))


if __name__ == '__main__':
    main()