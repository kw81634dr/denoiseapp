import argparse
import numpy as np
from pathlib import Path
import cv2
from model import get_model
from noise_model import get_noise_model
import os
import tensorflow as tf
import json
# from matplotlib import pyplot as plt


def get_args():
    parser = argparse.ArgumentParser(description="Test trained model",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--image_dir", type=str, required=True,
                        help="test image dir")
    parser.add_argument("--model", type=str, default="srresnet",
                        help="model architecture ('srresnet' or 'unet')")
    parser.add_argument("--weight_file", type=str, required=True,
                        help="trained weight file")
    parser.add_argument("--test_noise_model", type=str, default="gaussian,25,25",
                        help="noise model for test images")
    parser.add_argument("--output_dir", type=str, default=None,
                        help="if set, save resulting images otherwise show result using imshow")
    parser.add_argument("--laplacian_sharpening", type=str, default=False,
                        help="boolean for applying laplacian_sharpening")
    args = parser.parse_args()
    return args


def get_image(image):
    image = np.clip(image, 0, 255)
    return image.astype(dtype=np.uint8)


def main():
    # DEBUG, INFO, WARN, ERROR, or FATAL
    tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.FATAL)  # silence deprecate warning message
    config = tf.ConfigProto()  # for ubuntu nvidia driver
    config.gpu_options.allow_growth = True  # for ubuntu nvidia driver
    tf.keras.backend.set_session(tf.Session(config=config))  # for ubuntu nvidia driver
    args = get_args()
    image_dir = args.image_dir
    weight_file = args.weight_file
    is_sharpening = args.laplacian_sharpening
    val_noise_model = get_noise_model(args.test_noise_model)
    model = get_model(args.model)
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

    for image_path in image_paths:
        image_gray = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
        image = cv2.merge([image_gray, image_gray, image_gray])
        h, w, _ = image.shape
        image = image[:(h // 16) * 16, :(w // 16) * 16]  # for stride (maximum 16)
        h, w, _ = image.shape

        out_image = np.zeros((h, w * 3, 3), dtype=np.uint8)
        noise_image = val_noise_model(image)
        prediction = model.predict(np.expand_dims(noise_image, 0))
        denoised_image = get_image(prediction[0])

        if is_sharpening == 'True':
            print('sharpening')
            dst = cv2.Laplacian(denoised_image, cv2.CV_64F, ksize=1)
            denoised_image_float = denoised_image.astype(np.float64)
            denoised_image = denoised_image_float - dst
            denoised_image = np.clip(denoised_image, 0, 255).astype(np.uint8)

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

        if args.output_dir:
            output_dir = Path(args.output_dir).expanduser().resolve()
            # print('output_dir', output_dir)

            save_img_name = output_dir.joinpath(image_path)
            save_histogram_name = str(save_img_name)[:-4] + '_histogram.png'
            # print('save_img_name', save_img_name)
            # print('save_histogram_name', save_histogram_name)

            if not Path(save_img_name.parent).exists():
                os.makedirs(save_img_name.parent)

            cv2.imwrite(str(save_img_name), out_image)
            # plt.savefig(save_histogram_name, dpi=300)
            # plt.close()
        else:
            cv2.imshow("result", out_image)
            key = cv2.waitKey(-1)
            # "q": quit
            if key == 113:
                return 0


if __name__ == '__main__':
    main()
