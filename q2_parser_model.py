import cPickle
import os
import time
import tensorflow as tf

from model import Model
from q2_initialization import xavier_weight_init
from utils.parser_utils import minibatches, load_and_preprocess_data


class Config(object):
    """Holds model hyperparams and data information.

    The config class is used to store various hyperparameters and dataset
    information parameters. Model objects are passed a Config() object at
    instantiation. They can then call self.config.<hyperparameter_name> to
    get the hyperparameter settings.
    """
    n_features = 36
    n_classes = 3
    dropout = 0.50  # (p_drop in the handout)
    embed_size = 50
    hidden_size = 200
    batch_size = 1024
    n_epochs = 10
    lr = 0.0005
    None1 = None
    # beta = 0.01 # to be used in regularization
    # extension_on =False


class ParserModel(Model):
    """
    Implements a feedforward neural network with an embedding layer and single hidden layer.
    This network will predict which transition should be applied to a given partial parse
    configuration.
    """

    def add_placeholders(self):
        """Generates placeholder variables to represent the input tensors

        These placeholders are used as inputs by the rest of the model building and will be fed
        data during training.  Note that when "None" is in a placeholder's shape, it's flexible
        (so we can use different batch sizes without rebuilding the model).

        Adds following nodes to the computational graph

        input_placeholder: Input placeholder tensor of  shape (None, n_features), type tf.int32
        labels_placeholder: Labels placeholder tensor of shape (None, n_classes), type tf.float32
        dropout_placeholder: Dropout value placeholder (scalar), type tf.float32

        Add these placeholders to self as the instance variables
            self.input_placeholder
            self.labels_placeholder
            self.dropout_placeholder

        (Don't change the variable names)
        """
        ### YOUR CODE HERE
        cn = Config()

        self.input_placeholder = tf.placeholder(tf.int32,shape=(None,cn.n_features))
        self.labels_placeholder = tf.placeholder(tf.float32,shape=(None,cn.n_classes))
        # self.droupout_placeholder = tf.placeholder(tf.float32,cn.dropout)
        # self.dropout_placeholder = tf.constant(cn.dropout,tf.float32)
        self.dropout_placeholder = tf.placeholder(tf.float32) # change done to match B
        ### END YOUR CODE

    def create_feed_dict(self, inputs_batch, labels_batch=None, dropout=0):
        """Creates the feed_dict for the dependency parser.

        A feed_dict takes the form of:

        feed_dict = {
                <placeholder>: <tensor of values to be passed for placeholder>,
                ....
        }


        Hint: The keys for the feed_dict should be a subset of the placeholder
                    tensors created in add_placeholders.
        Hint: When an argument is None, don't add it to the feed_dict.

        Args:
            inputs_batch: A batch of input data.
            labels_batch: A batch of label data.
            dropout: The dropout rate.
        Returns:
            feed_dict: The feed dictionary mapping from placeholders to values.
        """
        ### YOUR CODE HERE
        feed_dict = dict()

        feed_dict[self.input_placeholder] = inputs_batch
        feed_dict[self.dropout_placeholder] = dropout
        if labels_batch is not None:
            feed_dict[self.labels_placeholder] = labels_batch
        ### END YOUR CODE
        return feed_dict

    def add_embedding(self):
        """Adds an embedding layer that maps from input tokens (integers) to vectors and then
        concatenates those vectors:
            - Creates a tf.Variable and initializes it with self.pretrained_embeddings.
            - Uses the input_placeholder to index into the embeddings tensor, resulting in a
              tensor of shape (None, n_features, embedding_size).
            - Concatenates the embeddings by reshaping the embeddings tensor to shape
              (None, n_features * embedding_size).

        Hint: You might find tf.nn.embedding_lookup useful.
        Hint: You can use tf.reshape to concatenate the vectors. See following link to understand
            what -1 in a shape means.
            https://www.tensorflow.org/api_docs/python/tf/reshape

        Returns:
            embeddings: tf.Tensor of shape (None, n_features*embed_size)
        """
        ### YOUR CODE HERE
        cn =Config()
        # embeddings = tf.zeros(shape=(None,cn.n_features*cn.embed_size))
        # embeddings = tf.get_variable("embedding_matrix", shape=(None,cn.n_features*cn.embed_size),initializer=self.pretrained_embeddings)

        embed = tf.get_variable("embeding_matrix",initializer=self.pretrained_embeddings)

        temp = tf.nn.embedding_lookup(embed,self.input_placeholder)

        # print "output shape from embedding_lookup",format(temp.shape)
        # print "shape of embed variable",format(embed.shape)
        # print "shape of embeddings",format(self.pretrained_embeddings.shape)
        # print "shape of input place holder",format(self.input_placeholder.shape)

        #Learnings from tf.reshape
        # we cannot pass tf.reshape(temp,(None,cn.n_features*cn.embed_size))
        # TypeError: Failed to convert object of type <type 'tuple'> to Tensor. Contents: (None, 1800). Consider casting elements to a supported type.
        # solution : Use -1 to act as a place holder
        # Let's say original matrix of size(3,4,5) and we reshape into matrix of size(-1,20) -1 will be inferred as 3


        embeddings= tf.reshape(temp,(-1,cn.n_features*cn.embed_size))
        # embeddings= tf.reshape(temp,[-1,cn.n_features*cn.embed_size]) # changed to match B


        # print  embeddings.shape
        ### END YOUR CODE
        return embeddings

    def add_prediction_op(self):
        """Adds the 1-hidden-layer NN:
            h = Relu(xW + b1)
            h_drop = Dropout(h, dropout_rate)
            pred = h_dropU + b2

        Note that we are not applying a softmax to pred. The softmax will instead be done in
        the add_loss_op function, which improves efficiency because we can use
        tf.nn.softmax_cross_entropy_with_logits

        Use the initializer from q2_initialization.py to initialize W and U (you can initialize b1
        and b2 with zeros)

        Hint: Note that tf.nn.dropout takes the keep probability (1 - p_drop) as an argument.
              Therefore the keep probability should be set to the value of
              (1 - self.dropout_placeholder)

        Returns:
            pred: tf.Tensor of shape (batch_size, n_classes)
        """

        x = self.add_embedding()

        ### YOUR CODE HERE
        cn = Config()
        W = tf.get_variable("Weights_Layer1", shape=(cn.n_features*cn.embed_size,cn.hidden_size)
                            ,initializer=xavier_weight_init())#cn.n_features*cn.embed_size,cn.hidden_size))
        b1 = tf.get_variable("bias_Layer1",shape=(1,cn.hidden_size),initializer=tf.zeros_initializer)

        # print "Dimension of W",format(W.shape)
        # print "Dimension of b1",format(b1.shape)
        # print "Dimension of x",format(x.shape)
        #
        # print "xW multiplication shape",format(tf.matmul(x,W).shape)


        h = tf.nn.relu(tf.matmul(x,W)+b1)

        h_drop = tf.nn.dropout(h,1.0-self.dropout_placeholder)
        U = tf.get_variable("Weights_Layer2", shape=(cn.hidden_size,cn.n_classes)
                            ,initializer=xavier_weight_init())#cn.hidden_size,cn.n_classes))
        b2 = tf.get_variable("bias_Layer2",shape=(1,cn.n_classes),initializer=tf.zeros_initializer)

        # print "Dimension of h", format(h.shape)
        # print "Dimension of h_drop", format(h_drop.shape)
        # print "Dimension of U", format(U.shape)
        # print "Dimension of b2", format(b2.shape)
        #
        # print "h_drop U multiplication shape", format(tf.matmul(h_drop, U).shape)

        pred = tf.matmul(h_drop,U) + b2

        ### END YOUR CODE

        return pred

    def add_loss_op(self, pred):
        """Adds Ops for the loss function to the computational graph.
        In this case we are using cross entropy loss.
        The loss should be averaged over all examples in the current minibatch.

        Hint: You can use tf.nn.softmax_cross_entropy_with_logits to simplify your
                    implementation. You might find tf.reduce_mean useful.
        Args:
            pred: A tensor of shape (batch_size, n_classes) containing the output of the neural
                  network before the softmax layer.
        Returns:
            loss: A 0-d tensor (scalar)
        """
        ### YOUR CODE HERE
        out1 = tf.nn.softmax_cross_entropy_with_logits(labels=self.labels_placeholder, logits=pred)

        loss = tf.reduce_mean(out1)

        # Add L2 regularization
        # Loss function using L2 Regularization
        # regularizer = tf.nn.l2_loss(weights)
        # loss = tf.reduce_mean(loss + beta * regularizer)
        ### END YOUR CODE

        return loss

    def add_training_op(self, loss):
        """Sets up the training Ops.

        Creates an optimizer and applies the gradients to all trainable variables.
        The Op returned by this function is what must be passed to the
        `sess.run()` call to cause the model to train. See

        https://www.tensorflow.org/api_docs/python/tf/train/Optimizer

        for more information.

        Use tf.train.AdamOptimizer for this model.
        Use the learning rate from self.config.
        Calling optimizer.minimize() will return a train_op object.

        Args:
            loss: Loss tensor, from cross_entropy_loss.
        Returns:
            train_op: The Op for training.
        """
        ### YOUR CODE HERE
        train_op = tf.train.AdamOptimizer(learning_rate=self.config.lr).minimize(loss)
        ### END YOUR CODE
        return train_op

    def train_on_batch(self, sess, inputs_batch, labels_batch):
        feed = self.create_feed_dict(inputs_batch, labels_batch=labels_batch,
                                     dropout=self.config.dropout)
        _, loss = sess.run([self.train_op, self.loss], feed_dict=feed)
        return loss

    def run_epoch(self, sess, parser, train_examples, dev_set):
        n_minibatches = 1 + len(train_examples) / self.config.batch_size
        prog = tf.keras.utils.Progbar(target=n_minibatches)
        for i, (train_x, train_y) in enumerate(minibatches(train_examples, self.config.batch_size)):
            loss = self.train_on_batch(sess, train_x, train_y)
            prog.update(i + 1, [("train loss", loss)], force=i + 1 == n_minibatches)

        print "Evaluating on dev set",
        dev_UAS, _ = parser.parse(dev_set)
        print "- dev UAS: {:.2f}".format(dev_UAS * 100.0)
        return dev_UAS

    def fit(self, sess, saver, parser, train_examples, dev_set):
        best_dev_UAS = 0
        for epoch in range(self.config.n_epochs):
            print "Epoch {:} out of {:}".format(epoch + 1, self.config.n_epochs)
            dev_UAS = self.run_epoch(sess, parser, train_examples, dev_set)
            if dev_UAS > best_dev_UAS:
                best_dev_UAS = dev_UAS
                if saver:
                    print "New best dev UAS! Saving model in ./data/weights/parser.weights"
                    saver.save(sess, './data/weights/parser.weights')
            print

    def __init__(self, config, pretrained_embeddings):
        self.pretrained_embeddings = pretrained_embeddings
        self.config = config
        self.build()



