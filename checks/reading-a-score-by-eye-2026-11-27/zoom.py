"""A closer look at one band of a system picture: python3 -I zoom.py IN.png OUT.png Y0 Y1 X0 X1 FACTOR"""
import sys, cv2
src, out, y0, y1, x0, x1, f = sys.argv[1], sys.argv[2], *map(int, sys.argv[3:7]), float(sys.argv[7])
im = cv2.imread(src, cv2.IMREAD_GRAYSCALE)[y0:y1, x0:x1]; im = cv2.resize(im, None, fx=f, fy=f, interpolation=cv2.INTER_CUBIC); cv2.imwrite(out, im); print(out, im.shape[1::-1])
