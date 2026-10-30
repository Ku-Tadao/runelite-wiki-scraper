from items import format_location, map_tiles, parse_tiles, required_key, version_locations
import mwparserfromhell as mw

assert parse_tiles({"1": "3030,3637,qty:5", "name": "Air rune"}, "0") == ["3030,3637,0"]
assert parse_tiles({"1": "2906,3538,respawn:45"}, "1") == ["2906,3538,1"]
assert parse_tiles({"1": "x:3202,y:3253", "2": "x:3206,y:3252"}, "0") == ["3202,3253,0", "3206,3252,0"]
assert parse_tiles({"1": "garbage"}, "0") == []
assert parse_tiles({"1": "x:3091.5,y:9799"}, "0") == ["3091,9799,0"]
assert map_tiles({"x": "3680", "y": "5152", "mtype": "pin"}, "0") == ["3680,5152,0"]
assert map_tiles({"x": "3680", "y": "5152", "1": "x:3674,y:5148"}, "0") == ["3674,5148,0"]
assert format_location("Taverley Dungeon (Upper Level){{Refn|Requires a blue dragon Slayer task.|group=l}}{{Refn|Requires {{SCP|Agility|70|link=yes}}.|name=Taverley|group=l}}") == "Taverley Dungeon (Upper Level)"
assert format_location('Lithkren Vault <ref group="l">Requires completion of Dragon Slayer II</ref>') == "Lithkren Vault"
assert format_location('Corsair Cove Dungeon<ref group "l">Requires Dragon Slayer II</ref>') == "Corsair Cove Dungeon"
assert format_location("Abyssal Area ({{Fairycode|alr}})") == "Abyssal Area (ALR)"
assert format_location("{{FloorNumber|uk=0|caps=y}} of Dorgesh-Kaan") == "Ground floor of Dorgesh-Kaan"
assert format_location("1st floor of the Grand Tree. <br/> {{*}} East of the Gnomeball Field") == "1st floor of the Grand Tree. East of the Gnomeball Field"
assert format_location("[[Varrock]] ({{Floor|2}})") == "Varrock (2nd floor)"
assert format_location("[[Lumbridge Castle|the castle]]") == "the castle"
def locs(*versions):
    return [{"location": str(i), "dropversion": v} for i, v in enumerate(versions)]
assert [l["location"] for l in version_locations(locs("Regular", "Regular, Free-to-Play", "Wilderness Slayer Cave"), "Free-to-play")] == ["1"]
assert [l["location"] for l in version_locations(locs("Standard", "Wilderness Slayer Cave"), "Missing")] == ["0", "1"]
assert [l["location"] for l in version_locations(locs("Standard", ""), "")] == ["0", "1"]
assert "dropversion" not in version_locations(locs("a"), "a")[0]
assert required_key(mw.parse("{{Infobox Scenery|name=Muddy chest}}\nIt can only be opened with a [[muddy key]].\n==Loot==\n[[Steel key]]")) == "Muddy key"
assert required_key(mw.parse("{{Infobox Scenery|examine=a [[spare key]]}}\nAn open chest.\n==Loot==\n[[Steel key]]")) == ""
assert required_key(mw.parse("{{Infobox Monster|name=Rat}}\nDrops a [[brass key]].")) == ""
print("parse_tiles ok")
