import numpy as np
import tensorflow as tf
import tensorflow.contrib.layers as layers
from tensorflow.contrib.rnn import GRUCell, LSTMCell
from .dynamic_decode import dynamic_decode
from .attention_mechanism import AttentionMechanism
from .attention_cell import AttentionCell
from .greedy_decoder_cell import GreedyDecoderCell
from .beam_search_decoder_cell import BeamSearchDecoderCell


class Decoder(object):
    """
    Implements this paper https://arxiv.org/pdf/1609.04938.pdf
    """
    def __init__(self, config):
        self.config = config


    def __call__(self, training, encoded_img, formula, dropout):
        """
        Args:
            training: (tf.placeholder) bool
            encoded_img: (tf.Tensor) shape = (N, H, W, C)
            formula: (tf.placeholder), shape = (N, T)
        Returns:
            pred_train: (tf.Tensor), shape = (?, ?, vocab_size) logits of each class
            pret_test: (structure) 
                - pred.test.logits, same as pred_train
                - pred.test.ids, shape = (?, config.max_length_formula)
        """
        # get embeddings for training
        
        if self.config.embeddings_init = "pretrained":
            npz_file = np.load(self.config.path_embeddings)
            embeddings = npz_file["arr-0"]
            assert(embeddings.shape == [self.config.vocab_size, self.config.dim_embeddings])
            E = tf.get_variable("E", shape=embeddings.shape,
                                  dtype=tf.float32,
                                  initializer=tf.constant_initializer(embeddings),
                                  trainable=self.config.trainable_embeddings)
        else:
            E = tf.get_variable("E", shape=[self.config.vocab_size, self.config.dim_embeddings], 
            dtype=tf.float32, initializer=tf.random_uniform_initializer(minval=-1.0, maxval=1.0))

        start_token = tf.get_variable("start_token", shape=[self.config.dim_embeddings],
            dtype=tf.float32, initializer=tf.random_uniform_initializer(minval=-1.0, maxval=1.0))

        # embedding with start token
        batch_size        = tf.shape(formula)[0]
        embedding_formula = tf.nn.embedding_lookup(E, formula)
        start_token_      = tf.reshape(start_token, [1, 1, self.config.dim_embeddings])
        start_tokens      = tf.tile(start_token_, multiples=[batch_size, 1, 1])
        embedding_train   = tf.concat([start_tokens, embedding_formula[:, :-1, :]], axis=1) 

        # attention mechanism
        attention_mechanism = AttentionMechanism(encoded_img, self.config.attn_cell_config["dim_e"])

        # attention cell
        with tf.variable_scope("attn_cell", reuse=False):
            cell      = LSTMCell(self.config.attn_cell_config["num_units"])
            attn_cell = AttentionCell(cell, attention_mechanism, dropout, self.config.attn_cell_config)
            train_outputs, _ = tf.nn.dynamic_rnn(attn_cell, embedding_train, initial_state=attn_cell.initial_state())

        with tf.variable_scope("attn_cell", reuse=True):
            cell         = LSTMCell(self.config.attn_cell_config["num_units"], reuse=True)
            attn_cell    = AttentionCell(cell, attention_mechanism, dropout, self.config.attn_cell_config)

            if self.config.decoding == "greedy":
                decoder_cell = GreedyDecoderCell(E, attn_cell, batch_size, start_token)
                
            elif self.config.decoding == "beam_search":
                decoder_cell = BeamSearchDecoderCell(E, attn_cell, batch_size, 
                        start_token, self.config.beam_size, self.config.id_END)
            else:
                print("Unknown decoding option {} - use `greedy` or `beam_search`".format(self.config.decoding))
                raise NotImplementedError

            test_outputs, _ = dynamic_decode(decoder_cell, self.config.max_length_formula+1)
        
        return train_outputs, test_outputs