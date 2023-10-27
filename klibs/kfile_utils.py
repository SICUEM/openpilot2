######################
# carlos@iglesias.io #
# 27/10/2023         #
######################

# File utils


import urllib.request


# Try to get file from url and 
# save it
def get_from_url_and_save(file_url: str, file_dst_path: str):
    urllib.request.urlretrieve(file_url, file_dst_path)
