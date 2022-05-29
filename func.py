# import the necessary packages
from scipy.spatial import distance as dist
from imutils import perspective
from imutils import contours
import numpy as np
import math
import imutils
import cv2
import matplotlib.pyplot as plt

def remove_outlier(df_in, col_name):
    q1 = df_in[col_name].quantile(0.25)
    q3 = df_in[col_name].quantile(0.75)
    iqr = q3-q1 #Interquartile range
    fence_low  = q1-1.06*iqr
    fence_high = q3+1.06*iqr
    df_out = df_in.loc[(df_in[col_name] > fence_low) & (df_in[col_name] < fence_high)]
    return df_out

def midpoint(ptA, ptB):
    return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)


def estimate_coef(x, y):
    # number of observations/points
    n = np.size(x)

    # mean of x and y vector
    m_x = np.mean(x)
    m_y = np.mean(y)

    # calculating cross-deviation and deviation about x
    SS_xy = np.sum(y * x) - n * m_y * m_x
    SS_xx = np.sum(x * x) - n * m_x * m_x

    # calculating regression coefficients
    b_1 = SS_xy / SS_xx
    b_0 = m_y - b_1 * m_x

    return (b_0, b_1)


# plot the best fit line
def plot_regression_line(x, y, b):
    # plotting the actual points as scatter plot
    plt.scatter(x, y, color="m",
                marker="o")

    # predicted response vector
    y_pred = b[0] + b[1] * x

    # plotting the regression line
    plt.plot(x, y_pred, color="g")

    # putting labels
    plt.xlabel('L^2')
    plt.ylabel('4t')

    # function to show plot
    plt.show()


