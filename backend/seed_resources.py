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
    {
        "title": "Python 入门教程 — 小甲鱼零基础学 Python",
        "description": "经典的 B 站 Python 入门课，小甲鱼带你从零开始学编程。涵盖基本语法、变量、数据类型、条件判断、循环、函数、文件操作等核心内容，每节课都有配套练习。",
        "resource_type": "video",
        "category": "Python",
        "tags": ["Python", "基础", "编程入门"],
        "difficulty": "beginner",
        "source": "B站",
        "url": "https://www.bilibili.com/video/BV1Fs411A7HZ",
        "cover_image": "https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=400",
    },
    {
        "title": "数据结构与算法 — OI Wiki 在线教程",
        "description": "国内最全面的算法竞赛知识库，涵盖数组、链表、栈、队列、树、图等基础数据结构，以及排序、搜索、动态规划等经典算法，附有详细代码示例和复杂度分析。",
        "resource_type": "article",
        "category": "数据结构",
        "tags": ["数据结构", "算法", "竞赛"],
        "difficulty": "intermediate",
        "source": "OI Wiki",
        "url": "https://oi-wiki.org/ds/",
        "cover_image": "https://images.unsplash.com/photo-1516116216624-53e697fedbea?w=400",
    },
    {
        "title": "机器学习实战 — TensorFlow 官方快速入门",
        "description": "Google 官方 TensorFlow 教程，使用 MNIST 数据集从零搭建神经网络完成手写数字识别。覆盖模型构建、训练、评估全流程，适合有 Python 基础的学习者。",
        "resource_type": "exercise",
        "category": "机器学习",
        "tags": ["机器学习", "深度学习", "TensorFlow"],
        "difficulty": "advanced",
        "source": "TensorFlow 官方",
        "url": "https://www.tensorflow.org/tutorials/quickstart/beginner",
        "cover_image": "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=400",
    },
    {
        "title": "计算机网络 — 韩立刚老师 TCP/IP 详解",
        "description": "高校经典计算机网络课程视频，详解 TCP/IP 五层模型：应用层（HTTP/DNS）、传输层（TCP/UDP）、网络层（IP/路由）、数据链路层与物理层。深入浅出，适合计算机专业学生。",
        "resource_type": "video",
        "category": "计算机网络",
        "tags": ["计算机网络", "TCP/IP", "协议"],
        "difficulty": "beginner",
        "source": "B站",
        "url": "https://www.bilibili.com/video/BV1c4411d7jb",
        "cover_image": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=400",
    },
    {
        "title": "Java 面向对象编程 — Oracle 官方教程",
        "description": "Oracle 官方出品的 Java OOP 教程，讲解封装、继承、多态三大特性，以及接口、抽象类、内部类、Lambda 表达式等高级特性。英文原版，代码示例丰富。",
        "resource_type": "article",
        "category": "Java",
        "tags": ["Java", "面向对象", "编程基础"],
        "difficulty": "intermediate",
        "source": "Oracle",
        "url": "https://docs.oracle.com/javase/tutorial/java/concepts/",
        "cover_image": "https://images.unsplash.com/photo-1623282033815-40b05d96c903?w=400",
    },
    {
        "title": "C++ STL 标准库参考 — cppreference",
        "description": "最权威的 C++ 标准库文档（中文版），详细列出 vector、list、map、set 等容器的接口、复杂度与使用示例。日常开发和面试前查阅的必备参考。",
        "resource_type": "article",
        "category": "C++",
        "tags": ["C++", "STL", "标准库"],
        "difficulty": "advanced",
        "source": "cppreference",
        "url": "https://zh.cppreference.com/w/cpp/container",
        "cover_image": "https://images.unsplash.com/photo-1515879218367-8466d910aaa9?w=400",
    },
    {
        "title": "操作系统原理 — OSTEP 经典教材",
        "description": "威斯康星大学《操作系统：三大简易部分》免费在线教材，被全球高校广泛采用。涵盖虚拟化（CPU/内存）、并发（锁/信号量）、持久化（文件系统/磁盘）三大模块，附课后项目。",
        "resource_type": "article",
        "category": "操作系统",
        "tags": ["操作系统", "进程", "并发", "文件系统"],
        "difficulty": "intermediate",
        "source": "OSTEP",
        "url": "https://pages.cs.wisc.edu/~remzi/OSTEP/",
        "cover_image": "https://images.unsplash.com/photo-1629654297299-c8506221ca97?w=400",
    },
    {
        "title": "前端开发入门 — MDN Web 开发指南",
        "description": "Mozilla 官方出品的前端入门教程，从零学习 HTML 结构、CSS 样式、JavaScript 交互三大核心技术。包含互动示例和最佳实践，是 Web 开发最权威的免费学习资源。",
        "resource_type": "article",
        "category": "前端",
        "tags": ["前端", "HTML", "CSS", "JavaScript"],
        "difficulty": "beginner",
        "source": "MDN",
        "url": "https://developer.mozilla.org/zh-CN/docs/Learn/Getting_started_with_the_web",
        "cover_image": "https://images.unsplash.com/photo-1593720213428-28a5b39e0a8e?w=400",
    },
    {
        "title": "数据库性能优化 — MySQL 8.0 官方文档",
        "description": "MySQL 官方优化指南，涵盖 SQL 语句优化、索引策略、EXPLAIN 执行计划分析、查询缓存、表结构设计范式和存储引擎选择。面向有 SQL 基础的学习者。",
        "resource_type": "article",
        "category": "数据库",
        "tags": ["数据库", "SQL", "性能优化", "MySQL"],
        "difficulty": "intermediate",
        "source": "MySQL 官方",
        "url": "https://dev.mysql.com/doc/refman/8.0/en/optimization.html",
        "cover_image": "https://images.unsplash.com/photo-1544383835-bda2bc66a55d?w=400",
    },
    {
        "title": "深度学习 — 斯坦福 CS231n 卷积神经网络",
        "description": "斯坦福大学著名课程 CS231n，面向视觉识别的卷积神经网络。从 CNN 基础原理到图像分类、目标检测、图像生成和迁移学习，含完整讲义和编程作业。",
        "resource_type": "video",
        "category": "深度学习",
        "tags": ["深度学习", "CNN", "计算机视觉"],
        "difficulty": "advanced",
        "source": "Stanford",
        "url": "https://cs231n.github.io/",
        "cover_image": "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=400",
    },
    {
        "title": "算法练习 — LeetCode 动态规划精选题单",
        "description": "LeetCode 官方整理的动态规划专题，包含 50+ 经典题目（背包、最长子序列、编辑距离、股票买卖等），由易到难排列。每道题有题解和多种语言实现。",
        "resource_type": "exercise",
        "category": "算法",
        "tags": ["算法", "动态规划", "LeetCode", "面试"],
        "difficulty": "advanced",
        "source": "LeetCode",
        "url": "https://leetcode.cn/problemset/all/?topicSlugs=dynamic-programming",
        "cover_image": "https://images.unsplash.com/photo-1504639725590-34d0984388bd?w=400",
    },
    {
        "title": "人工智能导论 — fast.ai 实用深度学习",
        "description": "fast.ai 出品的 Practical Deep Learning 免费课程，面向编程者的 AI 实战入门。从图像分类到自然语言处理，采用自顶向下的教学方式，先会用再理解原理，适合快速上手。",
        "resource_type": "video",
        "category": "人工智能",
        "tags": ["人工智能", "深度学习", "实战", "入门"],
        "difficulty": "beginner",
        "source": "fast.ai",
        "url": "https://course.fast.ai/",
        "cover_image": "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=400",
    },
]

for item in data:
    r = Resource.objects.create(**item, created_by=admin)
    r.browse_count = random.randint(50, 500)
    r.avg_rating = round(random.uniform(3.0, 5.0), 1)
    r.rating_count = random.randint(5, 100)
    r.save(update_fields=["browse_count", "avg_rating", "rating_count"])

print(f"Created {len(data)} resources")