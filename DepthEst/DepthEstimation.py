from yolov4.tf import YOLOv4
from tqdm import tqdm
import tensorflow as tf
import time
import numpy as np
import cv2
import glob
import warnings


path='/Users/aarsh/Desktop/Autonomous Vehicles/stereo_vision_course'
path2='/Users/aarsh/Desktop/Autonomous Vehicles/stereo_vision_course/data/Archive3'


def compute_disparity(image, img_pair, num_disparities=6*16, block_size=11, window_size=6):
    new_image = cv2.StereoSGBM_create(minDisparity=0,numDisparities=num_disparities,blockSize=block_size,P1=8 * 3 * window_size **2,P2=  32* 3 * window_size ** 2,mode=cv2.STEREO_SGBM_MODE_SGBM_3WAY )
    new_image = new_image.compute(image,img_pair).astype(np.float32)/16 
    return new_image

def get_calibration_parameters():
    file = glob.glob(path+"/data/calib/*.txt")
    with open(file[0], 'r') as f:
        fin = f.readlines()
        for line in fin:
            if line[:2] == 'P2':
                p_left = np.array(line[4:].strip().split(" ")).astype('float32').reshape(3,-1)
            elif line[:2] == 'P3':
                p_right = np.array(line[4:].strip().split(" ")).astype('float32').reshape(3,-1)
    return p_left, p_right


def decompose_projection_matrix(p):    
    k,r,t,_,_,_,_=cv2.decomposeProjectionMatrix(p)
    t=t/t[3]
    return k, r, t


def calc_depth_map(disp_left, k_left, t_left, t_right):
    f = k_left[0, 0]
    b = abs(t_left[0] - t_right[0]) 
    disp_left[disp_left == 0] = 0.1
    disp_left[disp_left == -1] = 0.1
    depth_map = np.ones(disp_left.shape, np.single)
    depth_map[:] = f * b / disp_left[:]
    return depth_map

def make_model():
    yolo = YOLOv4(tiny=True)
    yolo.classes = path +"/Yolov4/coco.names"
    yolo.make_model()
    yolo.load_weights(path + "/Yolov4/yolov4-tiny.weights", weights_type="yolo")
    return yolo

def run_obstacle_detection(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    resized_image = yolo.resize_image(img)
    resized_image = resized_image / 255.
    input_data = resized_image[np.newaxis, ...].astype(np.float32)
    candidates = yolo.model.predict(input_data)

    _candidates = []
    for candidate in candidates:
        batch_size = candidate.shape[0]
        grid_size = candidate.shape[1]
        _candidates.append(tf.reshape(candidate, shape=(1, grid_size * grid_size * 3, -1)))
        candidates = np.concatenate(_candidates, axis=1)
        pred_bboxes = yolo.candidates_to_pred_bboxes(candidates[0], iou_threshold=0.35, score_threshold=0.40)
        pred_bboxes = pred_bboxes[~(pred_bboxes==0).all(1)] 
        pred_bboxes = yolo.fit_pred_bboxes_to_original(pred_bboxes, img.shape)
        result = yolo.draw_bboxes(img, pred_bboxes)
    return result, pred_bboxes


def find_distances(depth_map, pred_bboxes, img):
    depth_list = []
    h, w, _ = img.shape
    for box in pred_bboxes:
        depth_list.append(depth_map[int(box[1]*h)][int(box[0]*w)])
    return depth_list

def add_depth(depth_list, result, pred_bboxes):
    h, w, _ = result.shape
    res = result.copy()
    for i, distance in enumerate(depth_list):
        cv2.putText(res, '{0:.2f} m'.format(distance), (int(pred_bboxes[i][0]*w - pred_bboxes[i][2]*w*0.5),int(pred_bboxes[i][1]*h)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2, cv2.LINE_AA)    
    return res


def pipeline (img_left, img_right):
    img_left_gray = cv2.cvtColor(img_left, cv2.COLOR_BGR2GRAY)
    img_right_gray = cv2.cvtColor(img_right, cv2.COLOR_BGR2GRAY)
    disparity = compute_disparity(img_left_gray, img_pair=img_right_gray, num_disparities=112, block_size=5, window_size=7)
    p_left, p_right= get_calibration_parameters()
    k_left, r_left, t_left = decompose_projection_matrix(p_left)
    k_right, r_right, t_right = decompose_projection_matrix(p_right)
    depth_map = calc_depth_map(disparity, k_left, t_left, t_right)
    result, pred_bboxes = run_obstacle_detection(img_left)
    depth_list = find_distances(depth_map, pred_bboxes, img_left)
    final = add_depth(depth_list, result, pred_bboxes)
    return final

def output(left_path,right_path,output_path):
    warnings.filterwarnings("ignore")
    start_time=time.time()
    left_video = sorted(glob.glob( left_path + "/data/*.png"))
    right_video = sorted(glob.glob(right_path + "/data/*.png"))
    h,w,_=cv2.imread(left_video[0]).shape
    result_video = []
    for idx in tqdm(range(len(left_video)),desc="Processing Video!"):
        left_img = cv2.imread(left_video[idx])
        right_img = cv2.imread(right_video[idx])
        result_video.append(pipeline(left_img, right_img))

    out = cv2.VideoWriter(output_path + "/out.mp4",cv2.VideoWriter_fourcc(*'DIVX'), 15, (w,h))
    for i in range(len(result_video)):
        out.write(cv2.cvtColor(result_video[i], cv2.COLOR_BGR2RGB))
    out.release()
    exec_time = time.time() - start_time
    print("time: {:.2f} mins".format(exec_time/60))


if __name__ == '__main__':
    yolo=make_model()
    output(f"{path2}/image_02",f"/{path2}/image_03",f"{path}/output")



