# authors : Guillaume Lemaitre <g.lemaitre58@gmail.com>
# license : MIT

from os.path import dirname, join
from pprint import pprint
from pathlib import Path
import pydicom
from pydicom.data import get_testdata_file
from pydicom.filereader import read_dicomdir
from pydicom.tag import Tag

# fetch the path to the test data
filepath = Path('D:/Users/user/Desktop/CT1/DICOMDIR').expanduser()
print('Path to the DICOM directory: {}'.format(filepath))
# load the data
dicom_dir = read_dicomdir(filepath)
base_dir = dirname(filepath)

# go through the patient record and print information
for patient_record in dicom_dir.patient_records:
    try:
        print("Patient: {}: {}".format(patient_record.PatientID,
                                       patient_record.PatientName))
    except AttributeError:
        print('AttributeError')
        pass
    studies = patient_record.children
    # got through each serie
    for study in studies:
        print(" " * 4 + "Study {}: {}: {}".format(study.StudyID,
                                                  study.StudyDate,
                                                  study.StudyDescription))
        all_series = study.children
        # go through each serie
        for series in all_series:
            image_count = len(series.children)
            plural = ('', 's')[image_count > 1]

            # Write basic series info and image count

            # Put N/A in if no Series Description
            if 'SeriesDescription' not in series:
                series.SeriesDescription = "N/A"
            print(" " * 8 + "Series {}: {}: {} ({} image{})".format(
                series.SeriesNumber, series.Modality, series.SeriesDescription,
                image_count, plural))

            # Open and read something from each image, for demonstration
            # purposes. For simple quick overview of DICOMDIR, leave the
            # following out
            print(" " * 12 + "Reading images...")
            image_records = series.children
            image_filenames = [join(base_dir, *image_rec.ReferencedFileID)
                               for image_rec in image_records]

            datasets=[]

            for image_filename in image_filenames:
                try:
                    datasets.append(pydicom.dcmread(image_filename))
                except FileNotFoundError:
                    print('File Not Found!')
                    pass

            # def safe_execute(default, exception, function, *args):
            #     try:
            #         return function(*args)
            #     except exception:
            #         return default

            patient_names = set(ds[Tag(0x33, 0x1013)].value.decode('utf8') for ds in datasets)
            patient_IDs = set(ds[Tag(0x33, 0x1014)].value.decode('utf8') for ds in datasets)
            # patient_names = set(ds.PatientName for ds in datasets)
            # patient_IDs = set(ds.PatientID for ds in datasets)

            # List the image filenames
            print("\n" + " " * 12 + "Image filenames:")
            print(" " * 12, end=' ')
            pprint(image_filenames, indent=12)

            # Expect all images to have same patient name, id
            # Show the set of all names, IDs found (should each have one)
            print(" " * 12 + "Patient Names in images..: {}".format(
                patient_names))
            print(" " * 12 + "Patient IDs in images..: {}".format(
                patient_IDs))
