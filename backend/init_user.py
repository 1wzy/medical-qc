"""
初始化用户脚本
用于创建默认管理员账户
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from db import SessionLocal
from models.user import User, UserRole, UserStatus
from utils.auth import get_password_hash

def init_users():
    """初始化用户"""
    db = SessionLocal()
    try:
        # 检查是否已有用户
        user_count = db.query(User).count()
        if user_count > 0:
            print("⚠️  数据库中已存在用户，跳过初始化")
            return
        
        # 创建默认管理员账户
        admin_user = User(
            username="admin",
            password_hash=get_password_hash("admin"),
            real_name="系统管理员",
            role=UserRole.ADMIN.value,  # 使用 .value 获取字符串值
            status=UserStatus.ACTIVE.value  # 使用 .value 获取字符串值
        )
        
        # 创建默认普通用户
        normal_user = User(
            username="user",
            password_hash=get_password_hash("user"),
            real_name="普通用户",
            role=UserRole.USER.value,  # 使用 .value 获取字符串值
            status=UserStatus.ACTIVE.value  # 使用 .value 获取字符串值
        )
        
        db.add(admin_user)
        db.add(normal_user)
        db.commit()
        
        print("✅ 用户初始化成功！")
        print("\n默认账户：")
        print("  管理员: admin / admin")
        print("  普通用户: user / user")
        print("\n⚠️  请在生产环境中修改默认密码！")
        
    except Exception as e:
        print(f"❌ 用户初始化失败: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_users()

