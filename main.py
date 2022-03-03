import cv2
import cvzone
import numpy as np 
import math
import random
from cvzone.HandTrackingModule import HandDetector
import os

cap = cv2.VideoCapture(0)
detector = HandDetector(detectionCon=0.8, maxHands=1)

class SnakeGameClass:
    def __init__(self, pathFood):
        self.points = [] #all points of the snake 
        self.lengths = [] #distance between each point
        self.currentLength = 0 #total length of the snake
        self.allowedLength = 150 #total allowed length 
        self.previousHead = 0, 0 #previous head point 
        
        
        self.imgFood = cv2.imread(pathFood, cv2.IMREAD_UNCHANGED)
        
        self.hFood, self.wFood, _ = self.imgFood.shape
        self.foodPoint = 0, 0
        self.randomFoodLocation()
        
        self.score = 0
        self.gameOver = False
        
        
    def randomFoodLocation(self):
        self.foodPoint = random.randint(100, 600), random.randint(100, 400)
    def update(self, imgMain, currentHead):
        if self.gameOver:
            cvzone.putTextRect(imgMain, "Game Over!", [100,100], scale=4, thickness=4, offset=10)
            cvzone.putTextRect(imgMain, f"Your Score: {self.score}", [100,50], scale=4, thickness=2, offset=10)
        else: 
            px, py = self.previousHead
            cx, cy = currentHead
            
            
            self.points.append([cx, cy])
            distance = math.hypot(cx - px, cy - py)
            self.lengths.append(distance)
            self.currentLength += distance
            self.previousHead = cx, cy
            
            #Length Reduction 
            if self.currentLength > self.allowedLength:
                for i, length in enumerate(self.lengths):
                    self.currentLength -= length
                    self.lengths.pop(i)
                    self.points.pop(i)
                    if self.currentLength < self.allowedLength:
                        break
            
            #Check if snake ate the food 
            rx, ry = self.foodPoint
            if rx - self.wFood // 2 < cx < rx + self.wFood // 2 and ry - + self.hFood // 2 < cy < ry + self.hFood // 2:
                self.randomFoodLocation()
                self.allowedLength += 50
                self.score += 1 
                os.system('aplay crunch.wav &')
                print(self.score)
                

            #Draw Snake
            if self.points:
                for i, point in enumerate(self.points):
                    if i != 0:
                        cv2.line(imgMain, self.points[i - 1], self.points[i], (0, 0, 255), 20)
                cv2.circle(imgMain, self.points[-1], 20, (200, 0, 200), cv2.FILLED)
            #Draw Food
            rx, ry = self.foodPoint
            imgMain = cvzone.overlayPNG(imgMain, self.imgFood,(rx - self.wFood // 2, ry - self.hFood // 2))
            cvzone.putTextRect(imgMain, f"Your Score: {self.score}", [50,80], scale=3, thickness=3, offset=10)
            #Check for Collision  
            pts = np.array(self.points[:-2], np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(imgMain, [pts], False, (0, 200, 0), 3)
            minDistance = cv2.pointPolygonTest(pts, (cx, cy), True)
            
            
            if -1 <= minDistance <= 1:
                print('Hit') 
                os.system('killall aplay')
                os.system('aplay fail.wav &')
                self.gameOver = True
                self.points = [] #all points of the snake 
                self.lengths = [] #distance between each point
                self.currentLength = 0 #total length of the snake
                self.allowedLength = 150 #total allowed length 
                self.previousHead = 0, 0 #previous head point 
                self.randomFoodLocation()
        return imgMain


game = SnakeGameClass('donut.png')
os.system('aplay startgame.wav &')
while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img, flipType=False)
    
    if hands:
        lmList = hands[0]['lmList']
        pointIndex = lmList[8][0:2]
        img = game.update(img, pointIndex)
    cv2.imshow('Snake Game by Shubharthak', img)
    if cv2.waitKey(1) == ord('r'):
        os.system('aplay startgame.wav &')
        game.gameOver = False
    if cv2.waitKey(1) == ord('q'):
        break
    
    

# cap.release()
# cv2.destroyAllWindows()
