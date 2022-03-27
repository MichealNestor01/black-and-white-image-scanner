import tkinter as tk
from tkinter.filedialog import askopenfilename
import datetime
from PIL import Image, ImageOps

class Scanner:
    def __init__(self):
        self.selectedFile = False
        self.interface() #lauch the interface

    #get directory allows the user to select an image file to scan
    def getDirectory(self):
        self.selectedFile = askopenfilename()
        if self.selectedFile == '': #if the directory is '' then no image has been selected
            self.selectedFile = False
        else:
            self.imageDirectoryLabel['text'] = f'Selected image: {self.selectedFile}'
        self.resetLabels()

    #When a new image is loaded the labels need to be reset
    def resetLabels(self):
        self.totalRegionsLabel['text'] = f'Total Regions: '
        self.minValueLabel['text'] = f'Min Value: '
        self.maxValueLabel['text'] = f'Max Value: '

    #scan image is the main function that scans the image and coordinates outputs
    def scanImage(self):
        if self.selectedFile != False:
            image = Image.open(self.selectedFile).convert('L') #convert to luminance mode as RGB information is irrelevant
            pixels = list(image.getdata()) #get the value of every pixel in the image
            width, height = image.size
            pixels = [pixels[i * width:(i+1) * width] for i in range(height)] #split the pixels array into a two dimensional array with the dimensions to match the image
            #This program scans every possible 331*331 square starting from the top left, so it will move right width - 331 pixels and down height - 331 pixels
            rightShifts = width - 331 
            downShifts = height - 331
            self.totalRegionsLabel['text'] = f'Total Regions: {rightShifts * downShifts}' #This wont update till the function has completed running
            #The process of asigning new values to values in an array is faster than appending them so this is why I prefilled the arrays:
            self.heatMap = [[] for i in range(0, downShifts)] 
            for x in range(len(self.heatMap)):
                self.heatMap[x] = [0 for i in range(0, rightShifts)] 
            cumulativeMatrix = [] #The cumulative matrix replaces each value in each row with how many zeros precede it
            for y in range(len(pixels)):
                cumulativeMatrix.append([])
                cumulativeMatrix[y].append(0)
                count = 0
                for x in range(len(pixels[y])):
                    if pixels[y][x] == 0:
                        count += 1
                    cumulativeMatrix[y].append(count)
            regionCount = 0
            maxValue = 0 #this is the lowest possible maximum value
            minValue = 109561 #this is the largest possible minimum value
            self.blackList = [] #black list stores the number of black pixels in each given region
            #loop through all possible regions
            for y in range(downShifts):
                for x in range(rightShifts):
                    blackPixels = 0
                    for regionY in range(y, y + 331):
                        lowerLimit = cumulativeMatrix[regionY][x]
                        upperLimit = cumulativeMatrix[regionY][x+332]
                        blackPixels += (upperLimit - lowerLimit)
                    if blackPixels > maxValue:
                        maxValue = blackPixels
                    if blackPixels < minValue:
                        minValue = blackPixels    
                    self.blackList.append(blackPixels)
                    self.heatMap[y][x] = blackPixels
                    regionCount += 1
            self.minValueLabel['text'] = f'Min Value: {minValue}'
            self.maxValueLabel['text'] = f'Max Value: {maxValue}'
            #this script finds the folder that the selected image is in
            destinationFolder = []
            buffer = []
            for char in self.selectedFile:
                buffer.append(char)
                if char == '/':
                    for i in buffer:
                        destinationFolder.append(i)
                    buffer = []
            destinationFolder.pop()
            destinationFolder = ''.join(destinationFolder)
            #this script finds the current date and time to the nearest minute and second to ensure and unique file name
            time = datetime.datetime.now()
            timeString = []
            for char in str(time):
                if char == ':':
                    char = '-'
                timeString.append(char)
                if char == '.':
                    break
            time = ''.join(timeString)
            #write the black list to a text file
            textFile = open(f'{destinationFolder}/{time}txt', 'w')
            for value in self.blackList:
                textFile.write(f'{value}\n')
            #generate and save the heatmap image
            img = Image.new('L', (rightShifts, downShifts), 255)
            for x in range(len(self.heatMap)):
                for y in range(len(self.heatMap[x])):
                    value = self.heatMap[x][y]
                    color = 255 - int((maxValue-value)/(maxValue-minValue)*255)
                    print(f"Color {(x * len(self.heatMap[x])) + y} = {color}")
                    img.putpixel((x,y), color)
            #The heatmap comes out flipped horrizontally and 90 deg anticlockwise in the wrong direction
            #so I added these lines to fix it, then I save the image.
            img.rotate(90)
            img = ImageOps.mirror(img)
            img.save(f'{destinationFolder}/{time}png')
            
    #This function sets up a basic user interface for user interactions
    def interface(self):
        self.window = tk.Tk()
        self.windowTitle = tk.Label(text='Image Scanner', font=10)
        self.getImageButton = tk.Button(text='Get Image', width=20, bg='#6f8ac7')
        self.getImageButton['command'] = self.getDirectory #link the getImageButton to the self.getDirectory() function
        self.imageDirectoryLabel = tk.Label(text='Selected Image: ')
        self.scanImageButton = tk.Button(text='Scan Image', width=20, bg='#6f8ac7')
        self.scanImageButton['command'] = self.scanImage #link the scanImageButton to the self.scanImage() function
        self.totalRegionsLabel = tk.Label(text='Total Regions: ')
        self.maxValueLabel = tk.Label(text='Max Value: ')
        self.minValueLabel = tk.Label(text='Min Value: ')
        self.windowTitle.pack()
        self.getImageButton.pack()
        self.imageDirectoryLabel.pack()
        self.scanImageButton.pack()
        self.totalRegionsLabel.pack()
        self.maxValueLabel.pack()
        self.minValueLabel.pack()
        self.window.mainloop()

if __name__ == '__main__':
    scanner = Scanner()