import os
from dotenv import load_dotenv
from supabase import create_client
import pandas as pd
import numpy as np
from datetime import datetime
from collections import defaultdict

# Загрузка переменных окружения
load_dotenv()

# Инициализация клиента Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase = create_client(supabase_url, supabase_key)

class RouletteAnalyzer:
    def __init__(self):
        self.numbers = []  # История выпавших чисел
        self.load_history()

    def load_history(self):
        """Загрузка истории из Supabase"""
        try:
            response = supabase.table('roulette_history').select('*').order('timestamp', desc=True).execute()
            self.numbers = [record['number'] for record in response.data]
            self.numbers.reverse()  # Разворачиваем список, чтобы числа шли в хронологическом порядке
        except Exception as e:
            print(f"Ошибка при загрузке данных: {e}")
            self.numbers = []

    def add_number(self, number: int):
        """Добавление нового числа в историю"""
        try:
            data = {
                'number': number,
                'timestamp': datetime.now().isoformat()
            }
            supabase.table('roulette_history').insert(data).execute()
            self.numbers.append(number)  # Добавляем число в конец списка
            print(f"Число {number} успешно добавлено")
        except Exception as e:
            print(f"Ошибка при добавлении числа: {e}")

    def get_hot_numbers(self):
        """Получение часто выпадающих чисел"""
        if not self.numbers:
            return []
        
        recent = self.numbers[-50:]  # Последние 50 чисел
        series = pd.Series(recent)
        counts = series.value_counts()
        mean_freq = counts.mean()
        return counts[counts >= mean_freq].index.tolist()

    def get_cold_numbers(self):
        """Получение редко выпадающих чисел"""
        if not self.numbers:
            return []
        
        recent = self.numbers[-50:]  # Последние 50 чисел
        series = pd.Series(recent)
        counts = series.value_counts()
        mean_freq = counts.mean()
        return counts[counts < mean_freq].index.tolist()

    def calculate_even_odd_ratio(self):
        """Расчет соотношения четных и нечетных чисел"""
        if not self.numbers:
            return 0
        
        recent = self.numbers[-20:]  # Последние 20 чисел
        even_count = sum(1 for x in recent if x % 2 == 0 and x != 0)
        return even_count / len(recent)

    def calculate_sector_probabilities(self):
        """Расчет вероятностей по секторам"""
        if not self.numbers:
            return {'1-12': 0, '13-24': 0, '25-36': 0}
        
        recent = self.numbers[-30:]  # Последние 30 чисел
        total = len(recent)
        
        sectors = {
            '1-12': sum(1 for x in recent if 1 <= x <= 12),
            '13-24': sum(1 for x in recent if 13 <= x <= 24),
            '25-36': sum(1 for x in recent if 25 <= x <= 36)
        }
        
        return {k: v/total for k, v in sectors.items()}

    def analyze_patterns(self):
        if not self.numbers:
            return None

        last_number = self.numbers[-1]
        following_numbers = self._get_following_numbers(last_number)
        
        # Анализ по дюжинам
        dozens_analysis = self._analyze_dozens(following_numbers)
        
        # Анализ по столбцам
        columns_analysis = self._analyze_columns(following_numbers)
        
        return {
            'last_number': last_number,
            'following_numbers': following_numbers,
            'dozens_analysis': dozens_analysis,
            'columns_analysis': columns_analysis
        }

    def _analyze_columns(self, numbers):
        if not numbers:
            return []

        # Определяем столбцы
        column1 = [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34]
        column2 = [2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35]
        column3 = [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36]

        # Подсчитываем количество чисел в каждом столбце
        total = len(numbers)
        col1_count = sum(1 for n in numbers if n in column1)
        col2_count = sum(1 for n in numbers if n in column2)
        col3_count = sum(1 for n in numbers if n in column3)
        zero_count = sum(1 for n in numbers if n == 0)

        return [
            {
                'name': '1-й столбец (1,4,7...34)',
                'count': col1_count,
                'percentage': round((col1_count / total) * 100, 2) if total > 0 else 0,
                'numbers': column1
            },
            {
                'name': '2-й столбец (2,5,8...35)',
                'count': col2_count,
                'percentage': round((col2_count / total) * 100, 2) if total > 0 else 0,
                'numbers': column2
            },
            {
                'name': '3-й столбец (3,6,9...36)',
                'count': col3_count,
                'percentage': round((col3_count / total) * 100, 2) if total > 0 else 0,
                'numbers': column3
            },
            {
                'name': 'Зеро (0)',
                'count': zero_count,
                'percentage': round((zero_count / total) * 100, 2) if total > 0 else 0,
                'numbers': [0]
            }
        ]

    def _get_following_numbers(self, target_number):
        """Поиск всех чисел, которые следуют за заданным числом"""
        following_numbers = []
        for i in range(len(self.numbers) - 1):
            if self.numbers[i] == target_number:
                following_numbers.append(self.numbers[i + 1])
        return following_numbers

    def _analyze_dozens(self, numbers):
        if not numbers:
            return []

        # Определяем дюжины
        dozen1 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        dozen2 = [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
        dozen3 = [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]

        # Подсчитываем количество чисел в каждой дюжине
        total = len(numbers)
        d1_count = sum(1 for n in numbers if n in dozen1)
        d2_count = sum(1 for n in numbers if n in dozen2)
        d3_count = sum(1 for n in numbers if n in dozen3)
        zero_count = sum(1 for n in numbers if n == 0)

        return [
            {
                'name': '1-я дюжина (1-12)',
                'count': d1_count,
                'percentage': round((d1_count / total) * 100, 2) if total > 0 else 0,
                'numbers': dozen1
            },
            {
                'name': '2-я дюжина (13-24)',
                'count': d2_count,
                'percentage': round((d2_count / total) * 100, 2) if total > 0 else 0,
                'numbers': dozen2
            },
            {
                'name': '3-я дюжина (25-36)',
                'count': d3_count,
                'percentage': round((d3_count / total) * 100, 2) if total > 0 else 0,
                'numbers': dozen3
            },
            {
                'name': 'Зеро (0)',
                'count': zero_count,
                'percentage': round((zero_count / total) * 100, 2) if total > 0 else 0,
                'numbers': [0]
            }
        ]

    def find_number_sequences(self, target_number):
        """Поиск всех последовательностей с заданным числом и следующим за ним"""
        sequences = []
        for i in range(len(self.numbers) - 1):
            if self.numbers[i] == target_number:
                sequences.append(self.numbers[i + 1])
        return sequences

    def analyze_next_numbers(self, target_number):
        """Анализ чисел, которые выпадали после заданного числа"""
        if len(self.numbers) < 2:
            return {}

        def get_dozen(num):
            if num == 0:
                return 'Zero'
            elif 1 <= num <= 12:
                return 'First'
            elif 13 <= num <= 24:
                return 'Second'
            else:
                return 'Third'

        # Находим все случаи выпадения целевого числа и следующие за ним числа
        next_numbers = self.find_number_sequences(target_number)
        if not next_numbers:
            return None

        # Анализ следующих чисел
        next_counts = pd.Series(next_numbers).value_counts()
        total = len(next_numbers)

        # Статистика по числам
        number_stats = []
        for next_num, count in next_counts.items():
            percentage = (count / total) * 100
            number_stats.append({
                'number': next_num,
                'count': int(count),
                'percentage': round(percentage, 2)
            })

        # Сортируем по количеству появлений
        number_stats.sort(key=lambda x: x['count'], reverse=True)

        # Анализ дюжин
        next_dozens = [get_dozen(num) for num in next_numbers]
        dozen_counts = pd.Series(next_dozens).value_counts()
        
        dozen_stats = []
        for dozen, count in dozen_counts.items():
            percentage = (count / total) * 100
            dozen_stats.append({
                'dozen': dozen,
                'count': int(count),
                'percentage': round(percentage, 2)
            })

        return {
            'total_appearances': total,
            'next_numbers': number_stats,
            'current_dozen': get_dozen(target_number),
            'next_dozens': dozen_stats
        }

    def predict_next(self):
        """Предсказание следующего числа на основе анализа паттернов"""
        if not self.numbers:
            return "Недостаточно данных для предсказания"

        last_number = self.numbers[-1]
        following_numbers = self._get_following_numbers(last_number)
        
        if not following_numbers:
            return "Недостаточно данных для предсказания"

        # Подсчет частоты каждого числа
        number_counts = {}
        for num in following_numbers:
            number_counts[num] = number_counts.get(num, 0) + 1

        # Сортировка по частоте (по убыванию)
        predictions = []
        total = len(following_numbers)
        for num, count in sorted(number_counts.items(), key=lambda x: x[1], reverse=True):
            predictions.append({
                'number': num,
                'count': count,
                'percentage': round((count / total) * 100, 2)
            })

        # Анализ по дюжинам и столбцам
        dozens_analysis = self._analyze_dozens(following_numbers)
        columns_analysis = self._analyze_columns(following_numbers)

        return {
            'last_number': last_number,
            'predictions': predictions,
            'dozens_analysis': dozens_analysis,
            'columns_analysis': columns_analysis,
            'total_appearances': total
        }

def main():
    analyzer = RouletteAnalyzer()
    
    while True:
        print("\n1. Добавить новое число")
        print("2. Показать анализ")
        print("3. Предсказать следующее число")
        print("4. Выход")
        
        choice = input("Выберите действие (1-4): ")
        
        if choice == '1':
            try:
                number = int(input("Введите число (0-36): "))
                if 0 <= number <= 36:
                    analyzer.add_number(number)
                else:
                    print("Число должно быть от 0 до 36")
            except ValueError:
                print("Пожалуйста, введите корректное число")
        
        elif choice == '2':
            print("\nАнализ последних чисел:")
            print(analyzer.analyze_patterns())
        
        elif choice == '3':
            print("\nПредсказание следующего числа:")
            print(analyzer.predict_next())
        
        elif choice == '4':
            break
        
        else:
            print("Неверный выбор. Пожалуйста, выберите 1-4")

if __name__ == "__main__":
    main()
