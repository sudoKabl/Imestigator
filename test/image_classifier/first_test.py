import tensorflow as tf
import os
import cv2
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image
import time

# GPUs verbrauche nicht 100% vmem
gpus = tf.config.experimental.list_physical_devices('GPU')
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)
    
data_dir = "D:\\Hochschule\\Bachelorarbeit\\training_img"
image_exts = ('jpeg', 'jpg', 'bmp', 'png')

# Image vorverarbeitung hier (schlechte löschen, prüfen ob man öffnen kann)

if False:
    for image_class in os.listdir(data_dir):
        for image in os.listdir(os.path.join(data_dir, image_class)):
            image_path = os.path.join(data_dir, image_class, image)
            try:
                if not image.endswith(image_exts):
                    os.remove(image_path)
                    print(image_path)
                    continue
                
                #img = cv2.imread(image_path)
                img = Image.open(image_path)
                img = img.convert("RGB")
                img.save(image_path)
            except Exception as e:
                print("Issue with {}".format(image_path))
if False:
    # Data pipeline
    data = tf.keras.utils.image_dataset_from_directory(data_dir, batch_size=32, image_size=(256, 256))

    # Access to pipeline
    data_iterator = data.as_numpy_iterator()

    # One batch of batch_size * (image as np array, labels)
    batch = data_iterator.next()

    # Preprocessing: x = images, y = labels
    # Happens on pipeline
    #data = data.map(lamda x, y: (x/255, y))


    fig, ax = plt.subplots(ncols=4, figsize=(20,20))
    for idx, img in enumerate(batch[0][:4]):
        ax[idx].imshow(img.astype(int))
        ax[idx].title.set_text(batch[1][idx])
        
    plt.show()
    # 1 = real
    # 0 = fake

if True:
    # Data pipeline
    data = tf.keras.utils.image_dataset_from_directory(data_dir, batch_size=32, image_size=(256, 256))

    # Access to pipeline
    data_iterator = data.as_numpy_iterator()

    # One batch of batch_size * (image as np array, labels)
    #batch = data_iterator.next()

    # Preprocessing: x = images, y = labels
    # Happens on pipeline
    #data = data.map(lamda x, y: (x/255, y))



    train_size = int(len(data)*.7)
    val_size = int(len(data)*.2)+1
    test_size = int(len(data)*.1)


    if train_size + val_size + test_size != len(data):
        print("len error:")
        print(train_size, val_size, test_size)
        print(len(data))
        exit
        
    train = data.take(train_size)
    val = data.skip(train_size).take(val_size)
    test = data.skip(train_size + val_size).take(test_size)

    model = tf.keras.models.Sequential()

    model.add(tf.keras.layers.Conv2D(16, (3,3), 1, activation='relu', input_shape=(256,256,3)))
    model.add(tf.keras.layers.MaxPooling2D())

    model.add(tf.keras.layers.Conv2D(32, (3,3), 1, activation='relu'))
    model.add(tf.keras.layers.MaxPooling2D())

    model.add(tf.keras.layers.Conv2D(16, (3,3), 1, activation='relu'))
    model.add(tf.keras.layers.MaxPooling2D())

    model.add(tf.keras.layers.Flatten())

    model.add(tf.keras.layers.Dense(256, activation='relu'))
    model.add(tf.keras.layers.Dense(1, activation='sigmoid'))

    model.compile('adam', loss=tf.losses.BinaryCrossentropy(), metrics=['accuracy'])

    print(model.summary())

    logdir = "D:\\Hochschule\\Bachelorarbeit\\trainig_else"
    tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=logdir)

    hist = model.fit(train, epochs=20, validation_data=val, callbacks=[tensorboard_callback])

    fig = plt.figure()
    plt.plot(hist.history['loss'], color='teal', label='loss')
    plt.plot(hist.history['val_loss'], color='orange', label='val_loss')
    fig.suptitle('Loss', fontsize=20)
    plt.legend(loc="upper left")
    plt.show()
    
    fig = plt.figure()
    plt.plot(hist.history['accuracy'], color='teal', label='accuracy')
    plt.plot(hist.history['val_accuracy'], color='orange', label='val_accuracy')
    fig.suptitle('Accuracy', fontsize=20)
    plt.legend(loc="upper left")
    plt.show()
    
    pre = tf.keras.metrics.Precision()
    re = tf.keras.metrics.Recall()
    acc = tf.keras.metrics.BinaryAccuracy()
    
    for batch in test.as_numpy_iterator(): 
        X, y = batch
        yhat = model.predict(X)
        pre.update_state(y, yhat)
        re.update_state(y, yhat)
        acc.update_state(y, yhat)
        
    print(pre.result(), re.result(), acc.result())
    
    img = cv2.imread("C:\\Users\\Kapsr\\Pictures\\test_image_folder\\klon_bearbeitet_2.png")
    
    resize = tf.image.resize(img, (256,256))
    plt.imshow(resize.numpy().astype(int))
    plt.show()
    
    yhat = model.predict(np.expand_dims(resize/255, 0))
    
    if yhat > 0.5: 
        print(f'Predicted class is real')
    else:
        print(f'Predicted class is fake')
        
    model.save(os.path.join(data_dir, "model_1.h5"))