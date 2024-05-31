
# QGIS GeorefExtension Plugin

This is a QGIS 3.x Python plugin to extend the features of the QGIS Raster Georeferencer.

## Why do we need a Georeferencer Extension?

The QGIS Georeferencer is a helpful tool to georeference all kinds of raster images, but there are a few features missing that could improve the process of georeferencing.

The following list shows the features I missed when I started using the QGIS Georeferencer more often.
That's why I decided to extend it.

1.) Export to **Virtual raster file (VRT)** instead of GeoTIFF.

2.) **Iterative improvement** of the georeferencing result by repeatedly changing/adjusting GCPs

3.) **Clipping the georeferenced image** with a QGIS polygon feature

4.) Changing the **background color** of the Georeferencer Map Canvas

5.) Easy **removal of all GCPs**

I will explain each list item later.

## What does the extension look like?

The extension consists of an additional Georeferencer toolbar with 3 buttons and a dialog for the VRT options:


![GeorefExtension Toolbar](file:///./images/toolbar.jpg)

|         |         |
| ------- | ------- |
| ![Set Background Color](file:///./icons/color.png) | Set Background Color |
| ![Delete all GCPs](file:///./icons/delete.png) | Delete all GCPs |
| ![Create Virtual Raster](file:///./icons/go.png) | Create Virtual Raster |

![Georeferencer Dialog](file:///./images/georeferencer.jpg)

The "Create Virtual Raster" dialog is only shown if a raster is loaded into the Georeferencer Map Canvas and the button "Create Virtual Raster" is pressed.

## How does the Georeferencer Extension work?

The Georeferencer Extension uses GDAL's Python bindings (gdal.translate, gdal.warp) to re-project a raster image using the ground control points (GCPs) from the GCP table, crop the result if necessary and save to VRT.

Since GDAL has no option to define a raster transformation typ, the QGIS Georeferencer transformation type setting (see Georeferencer > Settings > Transformation Settings... > Transformation Parameters) is ignored. GDAL selects the transformation type itself, depending on the number of GCPs.
Most, if not all, Transformation Settings parameters are ignored by the Georeferencer Extension, but you have to choose the right Source-CRS and Target-CRS before you start to pick GCPs.

## What use cases are there?

Here I come back to the list of the missing features I mentioned earlier.

### 1.) Export to **Virtual raster file (VRT)** instead of GeoTIFF:

I always found it very impractical that the original images were duplicated and I had to accept a certain loss of quality in the result.
In addition, QGIS locks the result file, so I cannot simply overwrite it. This brings me to item 2 of my list.

### 2.) **Iterative improvement** of the georeferencing result by repeatedly changing/adjusting GCPs

Virtual raster files (VRT) can be overwritten at any time, making iterative georeferencing easy.
By iterative georeferencing, I mean repeatedly adding and removing GCPs and refreshing the resulting image in QGIS. 
This means that the image does not lose any blending mode settings that may have been set and retains the correct layer order.

### 3.) **Clipping the georeferenced image** with a QGIS feature boundary

The georeferencing of images very often also requires cropping of the image content.
To make this process as efficient as possible, I have created the option of specifying WKT strings as clipping boundaries.
This allows us to select individual features using the QGIS `Copy Features` command and paste the WKT string into the "Enter Cutline WKT" edit field.

### 4.) Changing the **background color** of the Georeferencer Map Canvas

If we need to georeference images with a white background where the coordinates of the corner points are known but the corners not visible, we can use the “Change Background Color” button to change the background color of the Georeferencer Map Canvas.

### 5.) Easy **removal of all GCPs**

Not important, but sometimes helpful if we can delete all GCPs with the click of a button.

## The Create Virtual Raster dialog

![GeorefExtension Dialog](file:///./images/dialog.jpg)

|         |         |
| ------- | ------- |
| **Output File** | ... *the Name and Path of the Output File is automatically choosen from the Source Image. If the directory is read-only the Temp Path is used instead. We can change the file name to create multiple versions.* |
| **NoData Value** | ... *an Integer value to define a color as NoData (i.e. 255,0 or 1 for B/W images).* |
| **Create Alpha Channel** | ... *we have to enable this switch if we want to create an Alpha band (esp. for cropping images).* |
| **Load in QGIS when done** | ... *we have to enable this switch if we want to view the result in QGIS. If we repeat the georeferencing or cropping with the same image, we can disable the switch and track the changes to the existing image.* |
| **Target SRS** | ... *CRS of the result image.* |
| **Cutline SRS** | ... *CRS of the clipping boundary.* |
| **Enter Cutline WKT** | ... *WKT string of the clipping boundary.* |

## How to improve PDF image quality?

If we need to improve PDF image quality, we can change the resolution using the GDAL System Environment variable `GDAL_PDF_DPI`:

`set GDAL_PDF_DPI=300` (Windows). The default value is 250.

## Want to crop an already georeferenced Image?

We can use the Georeference Extension to crop already georeferenced images as well.
We can drag & drop a GeoTIFF or GeoPDF into the Georeferencer Map Canvas and call `Create Virtual Raster` without specifying any GCP.

