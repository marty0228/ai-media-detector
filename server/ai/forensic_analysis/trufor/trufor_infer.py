# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Copyright (c) 2023 Image Processing Research Group of University Federico II of Naples ('GRIP-UNINA').
#
# All rights reserved.
# This work should only be used for nonprofit purposes.
#
# By downloading and/or using any of these files, you implicitly agree to all the
# terms of the license, as specified in the document LICENSE.txt
# (included in this package) and online at
# http://www.grip.unina.it/download/LICENSE_OPEN.txt

"""
Created in September 2022
@author: fabrizio.guillaro
"""

# 표준 라이브러리 및 외부 라이브러리 import
import sys, os
import argparse
import numpy as np
from tqdm import tqdm
from glob import glob

import torch
from torch.nn import functional as F

# 현재 파일 기준 상위 폴더를 sys.path에 추가하여
# config.py, data_core.py 등을 import 가능하게 함
path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
if path not in sys.path:
    sys.path.insert(0, path)

# 설정 관련 함수/객체 import
from config import update_config
from config import _C as config

# 테스트용 데이터셋 클래스 import
from data_core import myDataset

# 명령행 인자 파서 설정
parser = argparse.ArgumentParser(description='Test TruFor')
parser.add_argument('-gpu', '--gpu', type=int, default=0, help='device, use -1 for cpu')
parser.add_argument('-in', '--input', type=str, default='../images',
                    help='can be a single file, a directory or a glob statement')
parser.add_argument('-out', '--output', type=str, default='../output', help='output folder')
parser.add_argument('-save_np', '--save_np', action='store_true', help='whether to save the Noiseprint++ or not')
parser.add_argument('opts', help="other options", default=None, nargs=argparse.REMAINDER)

# 명령행 인자 파싱 및 config 업데이트
args = parser.parse_args()
update_config(config, args)

# 자주 쓰는 인자들을 변수로 분리
input = args.input
output = args.output
gpu = args.gpu
save_np = args.save_np

# 수정 1:
# 기존에는 문자열 형태의 'cuda:0' / 'cpu'를 사용했는데,
# CPU/GPU 환경을 더 안전하게 처리하기 위해 torch.device 객체로 명확히 지정
# - gpu >= 0 이고 실제 CUDA 사용 가능할 때만 해당 GPU 사용
# - 그 외에는 CPU 사용
if args.gpu >= 0 and torch.cuda.is_available():
    device = torch.device(f'cuda:{args.gpu}')
else:
    device = torch.device('cpu')

# numpy 출력 포맷 설정
np.set_printoptions(formatter={'float': '{: 7.3f}'.format})

# GPU 사용 시 cudnn 설정 적용
if device.type != 'cpu':
    import torch.backends.cudnn as cudnn

    cudnn.benchmark = config.CUDNN.BENCHMARK
    cudnn.deterministic = config.CUDNN.DETERMINISTIC
    cudnn.enabled = config.CUDNN.ENABLED

# 입력 경로가 glob 패턴인지, 단일 파일인지, 폴더인지 판별하여
# 실제 처리할 이미지 파일 목록을 생성
if '*' in input:
    list_img = glob(input, recursive=True)
    list_img = [img for img in list_img if not os.path.isdir(img)]
elif os.path.isfile(input):
    list_img = [input]
elif os.path.isdir(input):
    list_img = glob(os.path.join(input, '**/*'), recursive=True)
    list_img = [img for img in list_img if not os.path.isdir(img)]
else:
    raise ValueError("input is neither a file or a folder")

# 테스트 데이터셋 / 데이터로더 생성
test_dataset = myDataset(list_img=list_img)
testloader = torch.utils.data.DataLoader(
    test_dataset,
    batch_size=1)  # 1 to allow arbitrary input sizes

# 설정 파일에서 모델 가중치 경로를 읽어옴
if config.TEST.MODEL_FILE:
    model_state_file = config.TEST.MODEL_FILE
