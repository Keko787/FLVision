#########################################################
#    Imports / Env setup                                #
#########################################################

import os
import flwr as fl
import tensorflow as tf

#########################################################
#    Initialization                                     #
#########################################################

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Creates the train and test dataset from calling cifar10 in TF
(x_train, y_train), (x_test, y_test) = tf.keras.datasets.cifar10.load_data()

# initialize model with TF and keras
model = tf.keras.applications.MobileNetV2((32, 32, 3), classes=10, weights=None)
model.compile(optimizer='adam',
              loss=tf.keras.losses.sparse_categorical_crossentropy,
              metrics=['accuracy'])

#########################################################
#    Federated Learning Setup                           #
#########################################################

class FLClient(fl.client.NumPyClient):
    def get_parameters(self, config):
        return model.get_weights()

    def fit(self, parameters, config):
        model.set_weights(parameters)
        model.fit(x_train, y_train, epochs=1, batch_size=32, steps_per_epoch=3)
        return model.get_weights(), len(x_train), {}

    def evaluate(self, parameters, config):
        model.set_weights(parameters)
        loss, accuracy = model.evaluate(x_test, y_test)
        return loss, len(x_test), {"accuracy": float(accuracy)}

#########################################################
#    Start the client                                   #
#########################################################

fl.client.start_client(server_address="server:8080", client=FLClient().to_client())