import csv
import cv2
import numpy as np
import matplotlib.pyplot as plt
import sklearn
from keras.models import Sequential, Model
from keras.layers import Flatten, Dense, Lambda
from keras.layers import Cropping2D
from keras.layers import Convolution2D
from keras.layers.pooling import MaxPooling2D
from keras.layers import Dropout
from keras.optimizers import Adam
samples = []
bad_record_count = 0
with open('driving_log.csv') as csvfile:
    reader = csv.reader(csvfile)
    for line in reader:
        samples.append(line)

from sklearn.model_selection import train_test_split
train_samples, validation_samples = train_test_split(samples, test_size=0.2) 
def generator(samples, batch_size=32):
    num_samples = len(samples)
    while 1: # Loop forever so the generator never terminates
        sklearn.utils.shuffle(samples)
        for offset in range(0, num_samples, batch_size):
            batch_samples = samples[offset:offset+batch_size]
            images=[]
            angles=[]
            for batch_sample in batch_samples:
                try:
                    steering_center = float(batch_sample[3])
                    # create adjusted steering measurements for the side camera images
                    correction =0.2 #
                    steering_left = steering_center + correction
                    steering_right = steering_center - correction

                    # read in images from center, left and right cameras
                    path = "./"
                    img_center = cv2.imread(path + batch_sample[0])
                    img_left = cv2.imread(path + batch_sample[1])
                    img_right = cv2.imread(path + batch_sample[2])
                
                    # add images and angles to data set
                    # img_center, img_left, img_right
                    # steering_center, steering_left, steering_right
                    images.append(img_center)
                    angles.append(steering_center)
                    #images.append(cv2.flip(img_center, 1))
                    #angles.append(steering_center*-1.0)                

                    images.append(img_left)
                    angles.append(steering_left)
                    #images.append(cv2.flip(img_left, 1))
                    #angles.append(steering_left*-1.0)                

                    images.append(img_right)
                    angles.append(steering_right)
                    #images.append(cv2.flip(img_right, 1))
                    #angles.append(steering_right*-1.0)
                except:
                    bad_record_count =+ 1

            X_train = np.array(images)
            y_train = np.array(angles)
            yield sklearn.utils.shuffle(X_train, y_train)


			
# compile and train the model using the generator function
train_generator = generator(train_samples, batch_size=32)
validation_generator = generator(validation_samples, batch_size=32)

ch, row, col = 3, 160, 320  # Trimmed image format

model = Sequential()
model.add(Lambda(lambda x: (x / 255.0) - 0.5,input_shape=(row, col, ch)))
model.add(Cropping2D(cropping=((70,25), (0,0)), input_shape=(160,320, 3)))
model.add(Convolution2D(24,5,5,subsample=(2,2),activation="relu"))
model.add(Convolution2D(36,5,5,subsample=(2,2),activation="relu"))
model.add(Convolution2D(48,5,5,subsample=(2,2),activation="relu"))
model.add(Convolution2D(64,3,3,activation="relu"))
model.add(Convolution2D(64,3,3,activation="relu"))
model.add(Flatten())
model.add(Dropout(0.4))
model.add(Dense(1124,activation="relu"))
model.add(Dropout(0.4))
model.add(Dense(100, activation="relu"))
model.add(Dense(50, activation="relu"))
model.add(Dense(1))

optimizer = Adam(lr=0.001)
model.compile(loss = 'mse', optimizer = optimizer, metrics=['accuracy'] )
model.save('model.h5')

history_object = model.fit_generator(train_generator, samples_per_epoch = len(train_samples), 
                    validation_data = validation_generator, nb_val_samples = len(validation_samples),
                    nb_epoch=3, verbose=1)


### print the keys contained in the history object
print(history_object.history.keys())
print("Found " , bad_record_count, " bad records ")
### plot the training and validation loss for each epoch
#plt.plot(history_object.history['loss'])
#plt.plot(history_object.history['val_loss'])
#plt.title('model mean squared error loss')
#plt.ylabel('mean squared error loss')
#plt.xlabel('epoch')
#plt.legend(['training set', 'validation set'], loc='upper right')
#plt.show()