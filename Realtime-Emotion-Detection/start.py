import sys
import os
import numpy as np
import pandas as pd
from keras.models import Sequential
from keras.layers import Dense,Dropout,Activation,Flatten
from keras.layers import Conv2D,MaxPooling2D,BatchNormalization
from keras.losses import categorical_crossentropy
from keras.optimizers import Adam
from keras.regularizers import l2
from keras.utils import np_utils
from keras.models import model_from_json
from keras.preprocessing import image
df=pd.read_csv('fer2013.csv')
#print(df.info())
#print(df["Usage"].value_counts())
#print(df.head())
X_train,train_y,X_test,test_y=[],[],[],[]
for index,row in df.iterrows():
	val=row['pixels'].split(" ")
	try:
		if 'training' in row['Usage']:
			X_train.append(np.array(val,'float32'))
			train_y.append(row['emotion'])
		elif 'PublicTest' in row['Usage']:
			X_test.append(np.array(val,'float32'))
			test_y.append(row['emotion'])
	except:
		print(f"error occured at index:{index} and row:{row}")
#print(f"X_train sample data:{X_train[0:2]}")
#print(f"train_y sample data:{train_y[0:2]}")
#print(f"X_test sample data:{X_test[0:2]}")
#print(f"test_y sample data:{test_y[0:2]}")


X_train=np.array(X_train,'float32')
train_y=np.array(train_y,'float32')
X_test=np.array(X_test,'float32')
test_y=np.array(test_y,'float32')
#Normalizing data between 0 and 1
X_train-=np.mean(X_train,axis=0)
X_train/=np.std(X_train,axis=0)
X_test-=np.mean(X_test,axis=0)
X_test/=np.std(X_test,axis=0)
num_features=64
num_labels=7
batch_size=64
epochs=30
width,height=48,48


X_train=X_train.reshape(X_train.shape[0],width,height,1)
X_test=X_test.reshape(X_test.shape[0],width,height,1)

train_y=np_utils.to_categorical(train_y,num_classes=num_labels)
test_y=np_utils.to_categorical(test_y,num_classes=num_labels)


#designing in cnn
model=Sequential()
#1st layer
model.add(Conv2D(num_features,kernel_size=(3,3),activation='relu',input_shape=(X_train.shape[1:])))
model.add(Conv2D(num_features,kernel_size=(3,3),activation='relu'))
model.add(MaxPooling2D(pool_size=(2,2),strides=(2,2)))
model.add(Dropout(0.5))

#2nd convolutional layer

model.add(Conv2D(num_features,(3,3),activation='relu'))
model.add(Conv2D(num_features,(3,3),activation='relu'))
model.add(MaxPooling2D(pool_size=(2,2),strides=(2,2)))
model.add(Dropout(0.5))

#3rd convolutional layer

model.add(Conv2D(2*num_features,(3,3),activation='relu'))
model.add(Conv2D(2*num_features,(3,3),activation='relu'))
model.add(MaxPooling2D(pool_size=(2,2),strides=(2,2)))

model.add(Flatten())

model.add(Dense(2*2*2*2*num_features,activation='relu'))
model.add(Dropout(0.2))
model.add(Dense(2*2*2*2*num_features,activation='relu'))
model.add(Dropout(0.2))

model.add(Dense(num_labels,activation='softmax'))
model.compile(loss=categorical_crossentropy,optimizer=Adam(),metrics=['accuaracy'])
model.fit(X_train,train_y,
	batch_size=batch_size,
	epochs=epochs,
	verbose=1,
	validation_data=(X_test,test_y),
	shuffle=True)
#saving model

fer_json=model.to_json()
with open("fer.json","w")as json_file:
	json_file.write(fer_json)
model.save_weights("fer.h5")

face_haar_cascade=cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
 
cap=cv2.VideoCapture(0)

while True:
	ret,test_img=cap.read()#captures frame and returns boolean value
	if not ret:
		continue
	gray_img=cv2.cvtColor(test_img,cv2.COLOR_BGR2GRAY)
	face_detected=face_haar_cascade.detectMultiScale(gray_img,1.32,5)
	
	for (x,y,w,h) in faces_detected:
		cv2.rectangle(test_img,(x,y),(x+w+y+h),(255,0,0),thickness=7)
		roi_gray=gray_img[y:y+w,x:x+h]#cropping region of interest i.e. face area from image
		roi_gray=cv2.resize(roi_gray,(48,48))
		img_pixels= image.img_to_array(roi_gray)
		img_pixels= np.expand_dims(img_pixels, axis=0)
		img_pixels /=255
		predictions=model.predict(img_pixels)
		#find max indexed array
		max_index=np.argmax(predictions[0])
		
		emotions=('angry','disgust','fear','happy','sad','surprise','neutral')
		predicted_emotion=emotions[max_index]
		cv2.putText(test_img, predicted_emotion,(int(x),int(y)),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)


	resized_img=cv2.resize(test_img,(1000,700))
	cv2.imshow('Facial emotion analysis',resized_img)

	if cv2.waitkey(10)==ord('q'):#wait until 'q'key is pressed
		break
cap.release()
cv2.destroyAllWindows
