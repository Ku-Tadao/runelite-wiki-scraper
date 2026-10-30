from items import map_tiles, parse_tiles

assert parse_tiles({"1": "3030,3637,qty:5", "name": "Air rune"}, "0") == ["3030,3637,0"]
assert parse_tiles({"1": "2906,3538,respawn:45"}, "1") == ["2906,3538,1"]
assert parse_tiles({"1": "x:3202,y:3253", "2": "x:3206,y:3252"}, "0") == ["3202,3253,0", "3206,3252,0"]
assert parse_tiles({"1": "garbage"}, "0") == []
assert parse_tiles({"1": "x:3091.5,y:9799"}, "0") == ["3091,9799,0"]
assert map_tiles({"x": "3680", "y": "5152", "mtype": "pin"}, "0") == ["3680,5152,0"]
assert map_tiles({"x": "3680", "y": "5152", "1": "x:3674,y:5148"}, "0") == ["3674,5148,0"]
print("parse_tiles ok")
