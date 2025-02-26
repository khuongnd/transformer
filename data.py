import io
import numpy as np
import unicodedata
import tensorflow as tf
import re
import os
from sklearn.model_selection import train_test_split
from constant import *
import pickle

class NMTDataset:
  def __init__(self, inp_lang, targ_lang, vocab_folder):
    self.inp_lang = inp_lang
    self.targ_lang = targ_lang
    self.inp_tokenizer = None
    self.target_tokenizer = None
    self.vocab_folder = vocab_folder

  def preprocess_sentence(self, w, max_length):
    w = w.lower().strip()
    w = re.sub(r"([?.!,¿])", r" \1 ", w)
    w = re.sub(r'[" "]+', " ", w)
    w = w.strip()

    # Truncate Length up to ideal_length
    w = " ".join(w.split()[:max_length+1])
    # Add start and end token 
    w = '{} {} {}'.format(BOS, w, EOS)
    return w

  def tokenize(self, lang, max_length):
    # TODO: Update document
    lang_tokenizer = tf.keras.preprocessing.text.Tokenizer(filters='')
    lang_tokenizer.fit_on_texts(lang)

    # Padding

    tensor = lang_tokenizer.texts_to_sequences(lang)
    tensor = tf.keras.preprocessing.sequence.pad_sequences(tensor, padding='post', maxlen=max_length)
    return tensor, lang_tokenizer

  def display_samples(self, num_of_pairs, inp_lines, targ_lines):
    # TODO: Update document
    pairs = zip(inp_lines[:num_of_pairs], targ_lines[:num_of_pairs])
    print('=============Sample Data================')
    print('----------------Begin--------------------')
    for i, pair in enumerate(pairs):
      inp, targ = pair
      print('--> Sample {}:'.format(i + 1))
      print('Input: ', inp)
      print('Target: ', targ)

    print('----------------End--------------------')

  def load_dataset(self, inp_path, targ_path, max_length, num_examples):
    # TODO: Update document
    inp_lines = io.open(inp_path, encoding=UTF_8).read().strip().split('\n')[:num_examples]
    targ_lines = io.open(targ_path, encoding=UTF_8).read().strip().split('\n')[:num_examples]
    
    inp_lines = [self.preprocess_sentence(inp, max_length) for inp in inp_lines]
    targ_lines = [self.preprocess_sentence(targ, max_length) for targ in targ_lines]

    # Display 10 pairs
    self.display_samples(3, inp_lines, targ_lines)
    
    # Tokenizing
    inp_tensor, inp_tokenizer = self.tokenize(inp_lines, max_length)
    targ_tensor, targ_tokenizer = self.tokenize(targ_lines, max_length)


    # Saving Tokenizer
    print('=============Saving Tokenizer================')
    print('Begin...')

    if not os.path.exists(self.vocab_folder):
      try:
        os.makedirs(self.vocab_folder)
      except OSError as exc: 
        raise IOError("Failed to create folders")

    with open('{}{}_tokenizer.pickle'.format(self.vocab_folder, self.inp_lang), 'wb') as handle:
      pickle.dump(inp_tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)

    with open('{}{}_tokenizer.pickle'.format(self.vocab_folder, self.targ_lang), 'wb') as handle:
      pickle.dump(targ_tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)

    print('Done!!!')

    return inp_tensor, targ_tensor, inp_tokenizer, targ_tokenizer

  def build_dataset(self, inp_path, targ_path, buffer_size, batch_size, max_length, num_examples):
    # TODO: Update document

    inp_tensor, targ_tensor, self.inp_tokenizer, self.targ_tokenizer = self.load_dataset(inp_path, targ_path, max_length, num_examples)

    inp_tensor_train, inp_tensor_val, targ_tensor_train, targ_tensor_val = train_test_split(inp_tensor, targ_tensor, test_size=0.2)

    train_dataset = tf.data.Dataset.from_tensor_slices((tf.convert_to_tensor(inp_tensor_train, dtype=tf.int64), tf.convert_to_tensor(targ_tensor_train, dtype=tf.int64)))

    train_dataset = train_dataset.shuffle(buffer_size).batch(batch_size)

    val_dataset = tf.data.Dataset.from_tensor_slices((tf.convert_to_tensor(inp_tensor_val, dtype=tf.int64), tf.convert_to_tensor(targ_tensor_val, dtype=tf.int64)))

    val_dataset = val_dataset.shuffle(buffer_size).batch(batch_size)

    return train_dataset, val_dataset


