import cv2 as cv


def get_pos(image):
  blurred = cv.GaussianBlur(image, (5, 5), 0)
  canny = cv.Canny(blurred, 200, 400)
  cv.imshow("canny",canny)
  contours, hierarchy = cv.findContours(canny, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
  # print(list(enumerate(contours)))
  # cv.imshow("cont",contours)
  for i, contour in enumerate(contours):
    M = cv.moments(contour)
    # print(M)
    if M['m00'] == 0:
      cx = cy = 0
    else:
      cx, cy = M['m20'] / M['m00'], M['m02'] / M['m00']
    print("area",cv.contourArea(contour))
    print("arcLength",cv.arcLength(contour, True))
    print('--------------------------')
    # if 30 < cv.contourArea(contour) < 60 and 350 < cv.arcLength(contour, True) < 450:
      # if cx < 400:
      #   continue
    x, y, w, h = cv.boundingRect(contour) # 外接矩形
    cv.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
    cv.imshow('image', image)
    # return x
  return 0


if __name__ == '__main__':
  # 图片400*200
  img0 = cv.imread('./test2.jpg')
  get_pos(img0)
  cv.waitKey(0)
  cv.destroyAllWindows()


'''
import cv2 as cv


def get_pos(image):
  blurred = cv.GaussianBlur(image, (5, 5), 0)
  canny = cv.Canny(blurred, 200, 400)
  contours, hierarchy = cv.findContours(canny, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
  for i, contour in enumerate(contours):
    M = cv.moments(contour)
    if M['m00'] == 0:
      cx = cy = 0
    else:
      cx, cy = M['m10'] / M['m00'], M['m01'] / M['m00']
    if 6000 < cv.contourArea(contour) < 8000 and 370 < cv.arcLength(contour, True) < 390:
      if cx < 400:
        continue
      x, y, w, h = cv.boundingRect(contour) # 外接矩形
      cv.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
      cv.imshow('image', image)
      return x
  return 0


if __name__ == '__main__':
  img0 = cv.imread('./demo/4/hycdn_4.jpg')
  get_pos(img0)
  cv.waitKey(0)
  cv.destroyAllWindows()

'''