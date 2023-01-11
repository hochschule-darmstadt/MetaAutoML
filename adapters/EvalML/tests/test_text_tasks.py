import json
import os
import shutil
import unittest
from unittest import IsolatedAsyncioTestCase
import uuid
import urllib.request

import tarfile
import evalml


import pandas as pd
from EvalMLAdapterManager import EvalMLAdapterManager
from Container import *
from AdapterBGRPC import *

# i was trying to use request modul for downloading dataset and then extract but encounter permission denied error

def load_aclImdb_dataset():
    """download titanic dataset
    Returns:
        path of reduced dataset csv
    """
    target_dir = os.path.join("tests", "datasets")
    os.makedirs(target_dir, exist_ok=True)
    # using cache dir to avoid multiple times download
    if (os.path.exists(os.path.join(target_dir,"aclImdb_v1.tar.gz")) == False):
        url = "http://ai.stanford.edu/~amaas/data/sentiment/aclImdb_v1.tar.gz"
        dataX = urllib.request.urlopen(url).read()
        urllib.request.urlretrieve(url,os.path.join(target_dir,"aclImdb_v1.tar.gz"))
    
    # chekc if the  tar gz file is extracted already
    if ((os.path.exists(os.path.join(target_dir,"aclImdb")) == False)):
        file = tarfile.open(os.path.join(target_dir,"aclImdb_v1.tar.gz"))
        file.extractall(os.path.join(target_dir))
        file.close()
    
    train_data: pd.DataFrame = evalml.preprocessing.load_data(
        os.path.join(target_dir,"aclImdb", "train"),
    )
    print(train_data)

    return True

class TestAdapter(IsolatedAsyncioTestCase):
    
    async def test_text_classification(self):
        dataset_path = load_aclImdb_dataset()
        # setup request as it is coming in from controller
        
    
        
if __name__ == '__main__':
    unittest.main()

