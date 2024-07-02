import threading
import __init__

import asyncio
from fastapi import FastAPI
import uvicorn
from packages.WhisperLive.whisper_live.client import TranscriptionClient
from reactivex import operators as ops
import argparse
from opencc import OpenCC
# 创建转换器，从繁体转为简体
cc = OpenCC('t2s')  # t2s 表示 Traditional Chine

app = FastAPI()

# 定義全域變數來儲存 TranscriptionClient 實例
transcription_client = None

history_segments = []
def last_segment_handler( last_segment):
    simplified_text = cc.convert(last_segment['text'])
    last_segment['text'] = simplified_text
    print(f"[Received] last_segment_subject : {last_segment['text']}")
    history_segments.append(last_segment)

def segment_handler( segment):
    print(f"[Received] segment_subject : {segment}")
    # resettable_timer.reset()

@app.get("/disconnect")
def disconnect():
    if transcription_client and transcription_client.client:
        transcription_client.close_all_clients()
        return {"status": "disconnected"}
    return {"error": "No transcription client available"}

@app.get("/connect")
def connect():
    if transcription_client and transcription_client.client:
        transcription_client.client.connect_websocket()
        start_transcription_client()
        return {"status": "reconnected"}
    else:
        pass
    return {"error": "No transcription client available"}

def start_transcription_client():
    # 使用多執行緒啟動 TranscriptionClient
    transcription_thread = threading.Thread(target=transcription_client)
    transcription_thread.start()
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', '-p',
                        type=int,
                        default=9090,
                        help="Websocket port to run the server on.")
    parser.add_argument('--backend', '-b',
                        type=str,
                        default='faster_whisper',
                        help='Backends from ["tensorrt", "faster_whisper"]')
    parser.add_argument('--faster_whisper_custom_model_path', '-fw',
                        type=str, default=None,
                        help="Custom Faster Whisper Model")
    parser.add_argument('--trt_model_path', '-trt',
                        type=str,
                        default=None,
                        help='Whisper TensorRT model path')
    parser.add_argument('--trt_multilingual', '-m',
                        action="store_true",
                        help='Boolean only for TensorRT model. True if multilingual.')
    parser.add_argument('--host', '-H',
                        type=str,
                        default="localhost",
                        help='Host for the server')
    args = parser.parse_args()

    if args.backend == "tensorrt":
        if args.trt_model_path is None:
            raise ValueError("Please Provide a valid tensorrt model path")

    
    # 初始化 TranscriptionClient
    transcription_client = TranscriptionClient(
        host=args.host,
        port=args.port,
        lang="zh",
        translate=False,
        model="small",
        use_vad=True
    )

    transcription_client.client.last_segment_behavior_subject.pipe(
        ops.filter(lambda last_segment: last_segment['text'] != '' and last_segment['text'] != '字幕by索兰娅'),
        ops.distinct_until_changed()
    ).subscribe(last_segment_handler)
    transcription_client.client.segment_behavior_subject.pipe(
        ops.filter(lambda segment: segment != '' and segment != '字幕by索兰娅'),
        ops.distinct_until_changed()
    ).subscribe(segment_handler)
    
    # start_transcription_client()

    # 在主線程中運行 FastAPI 應用程序
    config = uvicorn.Config(app, host="localhost", port=9001)
    server = uvicorn.Server(config)

    try:
        server.run()
    except KeyboardInterrupt:
        print("[INFO]: KeyboardInterrupt received. Shutting down...")
        if transcription_client:
            transcription_client.close_all_clients()