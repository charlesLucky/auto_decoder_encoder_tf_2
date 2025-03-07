import numpy as np
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '2, 3, 4, 5'
os.environ['TF_CPP_MIN_LOG_LEVEL']='3'# 只显示 Error
import logging
logging.disable(30)# for disable the warnning in gradient tape
import tensorflow as tf
from tensorflow.keras import Model, optimizers, layers, losses

from ModelZoo import createModel

num_epochs = 100000
batch_size = 32
# GLOBAL_BATCH_SIZE = batch_size * strategy.num_replicas_in_sync

learning_rate = 0.00001

model = createModel()
print(model.summary())
optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)


for epoch in range(num_epochs):
    # latents
    with tf.GradientTape() as tape:
        # seed = np.random.randint()
        rnd = np.random.RandomState()
        latents = rnd.randn(batch_size, 512)

        latents = tf.cast(latents, dtype=tf.float64)

        image_out, feature, new_latent = model(latents)

        new_latent = tf.cast(new_latent, dtype=tf.float64)
        new_image_out, new_feature, new_new_latent = model(new_latent)

        new_new_latent = tf.cast(new_new_latent, dtype=tf.float64)

        loss1 = tf.reduce_mean(losses.cosine_similarity(y_true=latents, y_pred=new_latent))
        loss1_2 = tf.reduce_mean( losses.cosine_similarity(y_true=new_new_latent, y_pred=new_latent))

        loss2 = tf.reduce_mean(losses.mae(image_out, new_image_out))

        loss3 = tf.reduce_mean(losses.cosine_similarity(feature, new_feature))
        # loss3 = tf.reduce_mean(loss3)

        latents = tf.cast(latents, dtype=tf.float64)

        loss = tf.cast(loss1, dtype=tf.float64)  + tf.cast(loss1_2, dtype=tf.float64)  + 0.01*tf.cast(loss2, dtype=tf.float64) + tf.cast(loss3, dtype=tf.float64)
        # loss = tf.reduce_mean(loss)
        # print("epoch %d: loss %f" % (epoch, loss1.numpy()))
        print("epoch %d: loss %f, loss1 %f,loss1_2 %f, loss2 %f, loss3 %f" % (epoch, loss.numpy(), loss1.numpy(),loss1_2.numpy(), loss2.numpy(), loss3.numpy()))
    grads = tape.gradient(loss, model.variables)
    optimizer.apply_gradients(grads_and_vars=zip(grads, model.variables))

    # if epoch % 2000 == 0:
    #     save_path = os.path.join('./models', f'step{epoch}')
    #     tf.saved_model.save(model, save_path)
