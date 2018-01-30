import tensorflow as tf
import numpy as np


y_true = tf.random_normal([64,5],mean=1,stddev=1.0)
y_target = tf.ones([64,5],tf.int32)
pred = tf.random_normal([64,100],mean=1,stddev=1.0)


x = tf.random_normal([64,100],mean=1,stddev=1.0)
W = tf.random_normal([100,5],mean=1,stddev=1.0)

# inf = x*W
inf = tf.matmul(x,W)
print inf.shape
# print y_true.shape
# print pred


with tf.Session() as sess:
    print sess.run(inf)


def cross_entropy_loss(y, yhat):
    ### YOUR CODE HERE
    out1 = -tf.to_float(y)* tf.log(yhat)
    # out1 = tf.tensordot(-tf.to_float(y),tf.log(yhat),axes=1)
    out = tf.reduce_sum(out1)

    ### END YOUR CODE

    return out

