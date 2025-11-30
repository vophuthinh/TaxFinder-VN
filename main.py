# main.py
# -*- coding: utf-8 -*-

"""
Entry point cho ứng dụng tra cứu mã số thuế
"""

import logging
from masothue_app import MasothueApp

if __name__ == "__main__":
    import os
    from pathlib import Path
    
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    from datetime import datetime
    log_file = log_dir / f"masothue_{datetime.now().strftime('%Y%m%d')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Khởi động ứng dụng. Log file: {log_file}")
    
    app = MasothueApp()
    app.mainloop()

