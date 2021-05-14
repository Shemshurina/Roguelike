 # файл для 
from __future__ import annotations

import copy
import math
from typing import Optional, Tuple, Type, TypeVar, TYPE_CHECKING, Union
from render_order import RenderOrder 

if TYPE_CHECKING:
   from components.ai import BaseAI
   from components.consumable import Consumable
   from components.fighter import Fighter
   from components.inventory import Inventory
   from game_map import GameMap

T = TypeVar("T", bound="Entity") 


class Entity:
    """ Класс для всех возможных объектов игры (для игроков, врагов, предметов etc.) """
    parent: Union[GameMap, Inventory]
    def __init__(   
        self,
        parent: Optional[GameMap] = None, 
        x: int = 0, 
        y: int = 0,
        char: str = "?",
        color: Tuple[int, int, int] = (255, 255, 255),
        name: str = "<Unnamed>",
        blocks_movement: bool = False,
        render_order: RenderOrder = RenderOrder.CORPSE, 
    ):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks_movement = blocks_movement
        self.render_order = render_order 
        if parent:
            # Если parent не представлен сейчас, то он будет предоставлен позже.
            self.parent = parent
            parent.entities.add(self) 
    
# x, y - координаты объекта на карте
# char - отражение объекта (e.g. для игрока это @)
# color - цвет объекта (задается тремя числами системы RGB)
# name - имя существа
# blocks_movement - двигается или нет (True/False)

    @property
    def gamemap(self) -> GameMap:
        return self.parent.gamemap

    def spawn(self: T, gamemap: GameMap, x: int, y: int) -> T:
        """создает копию существа из GameMap в данной локации"""
        clone = copy.deepcopy(self)
        clone.x = x
        clone.y = y
        clone.parent = gamemap 
        gamemap.entities.add(clone)
        return clone

    def place(self, x: int, y: int, gamemap: Optional[GameMap] = None) -> None: 
        """Размещает объект в новом месте.  Управляет передвижением по карте."""
        self.x = x
        self.y = y
        if gamemap:
            if hasattr(self, "parent"):  # Parent возможно не инициализирован.
                if self.parent is self.gamemap:
                    self.gamemap.entities.remove(self)
            self.parent = gamemap
            gamemap.entities.add(self)

    def distance(self, x: int, y: int) -> float:
        """
        Возвращает расстояние между текущим объектом и данными (x, y) координатами.
        """
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def move(self, dx: int, dy: int) -> None:
        # Переместить объект на заданную величину:
        self.x += dx
        self.y += dy
    # функция move изменяет позицию объекта

class Actor(Entity): # actor - герой/монстр
   def __init__(
       self,
       *,
       x: int = 0,
       y: int = 0,
       char: str = "?",
       color: Tuple[int, int, int] = (255, 255, 255),
       name: str = "<Unnamed>",
       ai_cls: Type[BaseAI],
       fighter: Fighter,
       inventory: Inventory,
   ):
       super().__init__(
           x=x,
           y=y,
           char=char,
           color=color,
           name=name,
           blocks_movement=True,
           render_order=RenderOrder.ACTOR, 
       )

       self.ai: Optional[BaseAI] = ai_cls(self)

       self.fighter = fighter
       self.fighter.parent = self

       self.inventory = inventory
       self.inventory.parent = self

   @property
   def is_alive(self) -> bool:
       """Возвращает True, если actor может совершать действия."""
       return bool(self.ai)

class Item(Entity): # item - аптечка или оружие
   def __init__(
       self,
       *,
       x: int = 0,
       y: int = 0,
       char: str = "?",
       color: Tuple[int, int, int] = (255, 255, 255),
       name: str = "<Unnamed>",
       consumable: Consumable,
   ):
       super().__init__(
           x=x,
           y=y,
           char=char,
           color=color,
           name=name,
           blocks_movement=False,
           render_order=RenderOrder.ITEM,
       )

       self.consumable = consumable
       self.consumable.parent = self
