# ec
[![警报](http://10.122.104.127:9001/api/project_badges/measure?project=sonar_ec&metric=alert_status)](http://10.122.104.127:9001/dashboard?id=sonar_ec)
### 需要配置几个环境变量
    test ci hh2 
    export MODE='xxx' (PRODUCTION 或者 DEVELOPMENT)

### 创建 venv 虚拟环境：

    python3 -m venv venv 

### 进入虚拟环境工作：

    source venv/bin/active


### 安装依赖包
    
    pip install -r requirements.txt

### 启动服务

    python manager.py runserver(测试)
    gunicorn -c  gunicorn.py -b 0.0.0.0:5000 wsgi:application (正式)
    
### 启动 Celery

    celery worker -A celery_worker.celery -l DEBUG (-Q default)
    celery beat -A celery_worker.celery -l DEBUG
    
### 启动celery beat(用这个)
    celery worker -l INFO -c 1 -A celery_worker.celery --beat
    
### 启动celery flower
     flower -A celery_worker.celery 
    
### 数据库迁移
    python manager.py db init
    python manager.py db migrate
    python manager.py db upgrade

### 测试