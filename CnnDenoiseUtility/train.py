import os
import argparse
import numpy as np
from pathlib import Path
from keras.callbacks import LearningRateScheduler, ModelCheckpoint, EarlyStopping, TensorBoard, TerminateOnNaN, \
    CSVLogger
from keras.optimizers import Adam, Adamax
from model import get_model, PSNR, L0Loss, UpdateAnnealingParameter
from generator import NoisyImageGenerator, ValGenerator
from noise_model import get_noise_model
from keras.utils import plot_model
from math import exp
from model import Mean_MSSSIM_loss, SSIM, MSSSIM
import time
from datetime import timedelta
import tensorflow as tf
import json
from keras import backend as K
from keras.callbacks import TensorBoard


class LRTensorBoard(TensorBoard):
    def __init__(self, log_dir, **kwargs):  # add other arguments to __init__ if you need
        super().__init__(log_dir=log_dir, **kwargs)

    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        logs.update({'lr': K.eval(self.model.optimizer.lr)})
        super().on_epoch_end(epoch, logs)


class MyStepwiseScheduler:
    def __init__(self, nb_epochs, initial_lr):
        self.epochs = nb_epochs
        self.initial_lr = initial_lr

    def __call__(self, epoch_idx):
        if epoch_idx < self.epochs * 0.25:
            return self.initial_lr
        elif epoch_idx < self.epochs * 0.50:
            return self.initial_lr * 0.5
        elif epoch_idx < self.epochs * 0.75:
            return self.initial_lr * 0.25
        return self.initial_lr * 0.125


class MyExponentialScheduler:
    def __init__(self, nb_epochs, initial_lr):
        self.epochs = nb_epochs
        self.initial_lr = initial_lr

    def __call__(self, epoch_idx):
        k = 0.1
        self.lr = self.initial_lr * exp(-k * epoch_idx)
        return self.lr


def get_args():
    parser = argparse.ArgumentParser(description="train noise2noise model",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--image_dir", type=str, required=True,
                        help="train image dir")
    parser.add_argument("--test_dir", type=str, required=True,
                        help="test image dir")
    parser.add_argument("--image_size", type=int, default=64,
                        help="training patch size")
    parser.add_argument("--batch_size", type=int, default=16,
                        help="batch size")
    parser.add_argument("--nb_epochs", type=int, default=60,
                        help="number of epochs")
    # 原本的 learning rate=0.01 太大,模型無法收斂, 得不到 val_loss, 起始改為 lr=0.001 經測試可收斂
    parser.add_argument("--lr", type=float, default=0.001,
                        help="learning rate")
    parser.add_argument("--steps", type=int, default=None,
                        help="steps per epoch")
    parser.add_argument("--loss", type=str, default="mse",
                        help="loss; mse', 'mae','l0','mssim' is expected")
    parser.add_argument("--weight", type=str, default=None,
                        help="weight file for restart")
    parser.add_argument("--output_path", type=str, default="checkpoints",
                        help="checkpoint dir")
    parser.add_argument("--source_noise_model", type=str, default="gaussian,0,50",
                        help="noise model for source images")
    parser.add_argument("--target_noise_model", type=str, default="gaussian,0,50",
                        help="noise model for target images")
    parser.add_argument("--val_noise_model", type=str, default="gaussian,25,25",
                        help="noise model for validation source images")
    parser.add_argument("--model", type=str, default="srresnet",
                        help="model architecture ('srresnet' or 'unet')")
    args = parser.parse_args()

    return args


