import os, sys, random
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
sys.path.insert(0, os.path.dirname(__file__))
import django; django.setup()

from apps.resources.models import Resource
from django.contrib.auth.models import User

admin = User.objects.filter(is_staff=True).first()
if not admin:
    admin = User.objects.create_superuser("admin", "admin@test.com", "admin123")

data = [
    {"title": "Python入门教程 - 从零开始学编程", "description": "面向初学者的Python完整教程，涵盖基本语法、数据结构和函数编程。包含大量实例和练习。", "resource_type": "video", "category": "Python", "tags": ["Python", "基础", "编程入门"], "difficulty": "beginner", "source": "B站", "url": "https://example.com/python-intro", "cover_image": "https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=400"},
    {"title": "数据结构与算法精讲", "description": "系统学习常见数据结构：数组、链表、栈、队列、树、图，以及排序、查找等经典算法。", "resource_type": "article", "category": "数据结构", "tags": ["数据结构", "算法", "面试"], "difficulty": "intermediate", "source": "CSDN", "url": "https://example.com/dsa", "cover_image": "https://images.unsplash.com/photo-1516116216624-53e697fedbea?w=400"},
    {"title": "机器学习实战 - 手写数字识别", "description": "使用TensorFlow和MNIST数据集，从零搭建神经网络完成手写数字识别任务。", "resource_type": "exercise", "category": "机器学习", "tags": ["机器学习", "深度学习", "TensorFlow"], "difficulty": "advanced", "source": "GitHub", "url": "https://example.com/ml-mnist", "cover_image": "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=400"},
    {"title": "计算机网络基础 - TCP/IP协议栈", "description": "详解TCP/IP五层模型，包括应用层、传输层、网络层、数据链路层和物理层的工作原理。", "resource_type": "video", "category": "计算机网络", "tags": ["计算机网络", "TCP/IP", "协议"], "difficulty": "beginner", "source": "B站", "url": "https://example.com/network", "cover_image": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=400"},
    {"title": "Java面向对象编程深入", "description": "深入理解Java的封装、继承、多态机制，以及接口、抽象类、内部类等高级特性。", "resource_type": "article", "category": "Java", "tags": ["Java", "面向对象", "编程基础"], "difficulty": "intermediate", "source": "掘金", "url": "https://example.com/java-oop", "cover_image": "https://images.unsplash.com/photo-1623282033815-40b05d96c903?w=400"},
    {"title": "C++ STL源码剖析", "description": "深入分析C++标准模板库的vector、list、map等容器的底层实现原理。", "resource_type": "article", "category": "C++", "tags": ["C++", "STL", "源码分析"], "difficulty": "advanced", "source": "知乎", "url": "https://example.com/cpp-stl", "cover_image": "https://images.unsplash.com/photo-1515879218367-8466d910auj9?w=400"},
    {"title": "操作系统原理 - 进程与线程", "description": "理解操作系统中进程管理、线程模型、CPU调度算法和同步互斥机制。", "resource_type": "video", "category": "操作系统", "tags": ["操作系统", "进程", "线程", "调度"], "difficulty": "intermediate", "source": "B站", "url": "https://example.com/os-process", "cover_image": "https://images.unsplash.com/photo-1629654297299-c8506221ca97?w=400"},
    {"title": "前端开发入门 - HTML/CSS/JavaScript", "description": "从零学习前端三大核心技术，掌握网页布局、样式设计和交互开发的基础知识。", "resource_type": "video", "category": "前端", "tags": ["前端", "HTML", "CSS", "JavaScript"], "difficulty": "beginner", "source": "B站", "url": "https://example.com/frontend-intro", "cover_image": "https://images.unsplash.com/photo-1593720213428-28a5b39e0a8e?w=400"},
    {"title": "SQL数据库设计与优化", "description": "学习关系型数据库的范式设计、索引优化、查询性能调优和事务管理。", "resource_type": "article", "category": "数据库", "tags": ["数据库", "SQL", "性能优化"], "difficulty": "intermediate", "source": "博客园", "url": "https://example.com/sql-optimize", "cover_image": "https://images.unsplash.com/photo-1544383835-bda2bc66a55d?w=400"},
    {"title": "深度学习入门 - 卷积神经网络", "description": "从CNN基础原理到实际应用，包括图像分类、目标检测和迁移学习。", "resource_type": "video", "category": "深度学习", "tags": ["深度学习", "CNN", "图像处理"], "difficulty": "advanced", "source": "B站", "url": "https://example.com/dl-cnn", "cover_image": "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=400"},
    {"title": "LeetCode刷题指南 - 动态规划专题", "description": "系统讲解动态规划解题思路，包含50+经典题目详解和代码实现。", "resource_type": "exercise", "category": "算法", "tags": ["算法", "动态规划", "LeetCode"], "difficulty": "advanced", "source": "LeetCode", "url": "https://example.com/leetcode-dp", "cover_image": "https://images.unsplash.com/photo-1504639725590-34d0984388bd?w=400"},
    {"title": "人工智能导论 - 从图灵测试到GPT", "description": "全面了解人工智能的发展历史、核心概念和前沿技术，适合AI入门学习者。", "resource_type": "article", "category": "人工智能", "tags": ["人工智能", "AI", "GPT", "机器学习"], "difficulty": "beginner", "source": "知乎", "url": "https://example.com/ai-intro", "cover_image": "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=400"},
]

for item in data:
    r = Resource.objects.create(**item, created_by=admin)
    r.browse_count = random.randint(50, 500)
    r.avg_rating = round(random.uniform(3.0, 5.0), 1)
    r.rating_count = random.randint(5, 100)
    r.save(update_fields=["browse_count", "avg_rating", "rating_count"])

print(f"Created {len(data)} resources")
