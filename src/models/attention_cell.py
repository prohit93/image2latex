import tensorflow as tf
import collections
from tensorflow.contrib.rnn import RNNCell, LSTMStateTuple


AttentionState = collections.namedtuple("AttentionState", ("cell_state", "o"))


class AttentionCell(RNNCell):
    def __init__(self, cell, attention_mechanism, dropout, attn_cell_config):
        """
        Args:
            training: (tf.placeholder) bool
            E: (tf.Variable) embeddings matrix
        """
        # variables and tensors
        self._cell                = cell
        self._attention_mechanism = attention_mechanism
        self._dropout             = dropout

        # hyperparameters and shapes
        self._n_channels     = self._attention_mechanism._n_channels
        self._batch_size     = self._attention_mechanism._batch_size
        self._dim_e          = attn_cell_config.get("dim_e", 512)
        self._dim_o          = attn_cell_config.get("dim_o", 512)
        self._num_units      = attn_cell_config.get("num_units", 512)
        self._num_proj       = attn_cell_config.get("num_proj", 512)
        self._dim_embeddings = attn_cell_config.get("dim_embeddings", 512)
        
        # for RNNCell
        self._state_size = AttentionState(self._cell._state_size, self._dim_o)


    @property
    def state_size(self):
        return self._state_size


    @property
    def output_size(self):
        return self._num_proj


    def initial_state(self):
        """
        Return initial state for the lstm
        """
        initial_cell_state = self._attention_mechanism.initial_cell_state(self._cell)
        initial_o          = self._attention_mechanism.initial_state("o", self._dim_o)

        return AttentionState(initial_cell_state, initial_o)


    def step(self, embedding, attn_cell_state):
        """
        Args:
            embedding: shape =  (batch, dim_embeddings) embeddings
                from previous time step
            state: hidden state from previous time step
        """
        prev_cell_state, o = attn_cell_state

        scope = tf.get_variable_scope()
        with tf.variable_scope(scope):
            # compute new h
            x                     = tf.concat([embedding, o], axis=-1)
            new_h, new_cell_state = self._cell.__call__(x, prev_cell_state)
            new_h = tf.nn.dropout(new_h, self._dropout)

            # compute attention
            c = self._attention_mechanism.context(new_h)

            # compute o
            o_W_c   = tf.get_variable("o_W_c", shape=(self._n_channels, self._dim_o), dtype=tf.float32)
            o_W_h   = tf.get_variable("o_W_h", shape=(self._num_units, self._dim_o), dtype=tf.float32)

            new_o = tf.tanh(tf.matmul(new_h, o_W_h) + tf.matmul(c, o_W_c))
            new_o = tf.nn.dropout(new_o, self._dropout)

            # new_o = new_h
            y_W_o  = tf.get_variable("y_W_o", shape=(self._dim_o, self._num_proj), dtype=tf.float32)
            new_y  = tf.matmul(new_o, y_W_o)

            # new Attn cell state
            new_state = AttentionState(new_cell_state, new_o)

            return new_state, new_y


    def __call__(self, embedding, state):
        """
        Args:
            inputs: the embedding of the previous word for training only
            state: tuple: (h, o) where h is the hidden state and o is the vector 
                used to make the prediction of the previous word
        """
        new_state, new_y = self.step(embedding, state)
        
        return (new_y, new_state)   