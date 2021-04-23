# генератор этажей
from __future__ import annotations

import random
from typing import Iterator, List, Tuple, TYPE_CHECKING

import tcod

import entity_factories
from game_map import GameMap
import tile_types

if TYPE_CHECKING:
    from engine import Engine 

class RectangularRoom:
    def __init__(self, x: int, y: int, width: int, height: int): #рамки комнаты
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height
    
    @property
    def center(self) -> Tuple[int, int]: #центр комнаты, нужен будет для рисования туннелей
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)

        return center_x, center_y
    
    @property
    def inner(self) -> Tuple[slice, slice]: #внутренности комнаты с учетом того, что между комнатами должны быть стены
        """Возвращает внутренюю область комнаты."""
        return slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2)

    def intersects(self, other: RectangularRoom) -> bool: #проверяет перекрывает ли одна комната другую и возвращает True, если да
        return (
            self.x1 <= other.x2
            and self.x2 >= other.x1
            and self.y1 <= other.y2
            and self.y2 >= other.y1
        )
def place_entities(
    room: RectangularRoom, dungeon: GameMap, maximum_monsters: int,
) -> None:
    number_of_monsters = random.randint(0, maximum_monsters)

    for i in range(number_of_monsters):
        x = random.randint(room.x1 + 1, room.x2 - 1) #рандомно выбирается координата в пределах комнаты, где будет монстр
        y = random.randint(room.y1 + 1, room.y2 - 1)

        if not any(entity.x == x and entity.y == y for entity in dungeon.entities): #проверяет нет ли там уже монстра
            if random.random() < 0.7:
                entity_factories.monst1.spawn(dungeon, x, y)
            else:
                entity_factories.monst2.spawn(dungeon, x, y)

def tunnel_between(
    start: Tuple[int, int], end: Tuple[int, int]
) -> Iterator[Tuple[int, int]]:
    """Возвращает L-образный туннель между двумя точками."""
    x1, y1 = start 
    x2, y2 = end
    if random.random() < 0.5:  # 50% шанс.
        #горизонтально, затем вертикально.
        corner_x, corner_y = x2, y1
    else:
        #вертикально, затем горизонтально.
        corner_x, corner_y = x1, y2

    # Генерирует координаты туннеля. #линии Бразенхема 
    for x, y in tcod.los.bresenham((x1, y1), (corner_x, corner_y)).tolist(): 
        yield x, y  #возвращает "генератор", вместо возвращения значения и выхода из функции
    for x, y in tcod.los.bresenham((corner_x, corner_y), (x2, y2)).tolist():
        yield x, y

def generate_dungeon(
    max_rooms: int,
    room_min_size: int,
    room_max_size: int,
    map_width: int,
    map_height: int,
    max_monsters_per_room: int,
    engine: Engine,
 ) -> GameMap:
    """создает новую карту"""
    player = engine.player
    dungeon = GameMap(engine, map_width, map_height, entities=[player]) 

    rooms: List[RectangularRoom] = []

    for r in range(max_rooms):
        room_width = random.randint(room_min_size, room_max_size)
        room_height = random.randint(room_min_size, room_max_size)

        x = random.randint(0, dungeon.width - room_width - 1)
        y = random.randint(0, dungeon.height - room_height - 1)

        new_room = RectangularRoom(x, y, room_width, room_height)

        # Проверяет, не накладываются комнаты друг на друга.
        if any(new_room.intersects(other_room) for other_room in rooms):
            continue  # Комната накладывается, поэтому она не появляется на карте.
        # Если комната не накладывается на другую, то она подходит.

        # Внутренность комнаты становится полом.
        dungeon.tiles[new_room.inner] = tile_types.floor

        if len(rooms) == 0:
            # первая комната, в которой появится персонаж
            player.place(*new_room.center, dungeon) 
        else:  # все комнаты после первой
            # создает туннель между этой комнатой и предыдущей
            for x, y in tunnel_between(rooms[-1].center, new_room.center):
                dungeon.tiles[x, y] = tile_types.floor

        place_entities(new_room, dungeon, max_monsters_per_room)

        # добавляет новую комнату в список
        rooms.append(new_room)

    return dungeon
