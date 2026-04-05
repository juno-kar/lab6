import sys
import subprocess
import platform
from urllib.parse import urlparse, unquote

# idna для підтримки Punycode
try:
    import idna # type: ignore
    IDNA_AVAILABLE = True
except ImportError:
    IDNA_AVAILABLE = False

class Decode:
    def __init__(self):
        self.system = platform.system()

    def is_likely_url(self, text: str) -> bool:
        """Коротка перевірка: чи схожий текст на посилання."""
        text = text.strip()

        # посилання не мають пробілів і повинні мати хоча б одну крапку
        if not text or " " in text or "." not in text:
            return False
        
        parsed = urlparse(text if "://" in text else "http://" + text)

        # перевіряємо, чи є хоча б доменне ім'я (напр. site.com)
        if parsed.netloc and "." in parsed.netloc:
            return True
        return False

    def clipboard(self) -> str:
        """Зчитує текст з буфера обміну."""
        try:
            if self.system == "Windows":

                # використовуємо PowerShell для читання буфера
                process = subprocess.Popen(
                    ['powershell', '-NoProfile', '-Command', 'Get-Clipboard'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding='utf-8'
                )
                stdout, _ = process.communicate()
                return stdout.strip() if stdout else ""
            
            elif self.system == "Darwin":
                process = subprocess.Popen(["pbpaste"], stdout=subprocess.PIPE, text=True)
                stdout, _ = process.communicate()
                return stdout.strip() if stdout else ""
            
            elif self.system == "Linux":
                for cmd in [["xclip", "-selection", "clipboard", "-o"], ["xsel", "-b", "-o"]]:
                    try:
                        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)
                        stdout, _ = process.communicate()
                        if stdout: return stdout.strip()
                    except FileNotFoundError:
                        continue
            return ""
        except Exception:
            return ""
        
    def copy_to_clipboard(self, text: str) -> bool:
        """Копіює текст в буфер обміну."""
        try:
            if self.system == "Windows":
                # використовуємо стандартну утиліту clip.exe
                process = subprocess.Popen(["clip"], stdin=subprocess.PIPE, text=True)
                process.communicate(text)
                return True
            
            elif self.system == "Darwin":
                process = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE, text=True)
                process.communicate(text)
                return True
            
            elif self.system == "Linux":
                try:
                    process = subprocess.Popen(["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE, text=True)
                    process.communicate(text)
                    return True
                except FileNotFoundError:
                    return False
            return False
        except:
            return False
    
    def detect_encoding_type(self, url: str) -> str:
        if 'xn--' in url.lower(): return "punycode"
        if '%' in url: return "url_encoded"
        return "plain"
    
    def decode_punycode(self, domain: str) -> tuple:
        try:
            if IDNA_AVAILABLE:
                return idna.decode(domain), True, "OK"
            return domain, False, "IDNA missing"
        except Exception as e:
            return domain, False, str(e)
    
    def decode_url_encoded(self, url: str) -> tuple:
        try:
            decoded = unquote(url)
            return decoded, decoded != url, "OK"
        except Exception as e:
            return url, False, str(e)
    
    def analyze_url(self, url: str) -> dict:
        encoding_type = self.detect_encoding_type(url)

        # додаємо префікс для коректного парсингу, якщо його немає
        parse_url = url if "://" in url else "http://" + url
        try:
            parsed = urlparse(parse_url)
            domain = parsed.netloc
            path = parsed.path + ("?" + parsed.query if parsed.query else "")
        except:
            domain = path = ""
        
        results = {
            'original_url': url, 
            'encoding_type': encoding_type, 
            'domain': domain, 
            'path': path, 
            'decoded_parts': {}
        }
        
        if domain and 'xn--' in domain.lower():
            d_dom, success, _ = self.decode_punycode(domain)
            results['decoded_parts']['domain'] = {'original': domain, 'decoded': d_dom, 'success': success, 'method': 'Punycode'}
        
        if '%' in url:
            d_url, success, _ = self.decode_url_encoded(url)
            results['fully_decoded'] = d_url
            
        if 'domain' in results['decoded_parts'] and 'fully_decoded' not in results:
            results['fully_decoded'] = url.replace(domain, results['decoded_parts']['domain']['decoded'])
            
        return results

def main():
    decoder = Decode()
    print("Аналіз буфера обміну...")
    
    clipboard_content = decoder.clipboard()
    
    if clipboard_content and decoder.is_likely_url(clipboard_content):
        print(f"Знайдено посилання: {clipboard_content}")
        url = clipboard_content
    else:
        if clipboard_content:
            print(f"Текст у буфері не схожий на посилання: '{clipboard_content[:40]}...'")
        else:
            print("Буфер порожній.")
        url = input("\nВведіть посилання вручну: ").strip()

    if not url:
        print("Введення порожнє. Вихід.")
        return

    results = decoder.analyze_url(url)
    
    print("\nРЕЗУЛЬТАТ")
    print(f"Оригінал: {results['original_url']}")
    
    final_text = results.get('fully_decoded', url)
    if final_text != url:
        print(f"Декодовано: {final_text}")
        if decoder.copy_to_clipboard(final_text):
            print("\n[Успіх] Результат скопійовано в буфер обміну!")
    else:
        print("Посилання вже в чистому вигляді або не потребує декодування.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nПрограму зупинено користувачем.")
    except Exception as e:
        print(f"\nКритична помилка: {e}")