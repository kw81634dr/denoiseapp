import argparse
import numpy as np
from pathlib import Path
import cv2
from model import get_model
from noise_model import get_noise_model
from tqdm import tqdm
import os
import json


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
    args = parser.parse_args()
    return args


def get_image(image):
    image = np.clip(image, 0, 255)
    return image.astype(dtype=np.uint8)


def main():
    args = get_args()
    image_dir = args.image_dir
    weight_file = args.weight_file
    val_noise_model = get_noise_model(args.test_noise_model)
    model = get_model(args.model)
    model.load_weights(weight_file)

    if args.output_dir:
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    save_arg_filename = Path(output_dir) / 'args.txt'
    with open(str(save_arg_filename), 'w') as f:
        json.dump(args.__dict__, f, indent=2)

    # --kw: glob -> rglob--
    image_paths = list(Path(image_dir).rglob("*.png"))
    image_paths += list(Path(image_dir).rglob("*.tif"))
    image_paths += list(Path(image_dir).rglob("*.jpg"))
    image_paths += list(Path(image_dir).rglob("*.bmp"))

    for image_path in tqdm(image_paths):
        # print('1', image_path)
        image = cv2.imread(str(image_path))
        h, w, _ = image.shape
        image = image[:(h // 16) * 16, :(w // 16) * 16]  # for stride (maximum 16)
        h, w, _ = image.shape

        out_image = np.zeros((h, w * 3, 3), dtype=np.uint8)
        noise_image = val_noise_model(image)
        pred = model.predict(np.expand_dims(noise_image, 0))
        denoised_image = get_image(pred[0])
        out_image[:, :w] = image
        out_image[:, w:w * 2] = noise_image
        out_image[:, w * 2:] = denoised_image

        if args.output_dir:
            # print('2', Path(output_dir))
            # print('3', image_path)
            save_dir = Path(output_dir).joinpath(Path(image_path).parent).joinpath('denoised')
            # save_dir = Path(output_dir).joinpath(Path(image_path).parent.name)

            if not Path(save_dir).exists():
                os.makedirs(save_dir)

            save_img_name = str(Path(save_dir).joinpath(Path(image_path).stem)) + '.png'
            # print('Dir:', save_dir)
            print('save_file_name:', save_img_name)
            cv2.imwrite(save_img_name, out_image)
        else:
            cv2.imshow("result", out_image)
            key = cv2.waitKey(-1)
            # "q": quit
            if key == 113:
                return 0


if __name__ == '__main__':
    main()
