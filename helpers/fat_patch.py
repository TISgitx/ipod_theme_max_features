import fs
from pathlib import Path
from pyfatfs import PyFatFS
from fontTools import ttLib, subset
import base64
import io
import sys
import os

fat = PyFatFS.PyFatFS("./rsrc.bin", read_only=False)
print(fat.listdir('/Resources/UI'))
print(fat.listdir('/Resources/Sounds'))

FONT_BASE = "/Resources/Fonts/"
IMAGE_BASE = "/Resources/UI/SilverImagesDB.LE.bin"

# List of all languages (without .bin/.bin2 for convenience)
LANG_FILES = [
    "SilverDB.ar_SA.LE",
    "SilverDB.ca_ES.LE",
    "SilverDB.cs_CZ.LE",
    "SilverDB.da_DK.LE",
    "SilverDB.de_DE.LE",
    "SilverDB.el_GR.LE",
    "SilverDB.en_GB.LE",
    "SilverDB.es_ES.LE",
    "SilverDB.fi_FI.LE",
    "SilverDB.fr_FR.LE",
    "SilverDB.he_IL.LE",
    "SilverDB.hr_HR.LE",
    "SilverDB.hu_HU.LE",
    "SilverDB.id_ID.LE",
    "SilverDB.it_IT.LE",
    "SilverDB.ja_JP.LE",
    "SilverDB.ko_KR.LE",
    "SilverDB.ms_MY.LE",
    "SilverDB.nl_NL.LE",
    "SilverDB.no_NO.LE",
    "SilverDB.pl_PL.LE",
    "SilverDB.pt_BR.LE",
    "SilverDB.pt_PT.LE",
    "SilverDB.ro_RO.LE",
    "SilverDB.ru_RU.LE",
    "SilverDB.sk_SK.LE",
    "SilverDB.sv_SE.LE",
    "SilverDB.th_TH.LE",
    "SilverDB.tr_TR.LE",
    "SilverDB.uk_UA.LE",
    "SilverDB.vi_VN.LE",
    "SilverDB.zh_CN.LE",
    "SilverDB.zh_HK.LE",
    "SilverDB.zh_TW.LE",
]

sounds_list = [
    "Alarm.m4a",
    "Ascending.m4a",
    "Bark.m4a",
    "Bell Tower.m4a",
    "bleep_context.wav",
    "Blues.m4a",
    "Boing.m4a",
    "camera.wav",
    "clicker.wav",
    "Crickets.m4a",
    "criticalbattery.wav",
    "Digital.m4a",
    "Doorbell.m4a",
    "Duck.m4a",
    "Harp.m4a",
    "marimba.m4a",
    "Motorcycle.m4a",
    "Old Car Horn.m4a",
    "Old Phone.m4a",
    "Piano Riff.m4a",
    "Pinball.m4a",
    "Robot.m4a",
    "Sci-Fi.m4a",
    "shake.wav",
    "Simon_Note01.wav",
    "Simon_Note02.wav",
    "Simon_Note03.wav",
    "Simon_Note04.wav",
    "Sonar.m4a",
    "Strum.m4a",
    "Timba.m4a",
    "Time Passing.m4a",
    "Trill.m4a",
    "VoiceOver_Alert.wav",
    "VoiceOver_BubbleAppear.wav",
    "VoiceOver_BubbleDisappear.wav",
    "VoiceOver_ContainerTouch.wav",
    "VoiceOver_Drill.wav",
    "VoiceOver_DrillOut.wav",
    "VoiceOver_ElementBorder.wav",
    "VoiceOver_ElementCenter.wav",
    "VoiceOver_EmptySpace.wav",
    "VoiceOver_PopupAppeared.wav",
    "VoiceOver_Reorder.wav",
    "VoiceOver_ScreenChange.wav",
    "VoiceOver_ScrollPage.wav",
    "VoiceOver_Select.wav",
    "VoiceOver_WrapBack.wav",
    "VoiceOver_WrapBoundary.wav",
    "VoiceOver_WrapForward.wav",
    "volumebeep.wav",
    "Xylophone.m4a",
]

# --- Export SilverImagesDB ---
with fat.openbin(IMAGE_BASE, mode="rb") as b:
    with open("./SilverImagesDB.LE.bin", 'wb') as out:
        out.write(b.read())

# --- Export all SilverDB langs ---
os.makedirs("./Languages", exist_ok=True)

for lang in LANG_FILES:
    fs_path = f"/Resources/UI/{lang}.bin"
    local_path = f"./Languages/{lang}.bin"
    with fat.openbin(fs_path, mode="rb") as b:
        with open(local_path, "wb") as out:
            out.write(b.read())

# --- Export Sounds ---
os.makedirs("./Sounds", exist_ok=True)

for sound in sounds_list:
    fs_path = f"/Resources/Sounds/{sound}"
    local_path = f"./Sounds/{sound}"
    try:
        with fat.openbin(fs_path, mode="rb") as b:
            with open(local_path, "wb") as out:
                out.write(b.read())
        print(f"Extracted {sound}")
    except Exception as e:
        print(f"Error extracting {sound}: {e}")

# --- Replace fonts ---
for root, dirs, files in os.walk("./Fonts"):
    for file in files:
        if file.endswith(".ttf"):
            print("Processing " + file + "...")
            custom_ttf_path = os.path.join(root, file)
            system_ttf_path = os.path.join(FONT_BASE, file)
            try:
                # Read the original font name table
                with fat.openbin(system_ttf_path, mode="rb") as b:
                    original_font = ttLib.TTFont(b)
                    original_font_name_table = original_font["name"]

                fat.remove(system_ttf_path)

                # Record a replacement
                with fat.openbin(system_ttf_path, mode="wb") as b:
                    with open(custom_ttf_path, "rb") as f:
                        fake_font = ttLib.TTFont(f)
                        fake_font["name"] = original_font_name_table
                        print("Replacing " + file + "...")
                        fake_font.save(b)

            except Exception as e:
                print(f"An error occurred while opening {system_ttf_path}: {e}")

# --- Repack SilverImagesDB ---
if os.path.exists("./SilverImagesDB.LE.bin2"):
    fat.remove(IMAGE_BASE)
    with fat.openbin(IMAGE_BASE, mode="wb") as b, open("./SilverImagesDB.LE.bin2", "rb") as local_file:
        print("Replacing SilverImagesDB...")
        b.write(local_file.read())
else:
    print("Re-packed SilverImagesDB.LE.bin2 doesn't exist yet, extraction only")

# --- Repack SilverDB langs ---
for lang in LANG_FILES:
    local_bin2 = f"./Languages/{lang}.bin2"
    fs_path = f"/Resources/UI/{lang}.bin"
    if os.path.exists(local_bin2):
        fat.remove(fs_path)
        with fat.openbin(fs_path, mode="wb") as b, open(local_bin2, "rb") as local_file:
            print(f"Replacing {lang}...")
            b.write(local_file.read())
    else:
        print(f"Re-packed {lang}.bin2 doesn't exist yet, extraction only")
        
# --- Repack Sounds ---
for sound in sounds_list:
    local_new = f"./Sounds/{sound}.new"
    fs_path = f"/Resources/Sounds/{sound}"
    if os.path.exists(local_new):
        fat.remove(fs_path)
        with fat.openbin(fs_path, mode="wb") as b, open(local_new, "rb") as local_file:
            b.write(local_file.read())
        print(f"Replaced {sound}")
    else:
        print(f"No replacement for {sound}, keeping original")

fat.close()
