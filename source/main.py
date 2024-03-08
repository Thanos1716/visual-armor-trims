#!/usr/bin/env python3
import numpy as np
from PIL import Image
import json
import os
import shutil

verbose = True

def load_json(filepath):
    with open(filepath, "r") as file:
        data = json.load(file)
    return data

def save_json(filepath, data):
    with open(filepath, "w") as file:
        json.dump(data, file, indent=4)

def get_data(path):
    img = Image.open(path).convert("RGBA")
    return np.array(img)

def colorise(trim_image, color_index):
    new_trim_image = np.zeros([*trim_image.shape], dtype=np.uint8)
    for y in range(len(trim_image)):
        for x in range(len(trim_image[y])):
            new_trim_image[y,x] = trim_image[y,x]#[255, 255, 255, 255]#colors[color_index,i]
            for i in range(len(colors[0])):
                # print(colors[0,i], trim_image[y,x])
                if tuple(colors[0,i]) == tuple(trim_image[y,x]):
                    # try:
                    new_trim_image[y,x] = colors[color_index + 1,i]
                    # print(trim_image[y,x])
                        # print(new_trim_image[y,x])
                    # except KeyError:
                        # new_trim_image[y,x] = [0, 0, 0, 255]
    return new_trim_image

colors = np.array(Image.open("armor_trim_palette.png").convert("RGBA"))

palettes = ["redstone", "copper", "gold", "gold_darker", "emerald", "diamond", "diamond_darker", "lapis", "amethyst", "quartz", "iron", "iron_darker", "netherite", "netherite_darker"]
trims = ["sentry", "vex", "wild", "coast", "dune", "wayfinder", "raiser", "shaper", "host", "ward", "silence", "tide", "snout", "rib", "eye", "spire"]
armor_types = ["helmet", "chestplate", "leggings", "boots"]
armor_materials = ["leather", "iron", "chainmail", "gold", "diamond", "netherite", "turtle"]

trim_paths = [f"{armor_material}/{trim}" for trim in trims for armor_material in armor_materials]

# try:
#     shutil.rmtree("../assets")
# except FileNotFoundError:
#     pass

for armor_type in armor_types:
    for trim_path in trims + trim_paths:  # FIX: try trim paths last so will overwrite any short trim paths

        trim = trim_path.split("/")[-1]
        partial_trim_dir_path = f"item/{armor_type}_trim/{trim_path}"
        trim_dir_path = f"assets/minecraft/textures/{partial_trim_dir_path}"

        try:
            trim_image_data = get_data(f"{trim_dir_path}.png")
        except FileNotFoundError:
            continue

        for trim_palette_index in range(len(palettes)):

            trim_palette = palettes[trim_palette_index]

            partial_trim_file_path = f"{partial_trim_dir_path}/{trim_palette}"
            trim_file_path = f"{trim_dir_path}/{trim_palette}"

            try:
                os.makedirs(f"../{trim_dir_path}")
            except FileExistsError:
                pass

            trim_image = Image.fromarray(colorise(trim_image_data, trim_palette_index))
            trim_image.save(f"../{trim_file_path}.png")

            verbose and print(f"Created output {trim_file_path}")


        for armor_material in armor_materials:

            if armor_material == "turtle" and armor_type != "helmet":
                continue

            item_name = "{}_{}".format("golden" if armor_material == "gold" else armor_material, armor_type)

            partial_dir_path = f"item/{item_name}"
            partial_file_path = f"{partial_dir_path}/{trim}"
            dir_path = f"assets/minecraft/textures/{partial_dir_path}"
            file_path = f"assets/minecraft/textures/{partial_file_path}"

            try:
                os.makedirs(f"../{dir_path}")
            except FileExistsError:
                pass

            # cut out trim shape from armor to avoid z-fighting in item frames, in hand, on ground etc.
            item_image_mask_data = get_data(f"{dir_path}.png")

            for y in range(len(trim_image_data)):
                for x in range(len(trim_image_data[y])):
                    if trim_image_data[y, x, 3] != 0:
                        item_image_mask_data[y, x] = [0, 0, 0, 0]

            item_image_mask = Image.fromarray(item_image_mask_data)
            item_image_mask.save(f"../{file_path}.png")


            # also perform cut out on the leather overlay (trims display over overlays)
            if armor_material == "leather":

                try:
                    os.makedirs(f"../{dir_path}_overlay")
                except FileExistsError:
                    pass

                item_image_overlay_mask_data = get_data(f"{dir_path}_overlay.png")

                for y in range(len(trim_image_data)):
                    for x in range(len(trim_image_data[y])):
                        if trim_image_data[y, x, 3] != 0:
                            item_image_overlay_mask_data[y, x] = [0 ,0, 0, 0]

                item_image_overlay_mask = Image.fromarray(item_image_overlay_mask_data)
                item_image_overlay_mask.save(f"../{dir_path}_overlay/{trim}.png")


            for trim_palette_index in range(len(palettes)):

                if palettes[trim_palette_index] in ["gold_darker", "diamond_darker", "iron_darker", "netherite_darker"]:
                    continue

                trim_material = palettes[trim_palette_index]
                trim_palette = palettes[trim_palette_index + (1 if armor_material == trim_material else 0)]

                # trim_palette == armor_material and print(trim_palette, trim_material)

                partial_trim_file_path = f"{partial_trim_dir_path}/{trim_palette}"
                trim_file_path = f"{trim_dir_path}/{trim_palette}"

                if armor_material == "leather":
                    model_data = {
                            "parent": "minecraft:item/generated",
                            "textures": {
                                "layer0": f"minecraft:{partial_file_path}",
                                "layer1": f"minecraft:{partial_dir_path}_overlay/{trim}",
                                "layer2": f"minecraft:{partial_trim_file_path}"
                            }
                        }

                else:
                    model_data = {
                            "parent": "minecraft:item/generated",
                            "textures": {
                                "layer0": f"minecraft:{partial_file_path}",
                                "layer1": f"minecraft:{partial_trim_file_path}"
                            }
                        }

                partial_model_dir_path = f"item/{item_name}/{trim}"
                partial_model_file_path = f"item/{item_name}/{trim}/{trim_material}"
                model_dir_path = f"assets/minecraft/models/{partial_model_dir_path}"
                model_file_path = f"{model_dir_path}/{trim_material}"

                try:
                    os.makedirs(f"../{model_dir_path}")
                except FileExistsError:
                    pass

                save_json(f"../{model_file_path}.json", model_data)

                verbose and print(f"Created model {model_file_path}.json")


                cit_dir_path = f"assets/minecraft/optifine/cit/{partial_model_dir_path}"
                cit_file_path = f"{cit_dir_path}/{trim_material}"

                try:
                    os.makedirs(f"../{cit_dir_path}")
                except FileExistsError:
                    pass

                with open(f"../{cit_file_path}.properties", 'w') as f:

                    f.write(
f"""type=item
matchItems={item_name}
model={partial_model_file_path}
nbt.Trim.material=minecraft:{trim_material}
nbt.Trim.pattern=minecraft:{trim}
"""
)

                verbose and print(f"Created CIT {cit_file_path}.properties")
