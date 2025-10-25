#!/usr/bin/env python3
"""
Универсальный тестер для FastAPI приложения
Включает тестирование всех роутеров и функциональности
"""

import asyncio
import json
import sys
import time
from typing import Optional, Dict, Any, List
import httpx
from pydantic import BaseModel


class WalletAuthRequest(BaseModel):
    wallet_address: str
    signature: str


class SendEmailCodeRequest(BaseModel):
    email: str


class VerifyEmailCodeRequest(BaseModel):
    email: str
    code: str


class MessageCreate(BaseModel):
    content: str
    chat_id: int


class APITester:
    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # Токены для аутентификации
        self.current_user = {
            "access_token": None, 
            "token_type": None,
            "exp": None,
            "user_id": None,
            "wallet_address": None
        }
        
        self.test_results = {
            "auth": {},
            "user": {},
            "chat": {},
            "events": {},
            "errors": []
        }
        
        self.start_time = None
        self.end_time = None

    async def close(self):
        """Закрыть HTTP клиент"""
        await self.client.aclose()

    def print_response(self, response: httpx.Response, title: str):
        """Красиво вывести ответ"""
        print(f"\n{'='*50}")
        print(f"{title}")
        print(f"{'='*50}")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
        except:
            print(f"Response Text: {response.text}")
        
        return response

    def get_headers(self, include_auth: bool = True) -> Dict[str, str]:
        """Получить заголовки для запроса"""
        headers = {"Content-Type": "application/json"}
        if include_auth and self.current_user["access_token"]:
            headers["Authorization"] = f"Bearer {self.current_user['access_token']}"
        return headers

    async def test_get_auth_message(self):
        """Тест получения сообщения для аутентификации"""
        print("\n🔐 Тестируем получение сообщения для аутентификации...")
        
        try:
            response = await self.client.get(f"{self.base_url}/auth/message")
            self.print_response(response, "GET AUTH MESSAGE")
            
            if response.status_code == 200:
                print("✅ Сообщение для аутентификации получено успешно!")
                return True
            else:
                print(f"❌ Ошибка при получении сообщения: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Ошибка при получении сообщения: {e}")
            return False

    async def test_wallet_authenticate(self):
        """Тест аутентификации через кошелек"""
        print("\n🔐 Тестируем аутентификацию через кошелек...")
        
        wallet_address = input("Введите адрес кошелька (или Enter для '0x1234567890abcdef'): ").strip()
        if not wallet_address:
            wallet_address = "0x1234567890abcdef"
        
        signature = input("Введите подпись (или Enter для 'test_signature'): ").strip()
        if not signature:
            signature = "test_signature"
        
        auth_data = WalletAuthRequest(
            wallet_address=wallet_address,
            signature=signature
        )
        
        try:
            response = await self.client.post(
                f"{self.base_url}/auth/authenticate",
                json=auth_data.dict()
            )
            self.print_response(response, "WALLET AUTHENTICATE")
            
            if response.status_code == 200:
                data = response.json()
                self.current_user["access_token"] = data.get("access_token")
                self.current_user["token_type"] = data.get("token_type")
                self.current_user["exp"] = data.get("exp")
                print("✅ Аутентификация через кошелек прошла успешно!")
                return True
            else:
                print(f"❌ Ошибка при аутентификации: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Ошибка при аутентификации: {e}")
            return False

    async def test_send_email_code(self):
        """Тест отправки кода верификации на email"""
        print("\n📧 Тестируем отправку кода верификации...")
        
        email = input("Введите email для отправки кода (или Enter для 'test@example.com'): ").strip()
        if not email:
            email = "test@example.com"
        
        email_data = SendEmailCodeRequest(email=email)
        
        try:
            response = await self.client.post(
                f"{self.base_url}/auth/send-email-code",
                json=email_data.dict()
            )
            self.print_response(response, "SEND EMAIL CODE")
            
            if response.status_code == 200:
                print("✅ Код верификации отправлен успешно!")
                return True
            else:
                print(f"❌ Ошибка при отправке кода: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Ошибка при отправке кода: {e}")
            return False

    async def test_verify_email_code(self):
        """Тест верификации email кода"""
        print("\n📧 Тестируем верификацию email кода...")
        
        if not self.current_user["access_token"]:
            print("❌ Нет токена! Сначала выполните аутентификацию.")
            return False
        
        email = input("Введите email для верификации (или Enter для 'test@example.com'): ").strip()
        if not email:
            email = "test@example.com"
        
        code = input("Введите код верификации (или Enter для '123456'): ").strip()
        if not code:
            code = "123456"
        
        verify_data = VerifyEmailCodeRequest(email=email, code=code)
        
        try:
            response = await self.client.post(
                f"{self.base_url}/auth/verify-email-code",
                json=verify_data.dict(),
                headers=self.get_headers()
            )
            self.print_response(response, "VERIFY EMAIL CODE")
            
            if response.status_code == 200:
                print("✅ Email код верифицирован успешно!")
                return True
            else:
                print(f"❌ Ошибка при верификации кода: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Ошибка при верификации кода: {e}")
            return False

    async def test_get_user_profile(self):
        """Тест получения профиля пользователя"""
        print("\n👤 Тестируем получение профиля пользователя...")
        
        if not self.current_user["access_token"]:
            print("❌ Нет токена! Сначала выполните аутентификацию.")
            return False
        
        try:
            response = await self.client.get(
                f"{self.base_url}/user/me",
                headers=self.get_headers()
            )
            self.print_response(response, "GET USER PROFILE")
            
            if response.status_code == 200:
                print("✅ Профиль пользователя получен успешно!")
                return True
            else:
                print(f"❌ Ошибка при получении профиля: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Ошибка при получении профиля: {e}")
            return False

    async def test_create_chat(self):
        """Тест создания чата"""
        print("\n💬 Тестируем создание чата...")
        
        if not self.current_user["access_token"]:
            print("❌ Нет токена! Сначала выполните аутентификацию.")
            return False
        
        try:
            response = await self.client.post(
                f"{self.base_url}/chat/",
                headers=self.get_headers()
            )
            self.print_response(response, "CREATE CHAT")
            
            if response.status_code == 200:
                data = response.json()
                chat_id = data.get("id")
                if chat_id:
                    print(f"✅ Чат создан успешно! ID: {chat_id}")
                    return chat_id
                else:
                    print("✅ Чат создан, но ID не получен")
                    return True
            else:
                print(f"❌ Ошибка при создании чата: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Ошибка при создании чата: {e}")
            return False

    async def test_get_user_chats(self):
        """Тест получения чатов пользователя"""
        print("\n💬 Тестируем получение чатов пользователя...")
        
        if not self.current_user["access_token"]:
            print("❌ Нет токена! Сначала выполните аутентификацию.")
            return False
        
        limit = input("Введите лимит (или Enter для 10): ").strip()
        if not limit:
            limit = 10
        
        offset = input("Введите offset (или Enter для 0): ").strip()
        if not offset:
            offset = 0
        
        try:
            response = await self.client.get(
                f"{self.base_url}/chat/?limit={limit}&offset={offset}",
                headers=self.get_headers()
            )
            self.print_response(response, "GET USER CHATS")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Получено {len(data)} чатов!")
                return True
            else:
                print(f"❌ Ошибка при получении чатов: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Ошибка при получении чатов: {e}")
            return False

    async def test_get_chat_by_id(self):
        """Тест получения чата по ID"""
        print("\n💬 Тестируем получение чата по ID...")
        
        if not self.current_user["access_token"]:
            print("❌ Нет токена! Сначала выполните аутентификацию.")
            return False
        
        chat_id = input("Введите ID чата (или Enter для 1): ").strip()
        if not chat_id:
            chat_id = "1"
        
        try:
            response = await self.client.get(
                f"{self.base_url}/chat/{chat_id}",
                headers=self.get_headers()
            )
            self.print_response(response, "GET CHAT BY ID")
            
            if response.status_code == 200:
                print("✅ Чат получен успешно!")
                return True
            else:
                print(f"❌ Ошибка при получении чата: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Ошибка при получении чата: {e}")
            return False

    async def test_get_chat_messages(self):
        """Тест получения сообщений чата"""
        print("\n💬 Тестируем получение сообщений чата...")
        
        if not self.current_user["access_token"]:
            print("❌ Нет токена! Сначала выполните аутентификацию.")
            return False
        
        chat_id = input("Введите ID чата (или Enter для 1): ").strip()
        if not chat_id:
            chat_id = "1"
        
        limit = input("Введите лимит (или Enter для 10): ").strip()
        if not limit:
            limit = 10
        
        offset = input("Введите offset (или Enter для 0): ").strip()
        if not offset:
            offset = 0
        
        try:
            response = await self.client.get(
                f"{self.base_url}/chat/{chat_id}/messages?limit={limit}&offset={offset}",
                headers=self.get_headers()
            )
            self.print_response(response, "GET CHAT MESSAGES")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Получено {len(data)} сообщений!")
                return True
            else:
                print(f"❌ Ошибка при получении сообщений: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Ошибка при получении сообщений: {e}")
            return False

    async def test_send_message(self):
        """Тест отправки сообщения"""
        print("\n💬 Тестируем отправку сообщения...")
        
        if not self.current_user["access_token"]:
            print("❌ Нет токена! Сначала выполните аутентификацию.")
            return False
        
        chat_id = input("Введите ID чата (или Enter для 1): ").strip()
        if not chat_id:
            chat_id = "1"
        
        content = input("Введите текст сообщения (или Enter для 'Привет, как дела?'): ").strip()
        if not content:
            content = "Привет, как дела?"
        
        message_data = MessageCreate(
            content=content,
            chat_id=int(chat_id)
        )
        
        try:
            response = await self.client.post(
                f"{self.base_url}/chat/{chat_id}/message/",
                json=message_data.dict(),
                headers=self.get_headers()
            )
            self.print_response(response, "SEND MESSAGE")
            
            if response.status_code == 200:
                print("✅ Сообщение отправлено успешно!")
                return True
            else:
                print(f"❌ Ошибка при отправке сообщения: {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"Детали ошибки: {error_detail}")
                except:
                    print(f"Текст ошибки: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Ошибка при отправке сообщения: {e}")
            return False

    async def test_send_message_with_task(self):
        """Тест отправки сообщения с задачей"""
        print("\n💬 Тестируем отправку сообщения с задачей...")
        
        if not self.current_user["access_token"]:
            print("❌ Нет токена! Сначала выполните аутентификацию.")
            return False
        
        chat_id = input("Введите ID чата (или Enter для 1): ").strip()
        if not chat_id:
            chat_id = "1"
        
        task_name = input("Введите название задачи (или Enter для 'summarize'): ").strip()
        if not task_name:
            task_name = "summarize"
        
        content = input("Введите текст сообщения (или Enter для 'Пожалуйста, суммируй этот текст'): ").strip()
        if not content:
            content = "Пожалуйста, суммируй этот текст"
        
        message_data = MessageCreate(
            content=content,
            chat_id=int(chat_id)
        )
        
        try:
            response = await self.client.post(
                f"{self.base_url}/chat/{chat_id}/message/{task_name}",
                json=message_data.dict(),
                headers=self.get_headers()
            )
            self.print_response(response, "SEND MESSAGE WITH TASK")
            
            if response.status_code == 200:
                print("✅ Сообщение с задачей отправлено успешно!")
                return True
            else:
                print(f"❌ Ошибка при отправке сообщения с задачей: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Ошибка при отправке сообщения с задачей: {e}")
            return False

    async def test_get_task_types(self):
        """Тест получения типов задач"""
        print("\n📋 Тестируем получение типов задач...")
        
        if not self.current_user["access_token"]:
            print("❌ Нет токена! Сначала выполните аутентификацию.")
            return False
        
        try:
            response = await self.client.get(f"{self.base_url}/chat/task", headers=self.get_headers())
            self.print_response(response, "GET TASK TYPES")
            
            if response.status_code == 200:
                print("✅ Типы задач получены успешно!")
                return True
            else:
                print(f"❌ Ошибка при получении типов задач: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Ошибка при получении типов задач: {e}")
            return False

    async def test_get_user_events(self):
        """Тест получения событий пользователя"""
        print("\n📊 Тестируем получение событий пользователя...")
        
        if not self.current_user["access_token"]:
            print("❌ Нет токена! Сначала выполните аутентификацию.")
            return False
        
        try:
            response = await self.client.get(
                f"{self.base_url}/events/all",
                headers=self.get_headers()
            )
            self.print_response(response, "GET USER EVENTS")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Получено {len(data)} событий!")
                return True
            else:
                print(f"❌ Ошибка при получении событий: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Ошибка при получении событий: {e}")
            return False

    async def test_get_chat_status(self):
        """Тест проверки статуса чата"""
        print("\n📊 Тестируем проверку статуса чата...")
        
        if not self.current_user["access_token"]:
            print("❌ Нет токена! Сначала выполните аутентификацию.")
            return False
        
        chat_id = input("Введите ID чата (или Enter для 1): ").strip()
        if not chat_id:
            chat_id = "1"
        
        try:
            response = await self.client.get(f"{self.base_url}/chat/{chat_id}/status", headers=self.get_headers())
            self.print_response(response, "GET CHAT STATUS")
            
            if response.status_code == 200:
                status_data = response.json()
                print(f"✅ Статус чата {chat_id}: {status_data.get('is_pending', False)}")
                return True
            else:
                print(f"❌ Ошибка при проверке статуса чата: {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"Детали ошибки: {error_detail}")
                except:
                    print(f"Текст ошибки: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Ошибка при проверке статуса чата: {e}")
            return False

    def show_menu(self):
        """Показать меню тестов"""
        print("\n" + "="*80)
        print("🚀 ИНТЕРАКТИВНОЕ ТЕСТИРОВАНИЕ FASTAPI ПРИЛОЖЕНИЯ")
        print("="*80)
        print("\n📋 ВЫБЕРИТЕ ТЕСТ ДЛЯ ВЫПОЛНЕНИЯ:")
        
        print("\n🔐 AUTH ROUTER (/auth):")
        print("  1. Получение сообщения для аутентификации")
        print("  2. Аутентификация через кошелек")
        print("  3. Отправка кода верификации на email")
        print("  4. Верификация email кода")
        
        print("\n👤 USER ROUTER (/user):")
        print("  5. Получение профиля пользователя")
        
        print("\n💬 CHAT ROUTER (/chat):")
        print("  6. Создание чата")
        print("  7. Получение чатов пользователя")
        print("  8. Получение чата по ID")
        print("  9. Получение сообщений чата")
        print("  10. Отправка сообщения")
        print("  11. Отправка сообщения с задачей")
        print("  12. Получение типов задач")
        
        print("\n📊 EVENTS ROUTER (/events):")
        print("  13. Получение событий пользователя")
        
        print("\n💬 CHAT STATUS:")
        print("  14. Проверка статуса чата")
        
        print("\n🎯 СПЕЦИАЛЬНЫЕ КОМАНДЫ:")
        print("  0. Запустить все тесты")
        print("  q. Выход")
        print("\n" + "="*80)

    async def run_interactive_tests(self):
        """Запуск интерактивных тестов"""
        self.start_time = time.time()
        
        # Словарь всех тестов
        tests = {
            1: ("Получение сообщения для аутентификации", self.test_get_auth_message),
            2: ("Аутентификация через кошелек", self.test_wallet_authenticate),
            3: ("Отправка кода верификации на email", self.test_send_email_code),
            4: ("Верификация email кода", self.test_verify_email_code),
            5: ("Получение профиля пользователя", self.test_get_user_profile),
            6: ("Создание чата", self.test_create_chat),
            7: ("Получение чатов пользователя", self.test_get_user_chats),
            8: ("Получение чата по ID", self.test_get_chat_by_id),
            9: ("Получение сообщений чата", self.test_get_chat_messages),
            10: ("Отправка сообщения", self.test_send_message),
            11: ("Отправка сообщения с задачей", self.test_send_message_with_task),
            12: ("Получение типов задач", self.test_get_task_types),
            13: ("Получение событий пользователя", self.test_get_user_events),
            14: ("Проверка статуса чата", self.test_get_chat_status),
        }
        
        successful_tests = 0
        total_tests = 0
        
        while True:
            self.show_menu()
            
            choice = input("\nВведите номер теста или 'q' для выхода: ").strip().lower()
            
            if choice == 'q':
                break
            elif choice == '0':
                # Запуск всех тестов
                print("\n🚀 ЗАПУСК ВСЕХ ТЕСТОВ...")
                for test_num, (test_name, test_func) in tests.items():
                    print(f"\n{test_num}. {test_name}...")
                    try:
                        result = await test_func()
                        total_tests += 1
                        if result:
                            successful_tests += 1
                    except Exception as e:
                        print(f"❌ Критическая ошибка в тесте '{test_name}': {e}")
                        total_tests += 1
                break
            else:
                try:
                    test_num = int(choice)
                    if test_num in tests:
                        test_name, test_func = tests[test_num]
                        print(f"\n{test_name}...")
                        try:
                            result = await test_func()
                            total_tests += 1
                            if result:
                                successful_tests += 1
                        except Exception as e:
                            print(f"❌ Критическая ошибка в тесте '{test_name}': {e}")
                            total_tests += 1
                    else:
                        print("❌ Неверный номер теста!")
                except ValueError:
                    print("❌ Введите корректный номер теста!")
        
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        
        # Итоговый отчет
        if total_tests > 0:
            print(f"\n{'='*80}")
            print("📊 ИТОГОВЫЙ ОТЧЕТ")
            print(f"{'='*80}")
            print(f"⏱️  Время выполнения: {duration:.2f} секунд")
            print(f"📈 Всего тестов: {total_tests}")
            print(f"✅ Успешных: {successful_tests}")
            print(f"❌ Неудачных: {total_tests - successful_tests}")
            print(f"📊 Процент успеха: {(successful_tests/total_tests*100):.1f}%")
            
            if successful_tests == total_tests:
                print("\n🎉 Все тесты выполнены успешно!")
            else:
                print(f"\n⚠️  {total_tests - successful_tests} тестов завершились с ошибками")
        
        print(f"\n🔗 Полезные ссылки:")
        print(f"   - Swagger UI: {self.base_url}/docs")
        print(f"   - ReDoc: {self.base_url}/redoc")


async def main():
    """Главная функция"""
    tester = APITester()
    try:
        await tester.run_interactive_tests()
    finally:
        await tester.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️  Тестирование прервано пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Критическая ошибка: {e}")
        sys.exit(1)
