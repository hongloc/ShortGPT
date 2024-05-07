import os
import shutil

# Parent Directory path 
parent_dir = "/content/gdrive/My Drive/moneyprinter/shorts"

def save_short(youtube_path, title, description):
  global parent_dir
  name_file = youtube_path.split('/')[-1]
  # Path 
  path = os.path.join(parent_dir, name_file) 
  try: 
    os.makedirs(path, exist_ok = True) 
    print("Directory '%s' created successfully" % name_file) 
  except OSError as error: 
    print("Directory '%s' can not be created" % name_file)
  f = open(path + "/title-desc.txt", "w")
  f.write(title + '\n' + description)
  f.close()
  shutil.copyfile(youtube_path, path + '/' + name_file)