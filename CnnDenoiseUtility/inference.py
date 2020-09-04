import argparse
import numpy as np
from pathlib import Path
import cv2
from model import get_model
from noise_model import get_noise_model
import os
import tensorflow as tf
import json
from tqdm import tqdm


class KwInference:

    def __init__(self, in_dir='', out_dir='', weightpath='', model='unet', noise='g20'):
        self.debugMode = False
        self.input_dir = in_dir
        self.output_dir = out_dir
        self.weight_path = weightpath
        self.model_category = model
        self.test_noise_model = noise

    def clip_image(self, image):
        image = np.clip(image, 0, 255)
        return image.astype(dtype=np.uint8)

    def denoise(self):
        # DEBUG, INFO, WARN, ERROR, or FATAL
        tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.FATAL)  # silence deprecate warning message
        config = tf.ConfigProto()  # for ubuntu nvidia driver
        config.gpu_options.allow_growth = True  # for ubuntu nvidia driver
        tf.keras.backend.set_session(tf.Session(config=config))  # for ubuntu nvidia driver

        image_dir =  self.input_dir
        weight_file = self.weight_path
        is_sharpening = False
        val_noise_model = get_noise_model('gaussian,20,20')
        model = get_model(self.model_category)

        model.load_weights(weight_file)

        # if args.output_dir:
        #     output_dir = Path(args.output_dir)
        #     output_dir.mkdir(parents=True, exist_ok=True)
        #
        # save_arg_filename = Path(output_dir) / 'args.txt'
        # with open(str(save_arg_filename), 'w') as f:
        #     json.dump(args.__dict__, f, indent=2)

        # --kw: glob -> rglob--
        image_paths = list(Path(image_dir).expanduser().rglob("*.png"))
        image_paths += list(Path(image_dir).expanduser().rglob("*.tif"))
        image_paths += list(Path(image_dir).expanduser().rglob("*.jpg"))
        image_paths += list(Path(image_dir).expanduser().rglob("*.bmp"))

        for image_path in tqdm(image_paths):
            image_gray = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
            image = cv2.merge([image_gray, image_gray, image_gray])
            h, w, _ = image.shape
            image = image[:(h // 16) * 16, :(w // 16) * 16]  # for stride (maximum 16)
            h, w, _ = image.shape

            out_image = np.zeros((h, w * 3, 3), dtype=np.uint8)
            noise_image = val_noise_model(image)
            prediction = model.predict(np.expand_dims(noise_image, 0))
            denoised_image = self.clip_image(prediction[0])

            # if is_sharpening == 'True':
            #     print('sharpening')
            #     dst = cv2.Laplacian(denoised_image, cv2.CV_64F, ksize=1)
            #     denoised_image_float = denoised_image.astype(np.float64)
            #     denoised_image = denoised_image_float - dst
            #     denoised_image = np.clip(denoised_image, 0, 255).astype(np.uint8)

            out_image[:, :w] = image
            out_image[:, w:w * 2] = noise_image
            out_image[:, w * 2:] = denoised_image
            out_image = cv2.cvtColor(out_image, cv2.COLOR_BGR2GRAY)

            # diff = cv2.absdiff(out_image[:, w * 2:], out_image[:, :w])
            # fig_diff, ax = plt.subplots(figsize=(10, 5))
            # fig_diff.subplots_adjust(hspace=0.2, wspace=0.2)  # 設定子圖的間隔
            # plt.subplot(1, 2, 1)
            # plt.imshow(diff, vmin=0, vmax=255)
            # plt.subplot(1, 2, 2)
            # plt.hist(diff.ravel(), bins=256, range=[0, 256])
            # plt.show()

            if not self.debugMode:
                output_dir = Path(self.output_dir).expanduser().resolve()
                # print('output_dir', output_dir)
                rawImgNameWithoutExtension = str(Path(image_path).stem)
                save_file_name = output_dir / str('deN-'+rawImgNameWithoutExtension+'.png')
                # save_histogram_name = str(save_img_name)[:-4] + '_histogram.png'
                # print('save_img_name', save_img_name)
                # print('save_histogram_name', save_histogram_name)

                if not Path(output_dir).exists():
                    os.makedirs(output_dir)

                cv2.imwrite(str(save_file_name), out_image)
                # plt.savefig(save_histogram_name, dpi=300)
                # plt.close()
            else:
                cv2.imshow("result", out_image)
                key = cv2.waitKey(-1)
                # "q": quit
                if key == 113:
                    return 0