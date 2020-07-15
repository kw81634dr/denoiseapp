import argparse
import numpy as np
from pathlib import Path
import cv2
from model import get_model
from noise_model import get_noise_model
from tqdm import tqdm
import os
import json
import pydicom


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


def window_scale(data, wl, ww, dtype, out_range):
    """
    Scale pixel intensity data using specified window level, width, and intensity range.
    """
    data_new = np.empty(data.shape, dtype=np.double)
    data_new.fill(out_range[1] - 1)

    data_new[data <= (wl - ww / 2.0)] = out_range[0]
    data_new[(data > (wl - ww / 2.0)) & (data <= (wl + ww / 2.0))] = \
        ((data[(data > (wl - ww / 2.0)) & (data <= (wl + ww / 2.0))] - (wl - 0.5)) / (ww - 1.0) + 0.5) * (
                    out_range[1] - out_range[0]) + out_range[0]
    data_new[data > (wl + ww / 2.0)] = out_range[1] - 1
    return data_new.astype(dtype)


def ct_windowed(dcm_ds, wl, ww, dtype, out_range):
    """
    Scale CT image represented as a `pydicom.dataset.FileDataset` instance.
    """
    # Convert pixel data from Houndsfield units to intensity:
    intercept = int(dcm_ds.RescaleIntercept)
    slope = int(dcm_ds.RescaleSlope)
    data = slope * dcm_ds.pixel_array + intercept
    # Scale intensity:
    return window_scale(data, wl, ww, dtype, out_range)


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

    # --kw: glob -> grab DCM file Only--
    image_paths = list(Path(image_dir).rglob("*.dcm"))

    for image_path in tqdm(image_paths):

        dcm_ds = pydicom.dcmread(str(image_path))
        dcm_ds_copy = dcm_ds
        default_wl = 0
        default_ww = 0
        if type(dcm_ds.WindowCenter) is pydicom.multival.MultiValue:
            default_wl = float(dcm_ds.WindowCenter[0])
        elif type(dcm_ds.WindowCenter) is pydicom.valuerep.DSfloat:
            default_wl = float(dcm_ds.WindowCenter)
        if type(dcm_ds.WindowWidth) is pydicom.multival.MultiValue:
            default_ww = float(dcm_ds.WindowWidth[0])
        elif type(dcm_ds.WindowWidth) is pydicom.valuerep.DSfloat:
            default_ww = float(dcm_ds.WindowWidth)

        rescale_intercept = float(dcm_ds.RescaleIntercept)
        rescale_slope = float(dcm_ds.RescaleSlope)

        dcm_image_scaled = ct_windowed(dcm_ds, default_wl, default_ww, np.uint8, (0, 255))
        image = cv2.cvtColor(dcm_image_scaled, cv2.COLOR_GRAY2RGB)

        h, w, _ = image.shape
        image = image[:(h // 16) * 16, :(w // 16) * 16]  # for stride (maximum 16)
        h, w, _ = image.shape

        noise_image = val_noise_model(image)
        predicts = model.predict(np.expand_dims(noise_image, 0))
        de_noised_rgb = get_image(predicts[0])
        de_noised_gray = cv2.cvtColor(de_noised_rgb, cv2.COLOR_RGB2GRAY)
        de_noised_gray_arr = np.asarray(de_noised_gray, dtype=np.int16)
        # cv2.imshow('RAW   wl:{}   ww:{}'.format(default_wl, default_ww), image)
        # cv2.imshow('De-noised', de_noised_gray)
        # cv2.waitKey(0)

        # x = np.kron([[1, 0] * 4, [0, 1] * 4] * 4, np.ones((100, 100)))

        dcm_ds_copy.WindowCenter = 127
        dcm_ds_copy.WindowWidth = 256
        dcm_ds_copy.RescaleIntercept = 0
        dcm_ds_copy.RescaleSlope = 1
        new_Patient_name = str(dcm_ds_copy.PatientName) + "-DeNoise"
        dcm_ds_copy.PatientName = new_Patient_name
        dcm_ds_copy.PixelData = de_noised_gray_arr.tostring()

        if args.output_dir:
            save_dir = Path(output_dir).joinpath(Path(image_path).parent).joinpath('denoised')
            if not Path(save_dir).exists():
                os.makedirs(save_dir)
            save_img_name = str(Path(save_dir).joinpath(Path(image_path).stem)) + '_dn.dcm'
            dcm_ds_copy.save_as(save_img_name)
        else:
            cv2.imshow("result", de_noised_gray)
            key = cv2.waitKey(-1)
            # "q": quit
            if key == 113:
                return 0


if __name__ == '__main__':
    main()
