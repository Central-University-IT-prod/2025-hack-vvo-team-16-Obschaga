from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

def find_suitable_rooms(db_filename="rooms.sqlite", preferred_sex="F", preferred_floor=1, preferred_capacity=1):
    """
    Находит подходящие комнаты в базе данных на основе заданных критериев.

    Args:
        db_filename (str, optional): Имя файла базы данных. Defaults to "rooms.sqlite".
        preferred_sex (str, optional): Пол проживающих (F/M). Defaults to "F".
        preferred_floor (int, optional): Желаемый этаж. Defaults to 1.
        preferred_capacity (int, optional): Желаемое количество мест. Defaults to 1.

    Returns:
        str: Строка с информацией о подходящих комнатах в формате "ROOM:ROOM_NUM(x;y), SEX:sex, N_ROOMS:amount / ...".
             Если комнаты не найдены, возвращает "Комнаты не найдены".
    """

    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()

    # Создаем SQL-запрос с параметрами
    query = """
        SELECT ROOM_NUM, ROOM_GEO_X, ROOM_GEO_Y, ROOM_SEX, ROOM_AMMOUNT
        FROM Rooms
        WHERE ROOM_SEX = ? AND ROOM_FLOOR = ? AND ROOM_AMMOUNT = ?
    """

    cursor.execute(query, (preferred_sex, preferred_floor, preferred_capacity))
    suitable_rooms = cursor.fetchall()

    conn.close()

    if not suitable_rooms:
        return "Комнаты не найдены"

    # Формируем строку с результатами
    result = ""
    for room_num, x, y, sex, amount in suitable_rooms:
        result += f"ROOM:{room_num}({x};{y}), SEX:{sex}, N_ROOMS:{amount} / "

    return result[:-3]  # Удаляем последние ' / '

@app.route('/', methods=['GET', 'POST'])
def index():
    error = None #инициализируем переменную error
    if request.method == 'POST':
        sex = request.form['sex'].upper()  # Преобразуем в верхний регистр для соответствия базе данных
        floor = int(request.form['floor'])
        capacity = int(request.form['capacity'])

        if capacity <= 0:
            error = "Количество мест должно быть положительным числом."
        else:
            suitable_rooms = find_suitable_rooms(preferred_sex=sex, preferred_floor=floor, preferred_capacity=capacity)
            return render_template('index.html', rooms=suitable_rooms, error=error)
    return render_template('index.html', error=error)

if __name__ == '__main__':
    app.run(debug=True)

