import zipfile 
import json 

def extract_zip_contents(filename):
    names = []
    files_wanted = ["data/tweets.js", "data/like.js"]
    try:
        file = zipfile.ZipFile(filename)
        data = []
        for name in file.namelist():
            if name in files_wanted:
                # z.read, then json.dumps 

                names.append(name)
                info = file.getinfo(name)
                data.append((name, info.compress_size, info.file_size)) 
        return data
    except zipfile.error:
        return "invalid"