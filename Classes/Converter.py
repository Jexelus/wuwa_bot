import os
import base64

import orjson

from instance.database import create_guide, add_to_favorite
import json


def start():
    preform_guides = os.listdir("./guides")
    for guide in preform_guides:
        with open(f"./guides/{guide}/info.json", 'r', encoding='utf-8') as f:
            guide_info = json.load(f)
            f.close()
        constellation_image = base64.b64encode(open(f"./guides/{guide}/ava.jpg", "rb").read()).decode("utf-8")
        constellation_talents_image = base64.b64encode(open(f"./guides/{guide}/talent.jpg", "rb").read()).decode("utf-8")
        constellation_weapon_image = base64.b64encode(open(f"./guides/{guide}/weapon.jpg", "rb").read()).decode("utf-8")

        create_guide(
            constellation_name=guide_info["constellation_name"],
            constellation_rarity=guide_info["constellation_rarity"],
            constellation_element=guide_info["constellation_element"],
            constellation_weapon_type=guide_info["constellation_weapon_type"],
            constellation_role=guide_info["constellation_role"],
            constellation_rising_materials=guide_info["constellation_rising_materials"],
            constellation_rising_talent_materials=guide_info["constellation_rising_talent_materials"],
            constellation_image=constellation_image,
            constellation_talents_image=constellation_talents_image,
            constellation_weapon_image=constellation_weapon_image
        )

