"""
This test ensures that Python distributions which have purelib like numpy
work file
"""

import tensorflow as tf
from tensorflow.contrib import learn

def test_numpy():
    assert tf != None
    assert learn != None
    print(tf.VERSION)