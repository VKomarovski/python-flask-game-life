import random
import copy
from threading import Lock
from flask import Flask, render_template, request


class SingletonMeta(type):
    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances or args or kwargs:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class GameOfLife(metaclass=SingletonMeta):
    def __init__(self, width=10, height=10):
        self.__width = width
        self.__height = height
        self.world = self.generate_universe()
        self.old_world = self.world
        self.cycle_counter = 0

    def form_new_generation(self):
        universe = self.world
        new_world = [[0 for _ in range(self.__width)] for _ in range(self.__height)]

        for i in range(len(universe)):
            for j in range(len(universe[0])):

                if universe[i][j]:
                    if self.__get_near(universe, [i, j]) not in (2, 3):
                        new_world[i][j] = 0
                        continue
                    new_world[i][j] = 1
                    continue

                if self.__get_near(universe, [i, j]) == 3:
                    new_world[i][j] = 1
                    continue
                new_world[i][j] = 0
        self.old_world = copy.deepcopy(self.world)
        self.world = new_world

    def generate_universe(self):
        return [[random.randint(0, 1) for _ in range(self.__width)] for _ in range(self.__height)]

    @staticmethod
    def __get_near(universe, pos, system=None):
        if system is None:
            system = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))

        count = 0
        for i in system:
            if universe[(pos[0] + i[0]) % len(universe)][(pos[1] + i[1]) % len(universe[0])]:
                count += 1
        return count


app = Flask(__name__)


@app.route('/', methods=['post', 'get'])
def index():
    width = 10
    height = 10
    if request.method == "POST":
        width = int(request.form.get('width'))
        height = int(request.form.get('height'))
    GameOfLife(width, height)
    return render_template('index.html', width=width, height=height)


@app.route('/live')
def live():
    life = GameOfLife()
    if life.cycle_counter > 0:
        life.form_new_generation()
    life.cycle_counter = life.cycle_counter + 1
    return render_template('live.html', life=life)


if __name__ == '__main__':
    app.run(port=3030)
