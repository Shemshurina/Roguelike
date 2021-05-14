from components.ai import HostileEnemy
from components import consumable
from components.fighter import Fighter
from components.inventory import Inventory
from entity import Actor, Item

player = Actor(
   char="@",
   color=(255, 255, 255),
   name="Player",
   ai_cls=HostileEnemy,
   fighter=Fighter(hp=30, defense=2, power=5),
   inventory=Inventory(capacity=26),
   # 26 по числу букв англ алфавита (каждая буква может представлять собой инвентарь) 
)

monst1 = Actor( 
   char="u",
   color=(142, 7, 54),
   name="Untung",
   ai_cls=HostileEnemy,
   fighter=Fighter(hp=10, defense=0, power=3),
   inventory=Inventory(capacity=0),
)
monst2 = Actor( 
   char="T",
   color=(142, 7, 54),
   name="Tiada",
   ai_cls=HostileEnemy,
   fighter=Fighter(hp=16, defense=1, power=4),
   inventory=Inventory(capacity=0),
)

first_aid = Item(
   char="+",
   color=(4, 161, 110),
   name="First Aid Kit",
   consumable=consumable.HealingConsumable(amount=6),
)

space_bomb = Item(
   char="*",
   color=(255, 255, 0),
   name="Space Bomb",
   consumable=consumable.BombDamageConsumable(damage=12, radius=3),
)

space_gun = Item(
   char="\"",
   color=(255, 255, 0),
   name="Space Gun",
   consumable=consumable.GunDamageConsumable(damage=20, maximum_range=5),
)

key = Item(
   char="1",
   color=(255, 215, 0),
   name="Key",
   consumable=consumable.KeyConsumable(amount=1),
)