else:
    raise ValueError("Model file is not specified.")

print('=> loading model from {}'.format(model_state_file))

# 수정 2:
# PyTorch 2.6부터 torch.load의 기본 weights_only 값이 바뀌어서
# 예전 체크포인트 로드 시 오류가 날 수 있으므로 weights_only=False 명시
# 또한 map_location에 위에서 만든 device를 그대로 사용
checkpoint = torch.load(
    model_state_file,
    map_location=device,
    weights_only=False
)

# config에 지정된 모델 이름에 맞춰 모델 생성
if config.MODEL.NAME == 'detconfcmx':
    from models.cmx.builder_np_conf import myEncoderDecoder as confcmx
    model = confcmx(cfg=config)
else:
    raise NotImplementedError('Model not implemented')

# 체크포인트의 state_dict를 모델에 로드
model.load_state_dict(checkpoint['state_dict'])

# 수정 3:
# 기존 .cuda(...) 대신 .to(device)를 사용하여
# CPU/GPU 어느 환경에서도 동일하게 동작하도록 변경
model = model.to(device)

# 추론 모드에서 gradient 계산 비활성화
with torch.no_grad():
    for index, (rgb, path) in enumerate(tqdm(testloader)):
        # filename_img = test_dataset.get_filename(index)

        # output이 확장자가 없는 경로라면 "출력 폴더"로 간주
        # 원본 입력 구조를 최대한 유지하여 .npz 파일 경로 생성
        if os.path.splitext(os.path.basename(output))[1] == '':
            path = path[0]
            root = input.split('*')[0]

            if os.path.isfile(input):
                # 단일 파일 입력일 때는 파일명만 사용해서 output 폴더 아래 저장
                sub_path = os.path.basename(path)
            else:
                sub_path = path.replace(root, '').strip()

                # Windows/Unix 경로 구분자 모두 처리
                if sub_path.startswith('/') or sub_path.startswith('\\'):
                    sub_path = sub_path[1:]

            filename_out = os.path.join(output, sub_path) + '.npz'
        else:
            filename_out = output

        # 확장자가 .npz가 아니면 자동으로 .npz 추가
        if not filename_out.endswith('.npz'):
            filename_out = filename_out + '.npz'

        # 기본적으로 기존 결과 파일이 있으면 덮어쓰지 않음
        if not (os.path.isfile(filename_out)):
            try:
                # 수정 4:
                # 입력 텐서를 .cuda(...) 대신 .to(device)로 이동
                rgb = rgb.to(device)

                # 모델 평가 모드 설정
                model.eval()

                det = None
                conf = None

                # 모델 추론 수행
                pred, conf, det, npp = model(rgb)

                # conf 후처리
                if conf is not None:
                    conf = torch.squeeze(conf, 0)
                    conf = torch.sigmoid(conf)[0]
                    conf = conf.cpu().numpy()

                # noiseprint++ 결과 후처리
                if npp is not None:
                    npp = torch.squeeze(npp, 0)[0]
                    npp = npp.cpu().numpy()

                # detection score 후처리
                if det is not None:
                    det_sig = torch.sigmoid(det).item()

                # segmentation map 후처리
                pred = torch.squeeze(pred, 0)
                pred = F.softmax(pred, dim=0)[1]
                pred = pred.cpu().numpy()

                # 저장할 결과 딕셔너리 구성
                out_dict = dict()
                out_dict['map'] = pred
                out_dict['imgsize'] = tuple(rgb.shape[2:])
                if det is not None:
                    out_dict['score'] = det_sig
                if conf is not None:
                    out_dict['conf'] = conf
                if save_np:
                    out_dict['np++'] = npp

                # 출력 폴더 생성 후 npz 저장
                from os import makedirs

                makedirs(os.path.dirname(filename_out), exist_ok=True)
                np.savez(filename_out, **out_dict)

            # 원본 코드의 예외 처리 방식 유지
            except:
                import traceback
                traceback.print_exc()
                pass