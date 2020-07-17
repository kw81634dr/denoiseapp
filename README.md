# Denoise App

論文用 DIOCM 降噪程式

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


# Features
## 1.Dicom Viewer
- [x] Open single Dicom Images
- [ ] Open Dicom series
- [ ] Dicom series in Tree-view
- [x] Parse `DICOMDIR` for CD/DVD
- [x] Open fom CD/DVD & parse `DIOCMDIR`
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
