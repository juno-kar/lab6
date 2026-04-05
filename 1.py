import re
from pathlib import Path


def get_custom_sort_key(text: str) -> tuple:
    """
    Функція, що повертає спеціальний ключ для сортування.
    Правила:
    1. Українські літери (кирилиця) йдуть першими.
    2. Латинські літери йдуть після українських.
    3. Всередині групок зберігається алфавітний порядок (незалежно від регістру).
    """
    
    UA_ALPHABET = "абвгґдеєжзиіїйклмнопрстуфхцчшщьюя"
    LATIN_ALPHABET = "abcdefghijklmnopqrstuvwxyz"
    
    result_key = []
    lower_text = text.lower()
    
    for char in lower_text:
        if char in UA_ALPHABET:
            # українська літера: (0, позиція в алфавіті)
            pos = UA_ALPHABET.index(char)
            result_key.append((0, pos, char))
        elif char in LATIN_ALPHABET:
            # латинська літера: (1, позиція в алфавіті)
            pos = LATIN_ALPHABET.index(char)
            result_key.append((1, pos, char))
        else:
            # інші символи (цифри, знаки пунктуації)
            result_key.append((2, ord(char), char))
    
    return tuple(result_key)


def sort_text(text: str) -> str:
    """
    Сортує текст за правилами (українські > латинські).
    """
    # розбиваємо текст на слова
    words = re.findall(r'\S+', text)
    
    # сортуємо слова
    sorted_words = sorted(words, key=get_custom_sort_key)
    
    # з'єднуємо назад у рядок
    return ' '.join(sorted_words)


def read_text_from_file(filepath: str) -> str:
    """
    Читає текст з файлу.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        print(f"Помилка: Файл '{filepath}' не знайдено!")
        return None
    except Exception as e:
        print(f"Помилка при читанні файлу: {e}")
        return None


def write_text_to_file(filepath: str, text: str) -> bool:
    """
    Записує текст у файл.
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)
        return True
    except Exception as e:
        print(f"Помилка при записі файлу: {e}")
        return False


def sort_file(input_filepath: str, output_filepath: str = None) -> bool:
    """
    Читає текст з файлу, сортує слова тексту та виводить результат а екран
    
    Args:
        input_filepath: Шлях до вхідного файлу
        output_filepath: Шлях до вихідного файлу (якщо None, то перевписує вхідний)
    
    Returns:
        True, якщо успішно; False інакше
    """
    
    # читаємо вхідний файл
    print(f"Читаємо файл: {input_filepath}")
    content = read_text_from_file(input_filepath)
    
    if content is None:
        return False
    
    print(f"Прочитано {len(content)} символів")
    print(f"Вміст файлу: {content}")
    
    # сортуємо текст
    print("\nСортуємо текст...")
    sorted_content = sort_text(content)
    print(f"Результат: {sorted_content}")

def main():
    while True:
        choice = input("Виберіть опцію (1-2): ").strip()
        
        if choice == '1':
            input_file = input("Введіть шлях до вхідного файлу: ").strip()
            
            if input_file:
                sort_file(input_file)
            else: print("Перевірте правильність шляху до файлу та його назву!")

        elif choice == '2':
            print("Завершуємо роботу...")
            break
        
        else:
            print("Ви вибрали неправильне значення. Спробуйте ще раз.")

if __name__ == "__main__":
    main()