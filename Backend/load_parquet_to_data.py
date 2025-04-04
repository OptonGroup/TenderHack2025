import pandas as pd
import os
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database import SessionLocal, init_db
from models import Data


def load_parquet_to_data(parquet_path: str, 
                         title_column: Optional[str] = None, 
                         description_column: Optional[str] = None, 
                         batch_size: int = 1000) -> dict:
    """
    Загружает данные из parquet-файла в таблицу Data.
    
    Args:
        parquet_path: Путь к parquet-файлу
        title_column: Название столбца для поля title (если не указано, используется первый текстовый столбец)
        description_column: Название столбца для поля description (если не указано, используется второй текстовый столбец)
        batch_size: Размер пакета для загрузки (по умолчанию 1000 записей)
    
    Returns:
        dict: Словарь с результатами выполнения:
            - success (bool): Успешно ли завершено выполнение
            - message (str): Сообщение о результате
            - imported (int): Количество импортированных записей
            - total (int): Общее количество записей в файле
            - errors (list): Список ошибок (если есть)
    """
    # Проверяем наличие файла
    if not os.path.exists(parquet_path):
        return {
            "success": False,
            "message": f"Файл '{parquet_path}' не найден",
            "imported": 0,
            "total": 0,
            "errors": [f"Файл '{parquet_path}' не найден"]
        }
    
    try:
        # Читаем parquet-файл
        df = pd.read_parquet(parquet_path)
        total_records = len(df)
        
        # Если не указаны столбцы для title и description, 
        # автоматически выбираем текстовые столбцы
        text_columns = df.select_dtypes(include=['object', 'string']).columns
        
        if not title_column and len(text_columns) > 0:
            title_column = text_columns[0]
        
        if not description_column and len(text_columns) > 1:
            description_column = text_columns[1]
        elif not description_column and len(text_columns) == 1:
            # Если есть только один текстовый столбец, используем его для title,
            # а description оставляем пустым
            description_column = None
        
        # Проверяем наличие выбранных столбцов
        if not title_column or title_column not in df.columns:
            return {
                "success": False,
                "message": f"Столбец для заголовка '{title_column}' не найден в файле",
                "imported": 0,
                "total": total_records,
                "errors": [f"Столбец для заголовка '{title_column}' не найден в файле"]
            }
        
        # Создаем соединение с БД
        db = SessionLocal()
        imported_count = 0
        errors = []
        
        try:
            # Обрабатываем данные пакетами
            for i in range(0, total_records, batch_size):
                batch_df = df.iloc[i:i+batch_size]
                
                for _, row in batch_df.iterrows():
                    try:
                        # Получаем значения для title и description
                        title = str(row[title_column])
                        description = str(row[description_column]) if description_column and description_column in df.columns else None
                        
                        # Проверяем, что title не пустой
                        if not title or title.lower() == 'nan' or title.strip() == '':
                            title = "Без заголовка"
                        
                        # Создаем запись в таблице Data
                        data_item = Data(title=title, description=description)
                        db.add(data_item)
                        imported_count += 1
                    except Exception as e:
                        errors.append(f"Ошибка при обработке строки: {str(e)}")
                
                # Сохраняем пакет в БД
                db.commit()
            
            return {
                "success": True,
                "message": f"Успешно импортировано {imported_count} из {total_records} записей",
                "imported": imported_count,
                "total": total_records,
                "errors": errors
            }
        except SQLAlchemyError as e:
            db.rollback()
            return {
                "success": False,
                "message": f"Ошибка базы данных: {str(e)}",
                "imported": imported_count,
                "total": total_records,
                "errors": [f"Ошибка базы данных: {str(e)}"] + errors
            }
        finally:
            db.close()
    
    except Exception as e:
        return {
            "success": False,
            "message": f"Ошибка при чтении parquet-файла: {str(e)}",
            "imported": 0,
            "total": 0,
            "errors": [f"Ошибка при чтении parquet-файла: {str(e)}"]
        }


def main():
    """
    Главная функция для вызова загрузки данных из командной строки
    """
    # Убедимся, что таблицы созданы
    init_db()
    
    # Путь к файлу
    parquet_path = "docs/dataset.parquet"
    
    # Загружаем данные
    result = load_parquet_to_data(parquet_path)
    
    # Выводим результат
    print(f"Результат импорта:")
    print(f"Статус: {'Успешно' if result['success'] else 'Ошибка'}")
    print(f"Сообщение: {result['message']}")
    print(f"Импортировано записей: {result['imported']} из {result['total']}")
    
    if result['errors']:
        print(f"Ошибки ({len(result['errors'])}):")
        for i, error in enumerate(result['errors'][:5], 1):
            print(f"{i}. {error}")
        
        if len(result['errors']) > 5:
            print(f"... и еще {len(result['errors']) - 5} ошибок")


if __name__ == "__main__":
    main() 