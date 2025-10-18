#!/usr/bin/env python

import sys
import argparse
from pathlib import Path

try:
    from video_translator.web_server import run_server
except ImportError:
    from web_server import run_server

def main():
    parser = argparse.ArgumentParser(
        description='启动视频翻译 Web 服务器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
  python -m video_translator.run_web_server
  python -m video_translator.run_web_server --host 0.0.0.0 --port 8080
  python -m video_translator.run_web_server --debug
        '''
    )
    
    parser.add_argument(
        '--host',
        default='127.0.0.1'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=5000
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
    )
    
    args = parser.parse_args()
    
    print(f"""
╔══════════════════════════════════════╗
║   Video Translator Web Server        ║
╚══════════════════════════════════════╝

Server:
  IP: {args.host}
  Port: {args.port}

url: http://{args.host}:{args.port}
    """)
    
    try:
        run_server(host=args.host, port=args.port, debug=args.debug)
    except KeyboardInterrupt:
        print("\n\nserver closed")
        sys.exit(0)
    except Exception as e:
        print(f"\n错误: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
