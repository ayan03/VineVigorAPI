from flask import request, url_for
from flask_api import FlaskAPI, status, exceptions
import cv2
import numpy as np
import base64

app = FlaskAPI(__name__)

@app.route('/', methods = ['GET', 'POST'])
def test():
    if request.method == 'POST':
        print("Handling POST request")

        # Retrieve b64 image data in body
        data = request.get_json()
        b64_string = data['image']
        print(type(b64_string))
         
        decoded_image = base64.b64decode(b64_string)
        np_data = np.frombuffer(decoded_image, np.uint8)
        image = cv2.imdecode(np_data, -1)

        print("Running algo")
        # Algo from Pantoja
        #Image denoising
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        # threshold the image, then perform a series of erosions +
        # dilations to remove any small regions of noise
        shifted = cv2.threshold(gray, 130, 255, cv2.THRESH_BINARY)[1]
        #next line commented since the next contour erodes the image too much
        #shifted = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1] #modify the threshold 
        opening = cv2.erode(shifted, None, iterations=2)
        closing = cv2.dilate(opening, None, iterations=2)

        #select the ROI of image to calculate the contour to avoid images with more than one wine tree
        """
        cv2.namedWindow('image',cv2.WINDOW_NORMAL)
        fromCenter = False
        r = cv2.selectROI('image', closing, fromCenter)
        """
        # Crop image according to the selected region of interest
        imCrop = closing
        originalCrop = image

        #find contours by selecting the black pixels
        cnts = cv2.findContours(imCrop, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2]
        print("[INFO] {} unique contours found".format(len(cnts)))
        #cv2.drawContours(originalCrop, cnts, -1, (0, 0, 255), 1)

        #Erase lines from wires
        lines = cv2.HoughLinesP(imCrop, 1, np.pi/180, 30,250)
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(originalCrop, (x1, y1), (x2, y2), (0, 0, 128), 1) #TODO change this and make pixels in line same color as its neighbor average


        #calculate the weight of the contour as how many pixels are black inside a selected rectangle
        height, width = imCrop.shape 
        TotalNumberOfPixels =height*width
        add=0
        for contour in cnts:
            #if cv2.contourArea(contour) > 100 : 
            add=add+cv2.cv2.contourArea(contour)
            cv2.drawContours(originalCrop, [contour], -1, (0, 0, 255), 2)
        print("[INFO] {} Contour Area".format(TotalNumberOfPixels-add))

        #count black pixels
        blackPixels = TotalNumberOfPixels - cv2.countNonZero(imCrop)
        print("[INFO] {} Black Pixels Area".format(blackPixels)) 
        #TODO change from number of pixels to weight in kg

        #reference drawing is good to determine wdith and hight no for this
        #we need to trnslate pixels to cm 1 pixel (X) = 0.0264583333 cm and 458 ppi
        #peso de una cagna 

        # When calling through flask have to disable GUI pop-ups
        """
        while(1):
            cv2.imshow('image',originalCrop)
            k = cv2.waitKey(1) & 0xFF
            if k == ord('q'):
                cv2.imwrite('output.jpg',originalCrop)
                break
        cv2.destroyAllWindows()
        """
        #ret_img = base64.b64encode(originalCrop).decode("utf-8")
        ret_img = base64.b64encode(decoded_image).decode("utf-8")

        body = {
            'POST' : 'POST data',
            'image': ret_img,
            'contours': len(cnts),
            'area': TotalNumberOfPixels - add,
            'black': blackPixels
        }

        return body, status.HTTP_200_OK
    else:
        print("Handling GET request")
        body = {'GET' : 'GET data'}
        return body, status.HTTP_200_OK

if __name__ == "__main__":
    app.run(debug=True)