def main():
    # DEBUG, INFO, WARN, ERROR, or FATAL
    tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.FATAL)  # silence deprecate warning message
    config = tf.ConfigProto()  # for ubuntu nvidia driver
    config.gpu_options.allow_growth = True  # for ubuntu nvidia driver
    config.gpu_options.per_process_gpu_memory_fraction = 0.9  # for ubuntu nvidia driver
    tf.keras.backend.set_session(tf.Session(config=config))  # for ubuntu nvidia driver
    args = get_args()
    image_dir = args.image_dir
    test_dir = args.test_dir
    image_size = args.image_size
    batch_size = args.batch_size
    nb_epochs = args.nb_epochs
    init_lr = float(args.lr)
    steps = args.steps
    loss_type = args.loss
    output_path = Path(__file__).resolve().parent.joinpath(args.output_path)
    model = get_model(args.model)

    # 儲存訓練參數 JSON
    save_arg_filename = Path(output_path) / 'args.txt'
    if not output_path.expanduser().exists():
        os.makedirs(output_path)
    with open(str(save_arg_filename), 'w') as f:
        json.dump(args.__dict__, f, indent=2)

    if args.weight is not None:
        model.load_weights(args.weight)

    callbacks = []

    if loss_type == "l0":
        l0 = L0Loss()
        callbacks.append(UpdateAnnealingParameter(l0.gamma, nb_epochs, verbose=1))
        loss_type = l0()

    source_noise_model = get_noise_model(args.source_noise_model)
    target_noise_model = get_noise_model(args.target_noise_model)
    val_noise_model = get_noise_model(args.val_noise_model)
    generator = NoisyImageGenerator(image_dir, source_noise_model, target_noise_model, batch_size=batch_size,
                                    image_size=image_size)
    val_generator = ValGenerator(test_dir, val_noise_model)
    output_path.mkdir(parents=True, exist_ok=True)

    if loss_type == "mssssim":
        print('Choose mean ssim loss')
        my_opt = Adam()
        model.compile(optimizer=my_opt, loss=Mean_MSSSIM_loss, metrics=[PSNR])
        # #建立檢查點
        callbacks.append(ModelCheckpoint(str(output_path) + "/weights.{epoch:03d}-{val_loss:.3f}-{val_PSNR:.5f}.hdf5",
                                         monitor="val_PSNR",
                                         verbose=1,
                                         mode="max",
                                         save_best_only=True))

    else:
        my_opt = Adam()
        model.compile(optimizer=my_opt, loss=loss_type, metrics=[PSNR])
        # #建立檢查點
        callbacks.append(ModelCheckpoint(str(output_path) + "/weights.{epoch:03d}-{val_loss:.3f}-{val_PSNR:.5f}.hdf5",
                                         monitor="val_PSNR",
                                         verbose=1,
                                         mode="max",
                                         save_best_only=True))

    # # 更新學習率
    # my_lr_schedule_stepwise = LearningRateScheduler(schedule=MyStepwiseScheduler(nb_epochs, init_lr), verbose=1)
    my_lr_schedule_exponential = LearningRateScheduler(schedule=MyExponentialScheduler(nb_epochs, init_lr), verbose=1)
    callbacks.append(my_lr_schedule_exponential)

    # plot_model(model, to_file=str(output_path) + "/model.png", show_shapes=True,dpi=200)
    # #連續 10 次不收斂則終止訓練
    # callbacks.append(EarlyStopping(patience=10))
    # #無法收斂則終止訓練
    # callbacks.append(TerminateOnNaN())

    # #以 CSV 紀錄訓練歷史
    callbacks.append(CSVLogger(filename=str(output_path) + "/TrainingLogCsv.csv", append=True))
    # #以 TensorBoard 紀錄訓練歷史
    callbacks.append(TensorBoard(log_dir=str(output_path) + str('/logs'),
                                 histogram_freq=0,
                                 write_graph=True,
                                 write_grads=False,
                                 embeddings_freq=0,
                                 embeddings_layer_names=None,
                                 embeddings_metadata=None))

    callbacks.append(LRTensorBoard(log_dir=str(output_path) + str('/logs')))

    # #訓練模型
    hist = model.fit_generator(generator=generator,
                               steps_per_epoch=steps,
                               epochs=nb_epochs,
                               validation_data=val_generator,
                               verbose=1,
                               callbacks=callbacks,
                               )
    # #儲存訓練歷史
    np.savez(str(output_path.joinpath("history.npz")), history=hist.history)


if __name__ == '__main__':
    start_time = time.time()
    main()
    end = time.time()
    execution_time = end - start_time
    print('training takes time:', str(timedelta(seconds=execution_time)))