def main(debug=False):
    print 80 * "="
    print "INITIALIZING"
    print 80 * "="
    config = Config()
    parser, embeddings, train_examples, dev_set, test_set = load_and_preprocess_data(debug)
    if not os.path.exists('./data/weights/'):
        os.makedirs('./data/weights/')


    with tf.Graph().as_default() as graph:
        print "Building model...",
        start = time.time()
        model = ParserModel(config, embeddings)
        parser.model = model
        init_op = tf.global_variables_initializer()
        saver = None if debug else tf.train.Saver()
        print "took {:.2f} seconds\n".format(time.time() - start)
    graph.finalize()


    with tf.Session(graph=graph) as session:
        parser.session = session
        session.run(init_op)

        print 80 * "="
        print "TRAINING"
        print 80 * "="
        model.fit(session, saver, parser, train_examples, dev_set)

        if not debug:
            print 80 * "="
            print "TESTING"
            print 80 * "="
            print "Restoring the best model weights found on the dev set"
            saver.restore(session, './data/weights/parser.weights')
            print "Final evaluation on test set",
            UAS, dependencies = parser.parse(test_set)
            print "- test UAS: {:.2f}".format(UAS * 100.0)
            print "Writing predictions"
            with open('q2_test.predicted.pkl', 'w') as f:
                cPickle.dump(dependencies, f, -1)
            print "Done!"


if __name__ == '__main__':
    main()

