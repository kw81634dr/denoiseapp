# Denoise App

論文用 DICOM 降噪程式
![image](https://github.com/kw81634dr/denoiseapp/blob/master/%E6%93%B7%E5%8F%96kwDeniseApp.PNG)

### To-Do
將 n2nkeras 降噪功能放在圖形介面按鈕上

# Env
python = 3.6 for vtk compatibility

# Dependencies
`tensorflow-gpu=1.15`
`opencv`
`pydicom`
`pyqt5`
`vtk`
`pillow`
`tqdm`
`chardet`


# Features
## 1.Dicom I/O
- [x] Open single Dicom Images
- [x] Load Dicom series to `Sqlite`
- [ ] Dicom series in Tree-view

##### DICOMDIR
- [x] Parse `DICOMDIR` File
- [x] `DICOMDIR` to DataBase `Sqlite`
- [x] Open from CD/DVD & parse `DIOCMDIR`
- [x] Duplicate Dcm Files to Hierarchy Folder according to `DICOMDIR`

##### Viewer
- [x] Adjustable WW/WL
- [ ] Show Dicom Tags
- [ ] Export Dicom Tags

## 2. Dicom Image Processing
- [x] Combine n2n-keras env
- [ ] Load Denoise CNN weight
- [ ] Denoise with fixed parameters
- [ ] Denoise with adjustable parameters
- [ ] Export Images in Dicom format
- [ ] Export Images in commonly used format


## 3.CNN Training Tools
- [ ] Import Dataset for training
- [ ] adjustable parameters
