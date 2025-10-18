"""
Flask 网页服务器，提供视频翻译程序的 GUI 界面
"""

import os
import json
import logging
from pathlib import Path
from threading import Thread
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from .single_video_translation import VideoTranslator, Device

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建 Flask 应用
app = Flask(__name__, template_folder='templates', static_folder='static')

# 配置
UPLOAD_FOLDER = Path('uploads')
OUTPUT_FOLDER = Path('outputs')
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv'}
MAX_FILE_SIZE = 5 * 1024 * 1024 * 1024  # 5GB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# 创建必要的目录
UPLOAD_FOLDER.mkdir(exist_ok=True)
OUTPUT_FOLDER.mkdir(exist_ok=True)

# 全局任务管理
tasks = {}

def allowed_file(filename):
    """检查文件是否被允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_video_task(task_id, video_path, model_size, device, manual_translate=False):
    """后台处理视频的任务函数"""
    try:
        tasks[task_id]['status'] = 'processing'
        tasks[task_id]['progress'] = 10
        
        # 创建转录器实例
        translator = VideoTranslator(
            video_path,
            model_size=model_size,
            device=Device(device),
            verbose=True
        )
        
        tasks[task_id]['progress'] = 20
        tasks[task_id]['message'] = '初始化环境...'
        
        # 设置输出目录
        output_dir = OUTPUT_FOLDER / Path(video_path).stem
        output_dir.mkdir(exist_ok=True)
        translator.env_setup(output_dir)
        
        tasks[task_id]['progress'] = 30
        tasks[task_id]['message'] = '提取音频...'
        translator.get_audio_stream()
        
        tasks[task_id]['progress'] = 50
        tasks[task_id]['message'] = '获取视频分辨率...'
        translator.get_resolution()
        
        tasks[task_id]['progress'] = 60
        tasks[task_id]['message'] = '生成转录...'
        translator.whisper_transcription()
        
        if manual_translate:
            tasks[task_id]['progress'] = 80
            tasks[task_id]['message'] = '等待翻译...'
            translator.split_transcription()
            tasks[task_id]['translation_file'] = str(translator.translation_file)
            tasks[task_id]['status'] = 'waiting_translation'
            tasks[task_id]['progress'] = 100
        else:
            tasks[task_id]['progress'] = 80
            tasks[task_id]['message'] = '生成字幕...'
            translator.generate_subtitle()
            
            tasks[task_id]['progress'] = 90
            tasks[task_id]['message'] = '压制字幕到视频...'
            translator.compress_subtitle()
            
            tasks[task_id]['output_file'] = str(translator.ass_path)
            tasks[task_id]['status'] = 'completed'
            tasks[task_id]['progress'] = 100
            tasks[task_id]['message'] = '完成！'
        
    except Exception as e:
        logger.error(f"Task {task_id} failed: {str(e)}", exc_info=True)
        tasks[task_id]['status'] = 'failed'
        tasks[task_id]['error'] = str(e)
        tasks[task_id]['progress'] = 0

# 路由

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_video():
    """上传视频文件"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有选择文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '文件名为空'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': '不支持的文件格式，请上传视频文件'}), 400
        
        # 保存文件
        filename = secure_filename(file.filename)
        filepath = UPLOAD_FOLDER / filename
        file.save(filepath)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'filepath': str(filepath)
        }), 200
    
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/process', methods=['POST'])
def process_video():
    """开始处理视频"""
    try:
        data = request.json
        filepath = data.get('filepath')
        model_size = data.get('model_size', 'large-v3')
        device = data.get('device', 'cpu')
        manual_translate = data.get('manual_translate', False)
        
        if not filepath or not Path(filepath).exists():
            return jsonify({'error': '视频文件不存在'}), 400
        
        # 生成任务 ID
        task_id = Path(filepath).stem + '_' + str(int(__import__('time').time()))
        
        # 创建任务
        tasks[task_id] = {
            'status': 'queued',
            'progress': 0,
            'message': '等待中...',
            'filepath': filepath,
            'model_size': model_size,
            'device': device
        }
        
        # 在后台线程中处理
        thread = Thread(
            target=process_video_task,
            args=(task_id, filepath, model_size, device, manual_translate),
            daemon=True
        )
        thread.start()
        
        return jsonify({
            'success': True,
            'task_id': task_id
        }), 200
    
    except Exception as e:
        logger.error(f"Process error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/task/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """获取任务状态"""
    try:
        if task_id not in tasks:
            return jsonify({'error': '任务不存在'}), 404
        
        task = tasks[task_id]
        return jsonify({
            'task_id': task_id,
            'status': task.get('status'),
            'progress': task.get('progress', 0),
            'message': task.get('message', ''),
            'error': task.get('error'),
            'translation_file': task.get('translation_file'),
            'output_file': task.get('output_file')
        }), 200
    
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload-translation/<task_id>', methods=['POST'])
def upload_translation(task_id):
    """上传翻译文件并继续处理"""
    try:
        if task_id not in tasks:
            return jsonify({'error': '任务不存在'}), 404
        
        if 'file' not in request.files:
            return jsonify({'error': '没有选择文件'}), 400
        
        file = request.files['file']
        if not file.filename.endswith('.json'):
            return jsonify({'error': '请上传 JSON 格式的翻译文件'}), 400
        
        # 验证 JSON 格式
        translation_data = json.load(file)
        if 'metadata' not in translation_data or 'transcriptions' not in translation_data:
            return jsonify({'error': '翻译文件格式不正确'}), 400
        
        # 保存翻译文件
        task = tasks[task_id]
        translation_path = Path(task['filepath']).parent / f'translation_{task_id}.json'
        file.seek(0)
        file.save(translation_path)
        
        # 继续处理
        thread = Thread(
            target=continue_with_translation,
            args=(task_id, translation_path),
            daemon=True
        )
        thread.start()
        
        return jsonify({
            'success': True,
            'message': '翻译文件已上传，开始处理...'
        }), 200
    
    except json.JSONDecodeError:
        return jsonify({'error': 'JSON 格式错误'}), 400
    except Exception as e:
        logger.error(f"Translation upload error: {str(e)}")
        return jsonify({'error': str(e)}), 500

def continue_with_translation(task_id, translation_path):
    """使用翻译文件继续处理"""
    try:
        task = tasks[task_id]
        task['status'] = 'processing'
        task['progress'] = 50
        task['message'] = '加载翻译...'
        
        translator = VideoTranslator(
            task['filepath'],
            model_size=task['model_size'],
            device=Device(task['device'])
        )
        
        output_dir = OUTPUT_FOLDER / Path(task['filepath']).stem
        translator.env_setup(output_dir)
        
        task['progress'] = 60
        task['message'] = '应用翻译...'
        if translator.load_from_translation_file(translation_path):
            task['progress'] = 80
            task['message'] = '生成字幕...'
            translator.generate_subtitle()
            
            task['progress'] = 90
            task['message'] = '压制字幕到视频...'
            translator.compress_subtitle()
            
            task['output_file'] = str(translator.ass_path)
            task['status'] = 'completed'
            task['progress'] = 100
            task['message'] = '完成！'
        else:
            raise Exception('无法加载翻译文件')
    
    except Exception as e:
        logger.error(f"Continue with translation error: {str(e)}", exc_info=True)
        task['status'] = 'failed'
        task['error'] = str(e)
        task['progress'] = 0

@app.route('/api/download/<path:filepath>', methods=['GET'])
def download_file(filepath):
    """下载文件"""
    try:
        file_path = Path(filepath)
        if not file_path.exists():
            return jsonify({'error': '文件不存在'}), 404
        
        return send_file(file_path, as_attachment=True)
    
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/models', methods=['GET'])
def get_models():
    """获取可用的模型列表"""
    models = ['tiny', 'base', 'small', 'medium', 'large', 'large-v2', 'large-v3']
    return jsonify({'models': models}), 200

@app.route('/api/devices', methods=['GET'])
def get_devices():
    """获取可用的设备列表"""
    devices = ['cpu', 'cuda']
    return jsonify({'devices': devices}), 200

def run_server(host='127.0.0.1', port=5000, debug=False):
    """运行 Flask 服务器"""
    logger.info(f"Starting server at http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    run_server(debug=True)
