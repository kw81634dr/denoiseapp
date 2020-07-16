import pydicom
import numpy as np


class DcmModule:

    def window_scale(self, data, wl, ww, dtype, out_range):
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

    def ct_windowed(self, dcm_ds, wl, ww, dtype, out_range):
        """
        Scale CT image represented as a `pydicom.dataset.FileDataset` instance.
        """
        # Convert pixel data from Houndsfield units to intensity:
        intercept = int(dcm_ds.RescaleIntercept)
        slope = int(dcm_ds.RescaleSlope)
        data = slope * dcm_ds.pixel_array + intercept
        # Scale intensity:
        return DcmModule.window_scale(data, wl, ww, dtype, out_range)

    @staticmethod
    def read_dcm_file(image_path):
        try:
            dcm_ds = pydicom.dcmread(str(image_path))
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

            return dcm_ds, default_wl, default_ww, rescale_intercept, rescale_slope

        except Exception as e:
            pass
            print('Exception', e)
        print("Cannot read DICOM! ", image_path)

