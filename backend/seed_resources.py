import os, sys, random
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
sys.path.insert(0, os.path.dirname(__file__))
import django; django.setup()

from django.db.models import Count
from apps.resources.models import Resource
from apps.behaviors.models import UserBehavior
from django.contrib.auth.models import User

admin = User.objects.filter(is_staff=True).first()
if not admin:
    admin = User.objects.create_superuser("admin", "admin@test.com", "admin123")

# ── Dedup: delete resources with the same title, keeping the one with most data ──
dupes = (
    Resource.objects.values("title")
    .annotate(cnt=Count("id"))
    .filter(cnt__gt=1)
)
deleted_count = 0
for d in dupes:
    same = Resource.objects.filter(title=d["title"]).order_by("-browse_count", "-rating_count", "id")
    keeper = same.first()
    for r in same.exclude(id=keeper.id):
        UserBehavior.objects.filter(resource=r).update(resource=keeper)
        r.delete()
        deleted_count += 1

if deleted_count:
    print(f"Removed {deleted_count} duplicate resources")

# ── Seed data ──
data = [
    # ===== 编程语言 =====
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
        "title": "Go 语言入门 — Go by Example",
        "description": "通过 80+ 个带注释的代码示例学习 Go 语言，涵盖 goroutine、channel、interface 等核心特性。适合有编程基础的学习者快速上手 Go 语言。",
        "resource_type": "exercise",
        "category": "Go",
        "tags": ["Go", "并发", "后端开发"],
        "difficulty": "intermediate",
        "source": "Go by Example",
        "url": "https://gobyexample.com/",
        "cover_image": "https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?w=400",
    },
    {
        "title": "Rust 程序设计语言 — 官方中文版",
        "description": "Rust 官方文档的中文翻译版，从所有权、借用、生命周期等核心概念到高级特性，配合大量实例，是学习 Rust 系统编程的最佳入门资源。",
        "resource_type": "article",
        "category": "Rust",
        "tags": ["Rust", "系统编程", "内存安全"],
        "difficulty": "intermediate",
        "source": "Rust 官方",
        "url": "https://rustwiki.org/zh-CN/book/",
        "cover_image": "https://images.unsplash.com/photo-1629654297299-c8506221ca97?w=400",
    },

    # ===== 数据结构与算法 =====
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
        "title": "Hello 算法 — 动画图解数据结构与算法",
        "description": "开源免费的算法入门教程，用动画和图解讲解数据结构与算法。涵盖数组、链表、树、图、排序、搜索、回溯、动态规划等，支持 Python、Java、C++ 等多语言代码示例。",
        "resource_type": "article",
        "category": "算法",
        "tags": ["算法", "数据结构", "图解", "面试"],
        "difficulty": "beginner",
        "source": "Hello 算法",
        "url": "https://www.hello-algo.com/",
        "cover_image": "https://images.unsplash.com/photo-1509228468518-180b3b1f8f78?w=400",
    },

    # ===== 计算机网络 =====
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
        "title": "HTTP 协议原理与实践 — MDN Web 文档",
        "description": "Mozilla 官方编写的 HTTP 协议教程，从请求响应模型、状态码、缓存机制到 CORS、Cookie 安全策略，覆盖 Web 开发者必须掌握的网络知识。",
        "resource_type": "article",
        "category": "计算机网络",
        "tags": ["HTTP", "Web", "网络协议"],
        "difficulty": "beginner",
        "source": "MDN",
        "url": "https://developer.mozilla.org/zh-CN/docs/Web/HTTP",
        "cover_image": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=400",
    },

    # ===== 操作系统 =====
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
        "title": "计算机组成原理 — CMU 深入理解计算机系统",
        "description": "卡内基梅隆大学经典课程 CS:APP（深入理解计算机系统），B 站中字版本。从处理器架构、内存层次、链接、异常控制流到虚拟内存，覆盖计算机系统的核心概念。",
        "resource_type": "video",
        "category": "计算机组成",
        "tags": ["计算机组成", "体系结构", "CSAPP"],
        "difficulty": "advanced",
        "source": "B站",
        "url": "https://www.bilibili.com/video/BV1iW411d7hd",
        "cover_image": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=400",
    },

    # ===== 数据库 =====
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
        "title": "Redis 实战 — 官方交互式教程",
        "description": "通过 30+ 个交互式练习学习 Redis 数据结构与命令（String、Hash、List、Set、Sorted Set），理解缓存、会话存储、消息队列等典型应用场景。",
        "resource_type": "exercise",
        "category": "数据库",
        "tags": ["Redis", "缓存", "NoSQL"],
        "difficulty": "beginner",
        "source": "Redis 官方",
        "url": "https://try.redis.io/",
        "cover_image": "https://images.unsplash.com/photo-1544383835-bda2bc66a55d?w=400",
    },

    # ===== 前端开发 =====
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
        "title": "Vue.js 3 官方文档 — 渐进式前端框架",
        "description": "Vue 3 官方中文文档，涵盖响应式基础、组件深入、组合式 API、路由、状态管理等核心主题。适合有 HTML/CSS/JS 基础的学习者系统掌握 Vue 生态。",
        "resource_type": "article",
        "category": "前端",
        "tags": ["Vue", "前端框架", "组件化"],
        "difficulty": "intermediate",
        "source": "Vue 官方",
        "url": "https://cn.vuejs.org/guide/introduction.html",
        "cover_image": "https://images.unsplash.com/photo-1593720213428-28a5b39e0a8e?w=400",
    },

    # ===== 机器学习 / AI =====
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
        "title": "深度学习 — 斯坦福 CS231n 卷积神经网络",
        "description": "斯坦福大学著名课程 CS231n，面向视觉识别的卷积神经网络。从 CNN 基础原理到图像分类、目标检测、图像生成和迁移学习，含完整讲义和编程作业。",
        "resource_type": "video",
        "category": "深度学习",
        "tags": ["深度学习", "CNN", "计算机视觉"],
        "difficulty": "advanced",
        "source": "Stanford",
        "url": "https://www.youtube.com/playlist?list=PL3FW7Lu3i5JvHM8ljYj-zLfQRF3EO8sYv",
        "cover_image": "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=400",
    },
    {
        "title": "人工智能导论 — fast.ai 实用深度学习",
        "description": "fast.ai 出品的 Practical Deep Learning 免费课程，面向编程者的 AI 实战入门。从图像分类到自然语言处理，采用自顶向下的教学方式，先会用再理解原理，适合快速上手。",
        "resource_type": "video",
        "category": "人工智能",
        "tags": ["人工智能", "深度学习", "实战", "入门"],
        "difficulty": "beginner",
        "source": "fast.ai",
        "url": "https://www.youtube.com/playlist?list=PLfYUBJiXbdtSvpQjSnJJ_PmDQB_VyT5iU",
        "cover_image": "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=400",
    },
    {
        "title": "自然语言处理 — Hugging Face Transformers 实战",
        "description": "Hugging Face 官方 NLP 课程，从分词器原理到 Transformer 架构，再到 BERT、GPT 等预训练模型的微调与应用。使用 Hugging Face Hub 数千个预训练模型完成文本分类、命名实体识别、问答等实战任务。",
        "resource_type": "exercise",
        "category": "人工智能",
        "tags": ["NLP", "Transformer", "BERT", "GPT"],
        "difficulty": "advanced",
        "source": "Hugging Face",
        "url": "https://huggingface.co/learn/nlp-course",
        "cover_image": "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=400",
    },

    # ===== DevOps / 工具 =====
    {
        "title": "Git 入门教程 — 廖雪峰 Git 教程",
        "description": "国内最流行的 Git 入门教程，从工作区、暂存区、版本库的基本概念，到分支管理、远程协作、标签管理等高级操作，图文并茂，适合零基础入门版本控制。",
        "resource_type": "article",
        "category": "开发工具",
        "tags": ["Git", "版本控制", "协作"],
        "difficulty": "beginner",
        "source": "廖雪峰",
        "url": "https://www.liaoxuefeng.com/wiki/896043488029600",
        "cover_image": "https://images.unsplash.com/photo-1556075798-4825dfaaf498?w=400",
    },
    {
        "title": "Docker 从入门到实践 — 容器化部署指南",
        "description": "中文社区最完善的 Docker 教程，从镜像、容器的基本操作到 Dockerfile 编写、Docker Compose 多容器编排，再到 Kubernetes 入门，覆盖容器化全链路。",
        "resource_type": "article",
        "category": "DevOps",
        "tags": ["Docker", "容器", "部署", "DevOps"],
        "difficulty": "intermediate",
        "source": "Docker Practice",
        "url": "https://yeasy.gitbook.io/docker_practice/",
        "cover_image": "https://images.unsplash.com/photo-1605745341112-85968b19335b?w=400",
    },
    {
        "title": "Linux 命令行与 Shell 脚本 — The Linux Command Line",
        "description": "从终端基础到 Shell 脚本编程的完整指南。涵盖文件操作、权限管理、进程控制、管道与重定向、正则表达式、bash 脚本编写等 Linux 日常开发必备技能。",
        "resource_type": "article",
        "category": "Linux",
        "tags": ["Linux", "Shell", "命令行"],
        "difficulty": "beginner",
        "source": "LinuxCommand.org",
        "url": "https://linuxcommand.org/tlcl.php",
        "cover_image": "https://images.unsplash.com/photo-1629654297299-c8506221ca97?w=400",
    },

    # ===== 软件工程 / 系统设计 =====
    {
        "title": "系统设计入门 — System Design Primer",
        "description": "GitHub 173k+ Star 的系统设计面试准备指南。涵盖可扩展性、负载均衡、数据库分片、缓存策略、消息队列、微服务等核心主题，附经典面试题分析与架构图。",
        "resource_type": "article",
        "category": "系统设计",
        "tags": ["系统设计", "架构", "面试", "分布式"],
        "difficulty": "advanced",
        "source": "GitHub",
        "url": "https://github.com/donnemartin/system-design-primer",
        "cover_image": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=400",
    },
    {
        "title": "RESTful API 设计最佳实践",
        "description": "从资源命名、HTTP 方法语义、状态码使用、认证方案到分页、版本控制、错误处理的 RESTful API 完整设计指南，适合后端开发者和 API 设计者。",
        "resource_type": "article",
        "category": "系统设计",
        "tags": ["REST", "API", "后端设计"],
        "difficulty": "intermediate",
        "source": "RestfulAPI.net",
        "url": "https://restfulapi.net/",
        "cover_image": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=400",
    },
    {
        "title": "Django 官方教程 — 从模型到部署",
        "description": "Django 官方入门教程，带你从零搭建一个 Polls 投票应用。覆盖模型定义、视图编写、模板渲染、表单处理、单元测试、静态文件管理和 Admin 定制。",
        "resource_type": "exercise",
        "category": "后端开发",
        "tags": ["Django", "Python", "后端开发"],
        "difficulty": "intermediate",
        "source": "Django 官方",
        "url": "https://docs.djangoproject.com/zh-hans/5.0/intro/tutorial01/",
        "cover_image": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=400",
    },
    {
        "title": "软件工程 — 代码整洁之道知识总结",
        "description": "基于 Robert C. Martin《Clean Code》的核心思想，涵盖命名规范、函数设计、注释原则、代码格式、错误处理、类与对象设计等编程实践，帮助你写出可读可维护的高质量代码。",
        "resource_type": "article",
        "category": "软件工程",
        "tags": ["代码质量", "重构", "编程规范"],
        "difficulty": "intermediate",
        "source": "Clean Code",
        "url": "https://github.com/ryanmcdermott/clean-code-javascript",
        "cover_image": "https://images.unsplash.com/photo-1516116216624-53e697fedbea?w=400",
    },

    # ===== 数据科学 =====
    {
        "title": "Python 数据科学手册 — NumPy / Pandas / Matplotlib",
        "description": "开源免费的 Python 数据科学入门书，通过 Jupyter Notebook 实操讲解 NumPy 向量化计算、Pandas 数据处理、Matplotlib 可视化，以及 Scikit-Learn 机器学习基础。",
        "resource_type": "exercise",
        "category": "数据科学",
        "tags": ["数据分析", "Pandas", "NumPy", "可视化"],
        "difficulty": "intermediate",
        "source": "GitHub",
        "url": "https://jakevdp.github.io/PythonDataScienceHandbook/",
        "cover_image": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400",
    },

    # ===== 编译原理 =====
    {
        "title": "编译原理实践 — Crafting Interpreters",
        "description": "Bob Nystrom 编写的编译器实现教程，手把手带你用 Java 和 C 分别实现一个完整的编程语言解释器。涵盖词法分析、语法解析、中间表示、虚拟机执行等编译原理核心概念。",
        "resource_type": "exercise",
        "category": "编译原理",
        "tags": ["编译原理", "解释器", "编程语言"],
        "difficulty": "advanced",
        "source": "Crafting Interpreters",
        "url": "https://craftinginterpreters.com/",
        "cover_image": "https://images.unsplash.com/photo-1515879218367-8466d910aaa9?w=400",
    },

    # ===== 安全 =====
    {
        "title": "Web 安全入门 — OWASP Top 10 漏洞详解",
        "description": "OWASP 官方整理的 Web 应用十大安全风险，包括注入攻击、身份验证失效、敏感数据泄露、XML 外部实体、访问控制缺失、安全配置错误、跨站脚本 XSS、不安全反序列化等。",
        "resource_type": "article",
        "category": "信息安全",
        "tags": ["安全", "OWASP", "Web安全"],
        "difficulty": "intermediate",
        "source": "OWASP",
        "url": "https://owasp.org/www-project-top-ten/",
        "cover_image": "https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?w=400",
    },
]

