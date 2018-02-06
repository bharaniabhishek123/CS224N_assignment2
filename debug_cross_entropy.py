import tensorflow as tf
import numpy as np


y_true = tf.random_normal([64,5],mean=1,stddev=1.0)
y_target = tf.ones([64,5],tf.int32)
pred = tf.random_normal([64,100],mean=1,stddev=1.0)


x = tf.random_normal([64,100],mean=1,stddev=1.0)
W = tf.random_normal([100,5],mean=1,stddev=1.0)

# # How reshaping works ?
# embeddings = tf.random_normal([3,4,5],mean=1,stddev=1.0)
#
# reshaped_embeddings = tf.reshape(embeddings,[-1,20])
#
# reshaped_embeddings1 = tf.reshape(embeddings,[3,20])
#
#
# assert reshaped_embeddings.shape==reshaped_embeddings1.shape
#
#
# print "Shape of original embeddings: ",format(embeddings.shape)
#
# print "Shape of reshaped embeddings: ",format(reshaped_embeddings.shape)
#
# with tf.Session() as sess:
#     print sess.run(embeddings)
#
# # End of reshaping code


#How softmax_cross_entropy_with_logits works ?


# # pred: A tensor of shape (batch_size, n_classes) containing the output of the neural
# #                   network before the softmax layer.
#
#
# y = tf.constant([[0, 1], [1, 0], [1, 0]])
# yhat = tf.constant([[.5, .5], [.5, .5], [.5, .5]])
#
# expected = -3 * tf.log(.5)
#
# out1 = tf.nn.softmax_cross_entropy_with_logits(labels=y,logits=yhat)
# out2 = tf.reduce_sum(out1)
#
# with tf.Session() as sess:
#     print sess.run(out1)
#     print sess.run(out2)
#     print sess.run(expected)
#
#
# # End of softmax_cross_entropy_with_logits


import pickle


with open('q2_test.predicted.pkl', 'rb') as f:
    data = pickle.load(f)
    print  len(data)
#
# tp = (2,3)
#
# print np.sum(tp)
#
# # inf = x*W
# inf = tf.matmul(x,W)
# print inf.shape
# # print y_true.shape
# # print pred
#
#
# with tf.Session() as sess:
#     print sess.run(inf)
#
#
# def cross_entropy_loss(y, yhat):
#     ### YOUR CODE HERE
#     out1 = -tf.to_float(y)* tf.log(yhat)
#     # out1 = tf.tensordot(-tf.to_float(y),tf.log(yhat),axes=1)
#     out = tf.reduce_sum(out1)
#
#     ### END YOUR CODE
#
#     return out

