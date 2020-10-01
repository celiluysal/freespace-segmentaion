import numpy as np
import cv2
import torch
import glob
import matplotlib.pyplot as plt
from PIL import Image

# MASK_DIR = "../data/masks"
# IMG_DIR = "../data/images"
MASK_DIR = "../data/test_masks"
IMG_DIR = "../data/test_images"

def tensorize_image(image_path, output_shape, cuda=False):
    batch_images = []
    for file_name in image_path:
        img = cv2.imread(file_name, cv2.IMREAD_COLOR)
        img = cv2.resize(img,output_shape)
        torchlike_image = torchlike_data(img)

        batch_images.append(torchlike_image)

    batch_images = np.array(batch_images)
    torch_image = torch.from_numpy(batch_images).float()
    if cuda:
        torch_image = torch_image.cuda()
    return torch_image 
    #[4765, 20, 20, 3] [B,W,H,C]
    

def tensorize_mask(mask_path, output_shape ,n_class, cuda=False):
    batch_masks = list()
    for file_name in mask_path:
        # print("file", file_name)
        mask = cv2.imread(file_name, cv2.IMREAD_GRAYSCALE)
        mask = cv2.resize(mask, output_shape)
        mask = mask / 255
        encoded_mask = one_hot_encoder(mask, n_class)  
        # print(encoded_mask.shape)
        torchlike_mask = torchlike_data(encoded_mask) #[C,W,H]

        batch_masks.append(torchlike_mask)      
  
    batch_masks = np.array(batch_masks, dtype=np.int)
    # print("mask enc batch", batch_masks)
    torch_mask = torch.from_numpy(batch_masks).float()
    # print("mask torch", torch_mask)
    if cuda:
        torch_mask = torch_mask.cuda()
    return torch_mask
    #[4765, 20, 20, 2] [B,W,H,C] 

def one_hot_encode(data, n_class):
    encoded_data = np.zeros((data.shape[0], data.shape[1], n_class), dtype=np.int)
    encoded_labels = [[1,0],[0,1]]
    # for lbl in range(n_class):
    #     encoded_label = [0] * n_class 
    #     encoded_label[lbl] = 1
    #     encoded_labels.append(encoded_label)
    
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            if ((data[i][j] == 0).all()):
                encoded_data[i, j] = encoded_labels[0]
            else: #((data[i][j] == 1).all()):
                encoded_data[i, j] = encoded_labels[1]
    return encoded_data

def one_hot_encoder(data, n_class):
    encoded_data = np.zeros((*data.shape, n_class), dtype=np.int) # (width, height, number_of_class)'lık bir array tanımlıyorum. 

    encoded_labels = [[0,1], [1,0]]
    for lbl in range(n_class):

        encoded_label = encoded_labels[lbl] # lbl = 0 için (arkaplan) [1, 0] labelini oluşturuyorum, 
                                # lbl = 1 için (freespace) [0, 1] labelini oluşturuyorum.
        numerical_class_inds = data[:,:] == lbl # lbl = 0 için data'nın 0'a eşit olduğu w,h ikililerini alıyorum diyelim ki (F).
                                                # lbl = 1 için data'nın 1'e eşit olduğu w,h ikililerini alıyorum diyelim ki (O).
        encoded_data[numerical_class_inds] = encoded_label # lbl = 0 için tüm F'in sahip olduğu tüm w,h ikililerini [1, 0]'a eşitliyorum.
                                                            # lbl = 1 için tüm O'un sahip olduğu tüm w,h ikililerini [0, 1]'e eşitliyorum.
    return encoded_data

def decode_and_convert_image(data, n_class):
    decoded_data_list = []
    decoded_data = np.zeros((data.shape[2], data.shape[3]), dtype=np.int)

    for tensor in data:
        for i in range(len(tensor[0])):
            for j in range(len(tensor[1])):
                if (tensor[1][i,j] == 0):
                    decoded_data[i, j] = 0
                else: #(tensor[1][i,j] == 1):
                    decoded_data[i, j] = 255
        print(decoded_data)
        image = Image.fromarray(np.uint8(decoded_data), "L")
        # image.show()
        decoded_data_list.append(image)
    
    # decoded_data_list[0].show() 

    return decoded_data_list
    



def torchlike_data(data):
    n_channels = data.shape[2]
    torchlike_data = np.empty((n_channels, data.shape[0], data.shape[1]))
    for ch in range(n_channels):
        torchlike_data[ch] = data[:,:,ch]
    # print((torchlike_data).shape)
    return torchlike_data

def image_mask_check(image_path_list, mask_path_list):
    for image_path, mask_path in zip(image_path_list, mask_path_list):
        image_name = image_path.split('/')[-1].split('.')[0]
        mask_name  = mask_path.split('/')[-1].split('.')[0]
        assert image_name == mask_name, "Image and mask name does not match {} - {}".format(image_name, mask_name)

if __name__ == '__main__':
    
    # image_file_names = glob.glob(IMG_DIR + "/*")
    # image_file_names.sort()
    # batch_image_list = image_file_names[:5] #first n
    # batch_image_tensor = tensorize_image(batch_image_list, (20,20))
    
    # print(batch_image_tensor.dtype)
    # print(type(batch_image_tensor))
    # print(batch_image_tensor.shape)

    # print("------------")    
    
    mask_file_names = glob.glob(MASK_DIR + "/*")
    mask_file_names.sort()
    batch_mask_list = mask_file_names[:2] #first n
    batch_mask_tensor = tensorize_mask(batch_mask_list, (224,224), 2)

    
    image_list = decode_and_convert_image(batch_mask_tensor,2)
    print(type(image_list[0]))
    img = image_list[0]
    plt.imshow(img, cmap="gray")
    plt.show()

    # batch_mask_tensor = batch_mask_tensor.permute(0, 3, 2, 1) # from NHWC to NCHW  
    # plt.imshow(batch_mask_tensor.permute(1, 2, 0))
    # print("asd",batch_mask_tensor[0].shape)
    # mask_tensor = batch_mask_tensor[0]
    # print("mask tensor ", mask_tensor.shape)
    # mask_tensor = mask_tensor.permute(1, 2, 0).numpy()
    # print("mask tensor ", mask_tensor.shape)
    # print("mask tensor type", type(mask_tensor))
    # print(mask_tensor)
    # plt.imshow(mask_tensor, cmap=plt.cm.gray)
    
    
    print(batch_mask_tensor.dtype)
    print(type(batch_mask_tensor))
    print(batch_mask_tensor.shape)  


