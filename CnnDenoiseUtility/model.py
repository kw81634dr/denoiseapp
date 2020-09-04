from keras.models import Model
from keras.layers import Input, Add, PReLU, Conv2DTranspose, Concatenate, MaxPooling2D, UpSampling2D, Dropout
from keras.layers.convolutional import Conv2D
from keras.layers.normalization import BatchNormalization
from keras.callbacks import Callback
from keras import backend as K
import tensorflow as tf

import numpy as np

class L0Loss:
    def __init__(self):
        self.gamma = K.variable(2.)

    def __call__(self):
        def calc_loss(y_true, y_pred):
            loss = K.pow(K.abs(y_true - y_pred) + 1e-8, self.gamma)
            return loss
        return calc_loss


class UpdateAnnealingParameter(Callback):
    def __init__(self, gamma, nb_epochs, verbose=0):
        super(UpdateAnnealingParameter, self).__init__()
        self.gamma = gamma
        self.nb_epochs = nb_epochs
        self.verbose = verbose

    def on_epoch_begin(self, epoch, logs=None):
        new_gamma = 2.0 * (self.nb_epochs - epoch) / self.nb_epochs
        K.set_value(self.gamma, new_gamma)

        if self.verbose > 0:
            print('\nEpoch %05d: UpdateAnnealingParameter reducing gamma to %s.' % (epoch + 1, new_gamma))


def tf_log10(x):
    numerator = tf.log(x)
    denominator = tf.log(tf.constant(10, dtype=numerator.dtype))
    return numerator / denominator


def PSNR(y_true, y_pred):
    max_pixel = 255.0
    y_pred = K.clip(y_pred, 0.0, 255.0)
    return 10.0 * tf_log10((max_pixel ** 2) / (K.mean(K.square(y_pred - y_true))))


#   #https://stackoverflow.com/questions/40666316/how-to-get-tensorflow-tensor-dimensions-shape-as-int-values
# def suggest_filter_size(image1_batch, image2_batch, power_factors, filter_size):
#     shape1 = (image1_batch.shape[1:-1])
#     shape2 = (image2_batch.shape[1:-1])
#     # num_rows_im1 = int(image1_batch.get_shape()[1])
#     # num_cols_im1 = int(image1_batch.get_shape()[2])
#     # num_rows_im2 = int(image2_batch.get_shape()[1])
#     # num_cols_im2 = int(image2_batch.get_shape()[2])
#     print('shape1,shape2', shape1, shape2)
#     if not (shape1[-3:-1][0] / (2 ** (len(power_factors) - 1)) and shape2[-3:-1][0] / (
#             2 ** (len(power_factors) - 1)) >= filter_size):
#         H = tf.math.reduce_min((shape1, shape2))
#         suggested_filter_size = int(H / (2 ** (len(power_factors) - 1)))
#     else:
#         suggested_filter_size = filter_size
#     return suggested_filter_size

#   #https://stackoverflow.com/questions/57357146/use-ssim-loss-function-with-keras
#   #https://stackoverflow.com/questions/57127626/error-in-calculation-of-inbuilt-ms-ssim-function-in-tensorflow
# Mean SSIM Loss function
def Mean_MSSSIM_loss(y_true, y_pred):
    power_factors = (0.0448, 0.2856, 0.3001, 0.2363, 0.1333)
    filter_size = 11  # default from tf.image.ssim_multiscale
    # new_filter_size = suggest_filter_size(y_true, y_pred, power_factors, filter_size)
    return 1 - (tf.reduce_mean(tf.image.ssim_multiscale(y_true, y_pred, max_val=1.0, filter_size=11)))


def MSSSIM(y_true, y_pred):
    power_factors = (0.0448, 0.2856, 0.3001, 0.2363, 0.1333)
    filter_size = 11  # default from tf.image.ssim_multiscale
    # new_filter_size = suggest_filter_size(y_true, y_pred, power_factors, filter_size)
    return tf.image.ssim_multiscale(y_true, y_pred, max_val=1.0, filter_size=11)


# calc SSIM
def SSIM(y_true, y_pred):
    return tf.image.ssim(y_true, y_pred, max_val=1.0)


def get_model(model_name="srresnet"):
    if model_name == "srresnet":
        return get_srresnet_model()
    elif model_name == "unet":
        return get_unet_model(out_ch=3)
    else:
        raise ValueError("model_name should be 'srresnet'or 'unet'")


# SRResNet
def get_srresnet_model(input_channel_num=3, feature_dim=64, resunit_num=16):
    def _residual_block(inputs):
        x = Conv2D(feature_dim, (3, 3), padding="same", kernel_initializer="he_normal")(inputs)
        x = BatchNormalization()(x)
        x = PReLU(shared_axes=[1, 2])(x)
        x = Conv2D(feature_dim, (3, 3), padding="same", kernel_initializer="he_normal")(x)
        x = BatchNormalization()(x)
        m = Add()([x, inputs])

        return m

    inputs = Input(shape=(None, None, input_channel_num))
    x = Conv2D(feature_dim, (3, 3), padding="same", kernel_initializer="he_normal")(inputs)
    x = PReLU(shared_axes=[1, 2])(x)
    x0 = x

    for i in range(resunit_num):
        x = _residual_block(x)

    x = Conv2D(feature_dim, (3, 3), padding="same", kernel_initializer="he_normal")(x)
    x = BatchNormalization()(x)
    x = Add()([x, x0])
    x = Conv2D(input_channel_num, (3, 3), padding="same", kernel_initializer="he_normal")(x)
    model = Model(inputs=inputs, outputs=x)

    return model


# UNet: code from https://github.com/pietz/unet-keras
def get_unet_model(input_channel_num=3, out_ch=3, start_ch=64, depth=4, inc_rate=2., activation='relu',
         dropout=0.5, batchnorm=False, maxpool=True, upconv=True, residual=False):
    def _conv_block(m, dim, acti, bn, res, do=0):
        n = Conv2D(dim, 3, activation=acti, padding='same')(m)
        n = BatchNormalization()(n) if bn else n
        n = Dropout(do)(n) if do else n
        n = Conv2D(dim, 3, activation=acti, padding='same')(n)
        n = BatchNormalization()(n) if bn else n

        return Concatenate()([m, n]) if res else n

    def _level_block(m, dim, depth, inc, acti, do, bn, mp, up, res):
        if depth > 0:
            n = _conv_block(m, dim, acti, bn, res)
            m = MaxPooling2D()(n) if mp else Conv2D(dim, 3, strides=2, padding='same')(n)
            m = _level_block(m, int(inc * dim), depth - 1, inc, acti, do, bn, mp, up, res)
            if up:
                m = UpSampling2D()(m)
                m = Conv2D(dim, 2, activation=acti, padding='same')(m)
            else:
                m = Conv2DTranspose(dim, 3, strides=2, activation=acti, padding='same')(m)
            n = Concatenate()([n, m])
            m = _conv_block(n, dim, acti, bn, res)
        else:
            m = _conv_block(m, dim, acti, bn, res, do)

        return m

    i = Input(shape=(None, None, input_channel_num))
    o = _level_block(i, start_ch, depth, inc_rate, activation, dropout, batchnorm, maxpool, upconv, residual)
    o = Conv2D(out_ch, 1)(o)
    model = Model(inputs=i, outputs=o)

    return model


def main():
    # model = get_model()
    model = get_model("unet")
    model.summary()


if __name__ == '__main__':
    main()