# construct the argument parse and parse the arguments
# ap = argparse.ArgumentParser()
# ap.add_argument("-i", "--image", required=True,
#     help="path to the input image")
# ap.add_argument("-w", "--width", type=float, required=True,
#     help="width of the left-most object in the image (in inches)")
# args = vars(ap.parse_args())
# load the video, convert each frame of it to grayscale, and blur them slightly, mask every frame after finding the coin by violet
def calculateVis(filename, liquid):
    cap = cv2.VideoCapture("uploadedimages//"+filename)
    ref_width = 0.02615
    count = 0   #frame count
    pixelsPerMetric = None
    time_radius = []
    errors = 0
    roi_offset = 25
    lower_violet = np.array([110,60,60]) #lower range of violet (HSV)
    upper_violet = np.array([160,255,255]) #higher range of violet(HSV)
    found = False
    violet_pixel = 0
    while(cap.isOpened()):
        count+=1
        ret, frame = cap.read()
        if not ret:   #when video ends
            break
        image = frame.copy()

        if pixelsPerMetric is not None:   #if coin is found
            if count < 30:#for precision
                continue
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, lower_violet, upper_violet)
            # cv2.imshow("Mask", mask)
            image = cv2.bitwise_and(frame, frame, mask = mask)
            violet_pixel= np.count_nonzero(image)
            pixel_r = math.sqrt(violet_pixel/math.pi)
            theo_r = pixel_r/pixelsPerMetric
            #print("Frame,", count," Radius,", theo_r)
            time_radius.append((count/30, 2*theo_r))
            cv2.putText(image, str(2*theo_r)+"m",(int(1920/2), int(1080/2)), cv2.FONT_HERSHEY_SIMPLEX,
            0.65, (255, 255, 255), 2)
            resized = cv2.resize(image,(960,540))
            cv2.imshow("Radius",resized)
            if cv2.waitKey(1) == 13: #13 is the Enter Key
                break
            continue


        if pixelsPerMetric is None:
            image = image[roi_offset:int(frame.shape[0]/3),roi_offset:int(frame.shape[1]/2)]
            # cv2.imshow("Crop", coin_image)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)   #grayscale
        blurred = cv2.GaussianBlur(gray, (7, 7), 0)   #blur
        # perform edge detection, then perform a dilation + erosion to
        # close gaps in between object edges
        edged = cv2.Canny(blurred, 10, 30)   #edge detection
        dilated = cv2.dilate(edged, None, iterations=1)  #dilation
        eroded = cv2.erode(dilated, None, iterations=1)   #erosion
        if pixelsPerMetric is None:
            cv2.imshow("Eroded",eroded)
        # find contours in the edge map
        cnts = cv2.findContours(eroded.copy(), cv2.RETR_EXTERNAL,   #find objects
            cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        # sort the contours from left-to-right and initialize the
        # 'pixels per metric' calibration variable
        if len(cnts) <= 0:
            cv2.waitKey(0)
            continue
        (cnts, _) = contours.sort_contours(cnts)
        # loop over the contours individually
        for c in cnts:
            # if the contour is not sufficiently large, ignore it
            if cv2.contourArea(c) < 1000:
                continue
            # compute the rotated bounding box of the contour
            orig = image.copy()
            box = cv2.minAreaRect(c)
            box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
            box = np.array(box, dtype="int")
            # order the points in the contour such that they appear
            # in top-left, top-right, bottom-right, and bottom-left
            # order, then draw the outline of the rotated bounding
            # box
            box = perspective.order_points(box)
            cv2.drawContours(orig, [box.astype("int")], -1, (0, 255, 0), 2)
            # loop over the original points and draw them
            for (x, y) in box:
                cv2.circle(orig, (int(x), int(y)), 5, (0, 0, 255), -1)
            # unpack the ordered bounding box, then compute the midpoint
            # between the top-left and top-right coordinates, followed by
            # the midpoint between bottom-left and bottom-right coordinates
            (tl, tr, br, bl) = box
            (tltrX, tltrY) = midpoint(tl, tr)
            (blbrX, blbrY) = midpoint(bl, br)
            # compute the midpoint between the top-left and top-right points,
            # followed by the midpoint between the top-righ and bottom-right
            (tlblX, tlblY) = midpoint(tl, bl)
            (trbrX, trbrY) = midpoint(tr, br)
            #print("frame: ",count)
            # if pixelsPerMetric is not None and (tltrX < 570 or tltrX > 814 or tltrY < 170 or tltrY > 372):
            #     continue


            # draw the midpoints on the image
            cv2.circle(orig, (int(tltrX), int(tltrY)), 5, (255, 0, 0), -1)
            cv2.circle(orig, (int(blbrX), int(blbrY)), 5, (255, 0, 0), -1)
            cv2.circle(orig, (int(tlblX), int(tlblY)), 5, (255, 0, 0), -1)
            cv2.circle(orig, (int(trbrX), int(trbrY)), 5, (255, 0, 0), -1)
            # draw lines between the midpoints
            cv2.line(orig, (int(tltrX), int(tltrY)), (int(blbrX), int(blbrY)),
                (255, 0, 255), 2)
            cv2.line(orig, (int(tlblX), int(tlblY)), (int(trbrX), int(trbrY)),
                (255, 0, 255), 2)
            # compute the Euclidean distance between the midpoints
            dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
            dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))
            # if the pixels per metric has not been initialized, then
            # compute it as the ratio of pixels to supplied metric
            # (in this case, cm)
            if pixelsPerMetric is None:   #first frame is the coin
                pixelsPerMetric = dB / ref_width
                found = True
            # compute the size of the object
            dimA = dA / pixelsPerMetric
            dimB = dB / pixelsPerMetric
            print(dimA, dimB)
            # draw the object sizes on the image
            cv2.putText(orig, "{:.4f}m".format(dimA),
                (int(tltrX - 15), int(tltrY - 10)), cv2.FONT_HERSHEY_SIMPLEX,
                0.65, (255, 255, 255), 2)
            cv2.putText(orig, "{:.4}m".format(dimB),
                (int(trbrX + 10), int(trbrY)), cv2.FONT_HERSHEY_SIMPLEX,
                0.65, (255, 255, 255), 2)
            print("x: ",int(tltrX)," y: ",int(tltrY))

            cv2.putText(orig, "frame{:d}".format(int(count)),
                (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
                0.65, (255, 255, 255), 2)
            cv2.putText(orig, "{:d}s".format(int(count/30)),
                (50, 70), cv2.FONT_HERSHEY_SIMPLEX,
                0.65, (255, 255, 255), 2)
            # show the output image
            resized = cv2.resize(orig,(960,540))
            cv2.imshow("Coin", resized)
            found = False
            break;
        if cv2.waitKey(1) == 13: #13 is the Enter Key
            break
    #initialize lists for l^2 and 4t values for the graph
    print(pixelsPerMetric)
    print("Number of errors: ", errors)
    x=[]
    y=[]
    for i in time_radius:
        x.append(i[0]*4) #4t
        y.append((i[1]*2)**2) #diameter squared

    # df = pd.DataFrame(time_radius, columns = ['time','radius'])
    # print(df)
    # df_out = remove_outlier(df, 'radius')
    # print(df_out)
    # new_time_radius = df_out.to_numpy()
    # x=[]
    # y=[]
    # for i in new_time_radius:
    #     if i[0] != 0:
    #         x.append(i[0])
    #         y.append(i[1])
    # plotting the points convert lists to numpy arrays
    x=np.array(x)
    y=np.array(y)
    #plt.plot(x, y, 'o')

    # naming the x axis
    #plt.xlabel('4t')
    # naming the y axis
    #plt.ylabel('L^2')

    # giving a title to my graph
    #plt.title('Diffusion')

    # estimating coefficients
    b = estimate_coef(x, y)
    slope = b[1]/b[0]
    print("Estimated coefficients:\nb_0 = {}  \
          \nb_1 = {}".format(b[0], b[1]))

    # plotting regression line
    #plot_regression_line(x, y, b)
    # m, b = np.polyfit(x,y,1)
    # plt.plot(x, m*x+b)
    # slope = m

    #print diffusion
    print("Diffusion: ",slope)

    top = 4.11*(10**-13)
    bottom = 6*math.pi*5*slope
    viscosity = top/bottom
    print("Viscosity:", viscosity)
    result = "Diffusion: %f.5 Viscosity: %f.3"%(slope, viscosity)
    # function to show the plot
    #plt.show()
    cv2.destroyAllWindows()
    cap.release()
    if liquid == "Water":
        if slope>0.00420 and slope< 0.00711:
            result = "PURE"
        else:
            result = "IMPURE"
    elif liquid == "Cologne":
        if slope>0.0134 and slope< 0.0536:
            result = "PURE"
        else:
            result = "IMPURE"
    return result
