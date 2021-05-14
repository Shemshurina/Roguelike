from __future__ import annotations 

from typing import Iterable, Iterator, Optional, TYPE_CHECKING 

import numpy as np  # type: ignore
from tcod.console import Console

from entity import Actor, Item
import tile_types

if TYPE_CHECKING:
    from engine import Engine 
    from entity import Entity 


class GameMap:
    def __init__( 
        self, engine: Engine, width: int, height: int, entities: Iterable[Entity] = ()
    ):
        self.engine = engine
        self.width, self.height = width, height
        self.entities = set(entities)
        self.tiles = np.full((width, height), fill_value=tile_types.wall, order="F") #покрывает все стеной сплошной 
        
        self.visible = np.full( 
            (width, height), fill_value=False, order="F"
        )  # Плитка, которую игрок может видеть в данный момент 
        self.explored = np.full(
            (width, height), fill_value=False, order="F"
        )  # Плитки, виденные ранее

        self.downstairs_location = (0, 0)

    @property
    def gamemap(self) -> GameMap:
        return self

    @property
    def actors(self) -> Iterator[Actor]:
        """Итерируется по actors карты."""
        yield from (
            entity
            for entity in self.entities
            if isinstance(entity, Actor) and entity.is_alive
        )

    @property
    def items(self) -> Iterator[Item]:
        yield from (entity for entity in self.entities if isinstance(entity, Item))

    def get_blocking_entity_at_location( #эта функция нужна, чтобы найти монстра, на которого наткнулся игрок
        self, location_x: int, location_y: int,
    ) -> Optional[Entity]:
        for entity in self.entities:
            if ( 
                entity.blocks_movement
                and entity.x == location_x
                and entity.y == location_y
            ): 
                return entity

        return None
    

    def get_actor_at_location(self, x: int, y: int) -> Optional[Actor]:
        for actor in self.actors:
            if actor.x == x and actor.y == y:
                return actor

        return None

    def in_bounds(self, x: int, y: int) -> bool:
        """возвращает True, если координаты внутри границ карты."""
#(нужно, чтобы игрок не мог выйти за пределы карты)
        return 0 <= x < self.width and 0 <= y < self.height

    def render(self, console: Console) -> None:
        """
        Визуализирует карту. 
 
        Если плитка в зоне видимости, то она отрисовывается в светлых цветах.  
        Если нет, но она была ранее исследована, тогда отрисовывается темными цветами.
        Во всех других случаях используется SHROUD (по дефолту) (черные плитки).
        """
        console.tiles_rgb[0 : self.width, 0 : self.height] = np.select( 
# np.select позволяет отрисовывать плитки, которые мы хотим, опираясь на то, что указано в condlist
            condlist=[self.visible, self.explored],
            choicelist=[self.tiles["light"], self.tiles["dark"]],
            default=tile_types.SHROUD,
        ) 

        entities_sorted_for_rendering = sorted( 
            self.entities, key=lambda x: x.render_order.value
        ) 

        for entity in entities_sorted_for_rendering: 
           # печатает только те объекты, которые находятся в FOV
            if self.visible[entity.x, entity.y]:
                console.print( 
                    x=entity.x, y=entity.y, string=entity.char, fg=entity.color
                ) 

class GameWorld:
    """
    Содержит настройки для GameMap, и генерирует новые карты при передвижении по лестнице.
    """

    def __init__(
        self,
        *,
        engine: Engine,
        map_width: int,
        map_height: int,
        max_rooms: int,
        room_min_size: int,
        room_max_size: int,
        current_floor: int = 0,
        lvl: int
    ):
        self.engine = engine

        self.map_width = map_width
        self.map_height = map_height

        self.max_rooms = max_rooms

        self.room_min_size = room_min_size
        self.room_max_size = room_max_size

        self.current_floor = current_floor
        self.lvl = lvl

    def generate_floor(self) -> None:
        from procgen import generate_spaceship

        self.current_floor += 1

        self.engine.game_map = generate_spaceship(
            max_rooms=self.max_rooms,
            room_min_size=self.room_min_size,
            room_max_size=self.room_max_size,
            map_width=self.map_width,
            map_height=self.map_height,
            engine=self.engine,
            floor=self.current_floor,
            lvl=self.lvl,
        )