# ── Upsert resources ──
created = updated = 0
for item in data:
    r, is_new = Resource.objects.get_or_create(
        title=item["title"],
        defaults={**item, "created_by": admin},
    )
    if is_new:
        r.browse_count = random.randint(50, 500)
        r.avg_rating = round(random.uniform(3.0, 5.0), 1)
        r.rating_count = random.randint(5, 100)
        r.save(update_fields=["browse_count", "avg_rating", "rating_count"])
        created += 1
    else:
        # Update fields for existing resources (fix URLs, types, etc.)
        changed = False
        for field in ["description", "resource_type", "category", "tags",
                       "difficulty", "source", "url", "cover_image"]:
            if getattr(r, field) != item[field]:
                setattr(r, field, item[field])
                changed = True
        if changed:
            r.save()
            updated += 1

print(f"Created {created} new resources, updated {updated} existing")
print(f"Total: {Resource.objects.count()} resources")

# ── Seed user behaviors (so collaborative filtering can activate) ──
all_ids = list(Resource.objects.values_list("id", flat=True))
users = list(User.objects.all())

for user in users:
    existing = UserBehavior.objects.filter(user=user).count()
    if existing >= 15:
        print(f"User {user.username}: {existing} behaviors (skip)")
        continue

    # Pick 10-20 resources for this user to simulate engagement
    n = random.randint(10, 20)
    picked = random.sample(all_ids, min(n, len(all_ids)))

    for rid in picked:
        UserBehavior.objects.get_or_create(
            user=user, resource_id=rid,
            behavior_type=UserBehavior.BehaviorType.BROWSE,
        )
        # 60% chance of also rating
        if random.random() < 0.6:
            UserBehavior.objects.get_or_create(
                user=user, resource_id=rid,
                behavior_type=UserBehavior.BehaviorType.RATE,
                defaults={"rating": random.randint(2, 5)},
            )

    print(f"User {user.username}: {UserBehavior.objects.filter(user=user).count()} behaviors")

print("Behavior seeding complete")