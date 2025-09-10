from PIL import Image

img = Image.open("./moavlink.png")
img.save("moavlink.ico", format="ICO", sizes=[(256,256), (128,128), (64,64), (32,32), (16,16)])
