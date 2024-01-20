import os
from Cryptodome.Cipher import AES
from alive_progress import alive_bar
import shutil
import csv
import hashlib

def make_mod_apk(original_apk, mod_files_dir, pack_patch, output_apk):

  # Extract original APK
  temp_dir = 'temp_modding'  
  os.makedirs(temp_dir, exist_ok=True)
  shutil.unpack_archive(original_apk, temp_dir)

  # Apply pack patch
  assets_dir = os.path.join(temp_dir, 'assets')
  original_pack = os.path.join(assets_dir, 'files.pack')
  patched_pack = os.path.join(assets_dir, 'files_modded.pack')
  patch_pack(original_pack, pack_patch, patched_pack)

  # Copy over other mod files
  shutil.copytree(mod_files_dir, assets_dir)

  # Rebuild patched APK
  shutil.make_archive(output_apk, 'zip', temp_dir)  

  # Clean up
  shutil.rmtree(temp_dir)
    
def decrypt_files(pack_files, output_dir):
    """Decrypts Battle Cats pack files and extracts contents."""
    
    os.makedirs(output_dir, exist_ok=True)
    
    file_groups = find_lists(pack_files)
    
    for group in file_groups:
        ls_data = unpack_list(group['list'])
        unpack_pack(group['pack'], ls_data, output_dir)
        
def encrypt_files(input_dir, output_dir):
    """Encrypts files from input dir into pack files."""
    
    os.makedirs(output_dir, exist_ok=True)
    
    list_data = create_list(input_dir)
    list_file = os.path.join(output_dir, 'files.list')
    with open(list_file, 'wb') as f:
        f.write(encrypt_list(list_data))
    
    pack_data = create_pack(input_dir, list_data)
    pack_file = os.path.join(output_dir, 'files.pack')
    with open(pack_file, 'wb') as f:
        f.write(pack_data)
        
def make_mod_apk(original_apk, mod_files_dir, output_apk):
    """Creates modded APK with encrypted mod files."""
    
    temp_dir = 'temp_modding'
    os.makedirs(temp_dir, exist_ok=True)
    
    # Extract original APK
    shutil.unpack_archive(original_apk, temp_dir)  
    
    # Copy mod files into assets
    assets_dir = os.path.join(temp_dir, 'assets')
    shutil.copytree(mod_files_dir, assets_dir)
    
    # Rebuild APK
    shutil.make_archive(output_apk.replace('.apk', ''), 'zip', temp_dir)
    
    # Clean up
    shutil.rmtree(temp_dir)

def find_lists(pack_files):
    lists = []
    for pack in pack_files:
        list_file = pack.replace('.pack', '.list')
        if os.path.exists(list_file):
            lists.append({'pack': pack, 'list': list_file})
    return lists

def unpack_list(list_file):
    with open(list_file, 'rb') as f:
        data = f.read()
        
    key = AES.new(b'pack', AES.MODE_ECB)
    decrypted = key.decrypt(data)
    return decrypted

def unpack_pack(pack_file, list_data, output_dir):
    rows = list_data.decode().split('\n')
    reader = csv.reader(rows, delimiter=',', quotechar='"')
    pack_data = open(pack_file, 'rb').read()
    
    for row in reader:
        name, offset, size = row
        chunk = pack_data[int(offset):int(offset)+int(size)]
        out_path = os.path.join(output_dir, name)
        
        with open(out_path, 'wb') as f:
            f.write(chunk)
            
def create_list(files_dir):
    rows = []
    for name in os.listdir(files_dir):
        path = os.path.join(files_dir, name)
        size = os.path.getsize(path)
        rows.append(f'{name},{len(rows)},{size}')
    return '\n'.join(rows).encode()
    
def create_pack(files_dir, list_data):
    rows = list_data.decode().split('\n')
    pack_data = bytearray()
    
    for row in csv.reader(rows):
        name, offset, size = row
        path = os.path.join(files_dir, name)
        data = open(path, 'rb').read()
        pack_data[int(offset):int(offset)+int(size)] = data
        
    return pack_data
    
def encrypt_list(list_data):
    key = AES.new(b'pack', AES.MODE_ECB)
    return key.encrypt(list_data)


def encrypt_file(file_data, jp=False, name=""):
  aes_mode = AES.MODE_CBC
  
  if jp:
    key = bytes.fromhex("d754868de89d717fa9e7b06da45ae9e3") 
    iv = bytes.fromhex("40b2131a9f388ad4e5002a98118f6128")
  else:
    key = bytes.fromhex("0ad39e4aeaf55aa717feb1825edef521")
    iv = bytes.fromhex("d1d7e708091941d90cdf8aa5f30bb0c2")

  if "server" in name.lower():
      key = md5_hash("battlecats") 
      iv = None
      aes_mode = AES.MODE_ECB

  cipher = AES.new(key, aes_mode, iv=iv)
  encrypted = cipher.encrypt(file_data)

  return encrypted

def md5_hash(text):
  hash_obj = hashlib.md5()
  hash_obj.update(text.encode('utf-8'))
  return hash_obj.digest()
