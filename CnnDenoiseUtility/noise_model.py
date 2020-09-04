import argparse
import string
import random
import numpy as np
import cv2
from skimage.util import random_noise, img_as_float, img_as_ubyte, img_as_float64


def get_noise_model(noise_type="gaussian,0,50"):
    tokens = noise_type.split(sep=",")

    if tokens[0] == "gaussian":
        min_stddev = int(tokens[1])
        max_stddev = int(tokens[2])

        def gaussian_noise(img):
            # print('gaussian noise')
            noise_img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            noise_img_gray = noise_img_gray.astype(np.float)
            stddev = np.random.uniform(min_stddev, max_stddev)
            noise = np.random.randn(*noise_img_gray.shape) * stddev
            noise_img_gray += noise
            noise_img_gray = np.clip(noise_img_gray, 0, 255).astype(np.uint8)
            noise_img = cv2.merge([noise_img_gray, noise_img_gray, noise_img_gray])
            # title = "N," + str(img.shape)
            # cv2.imshow(title, noise_img)
            # cv2.waitKey(0)
            return noise_img
        return gaussian_noise

    elif tokens[0] == "poisson":
        def poisson_noise(img):
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            image_gray_scikit_float = img_as_float(img_gray)
            noisy_img = random_noise(image_gray_scikit_float, mode='poisson')
            cv_image = img_as_ubyte(noisy_img)
            noisy_img_gray = np.clip(cv_image, 0, 255).astype(np.uint8)
            noisy_poisson_img = cv2.merge([noisy_img_gray, noisy_img_gray, noisy_img_gray])
            # print('poisson added')
            # title = "N," + str(img.shape)
            # cv2.imshow(title, noisy_poisson_img)
            # cv2.waitKey(0)
            return noisy_poisson_img
        return poisson_noise

    elif tokens[0] == "low_dose":
        min_stddev = int(tokens[1])
        max_stddev = int(tokens[2])

        def low_dose(img):
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            image_gray_scikit_float = img_as_float(img_gray)
            #   gen poisson
            poisson_noisy_img = random_noise(image_gray_scikit_float, mode='poisson')
            #   gen gaussian
            img_gray_cv = img_gray.astype(np.float)
            stddev = np.random.uniform(min_stddev, max_stddev)
            gau_noise = np.random.randn(*img_gray_cv.shape) * stddev
            img_gray_cv += gau_noise
            norm_gau = cv2.normalize(img_gray_cv, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_64F)
            #   combine 2 types of noise
            noisy_img = poisson_noisy_img + norm_gau
            #   convert to unsigned byte
            noisy_norm = cv2.normalize(noisy_img, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
            noisy_low_dose_img = cv2.merge([noisy_norm, noisy_norm, noisy_norm])
            # print('low_dose added')
            # title = "N," + str(img.shape)
            # cv2.imshow(title, noisy_low_dose_img)
            # cv2.waitKey(0)
            return noisy_low_dose_img
        return low_dose

    elif tokens[0] == "clean":
        return lambda img: img
    elif tokens[0] == "text":
        min_occupancy = int(tokens[1])
        max_occupancy = int(tokens[2])

        def add_text(img):
            img = img.copy()
            h, w, _ = img.shape
            font = cv2.FONT_HERSHEY_SIMPLEX
            img_for_cnt = np.zeros((h, w), np.uint8)
            occupancy = np.random.uniform(min_occupancy, max_occupancy)

            while True:
                n = random.randint(5, 10)
                random_str = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(n)])
                font_scale = np.random.uniform(0.5, 1)
                thickness = random.randint(1, 3)
                (fw, fh), baseline = cv2.getTextSize(random_str, font, font_scale, thickness)
                x = random.randint(0, max(0, w - 1 - fw))
                y = random.randint(fh, h - 1 - baseline)
                color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                cv2.putText(img, random_str, (x, y), font, font_scale, color, thickness)
                cv2.putText(img_for_cnt, random_str, (x, y), font, font_scale, 255, thickness)

                if (img_for_cnt > 0).sum() > h * w * occupancy / 100:
                    break
            return img
        return add_text
    elif tokens[0] == "impulse":
        min_occupancy = int(tokens[1])
        max_occupancy = int(tokens[2])

        def add_impulse_noise(img):
            occupancy = np.random.uniform(min_occupancy, max_occupancy)
            mask = np.random.binomial(size=img.shape, n=1, p=occupancy / 100)
            noise = np.random.randint(256, size=img.shape)
            img = img * (1 - mask) + noise * mask
            return img.astype(np.uint8)
        return add_impulse_noise
    else:
        raise ValueError("noise_type should be 'gaussian', 'clean', 'text', or 'impulse'")


def get_args():
    parser = argparse.ArgumentParser(description="test noise model",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--image_size", type=int, default=256,
                        help="training patch size")
    parser.add_argument("--noise_model", type=str, default="gaussian,0,50",
                        help="noise model to be tested")
    args = parser.parse_args()
    return args


def main():
    args = get_args()
    image_size = args.image_size
    noise_model = get_noise_model(args.noise_model)

    while True:
        image = np.ones((image_size, image_size, 3), dtype=np.uint8) * 128
        cv2.imshow("RAW image", image)
        noisy_image = noise_model(image)
        cv2.imshow("noise image", noisy_image)
        key = cv2.waitKey(-1)

        # "q": quit
        if key == 113:
            return 0


if __name__ == '__main__':
    main()
