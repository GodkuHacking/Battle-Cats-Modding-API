import os
import modder

# Original APK and assets
original_apk = 'battle.apk'
assets_dir = 'assets'
os.makedirs(assets_dir, exist_ok=True)

# Create test pack and list
battlecat_modder.encrypt_files(assets_dir, assets_dir) 

# Test patch file
with open('new_unit.bin', 'wb') as f:
  f.write(os.urandom(30))

# Mod APK  
pack_patch = [('new_unit.bin', 100, 30)]
modded_apk = 'modded.apk'

battlecat_modder.make_mod_apk(original_apk, assets_dir, pack_patch, modded_apk)

print('Modded APK created!')
