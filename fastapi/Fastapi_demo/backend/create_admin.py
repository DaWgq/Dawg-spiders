"""创建或重置管理员账号 (无需启动后端服务)。

用法:
    python create_admin.py                       # 创建/重置 admin / admin123
    python create_admin.py -u admin -p 新密码     # 指定用户名和密码

运行前请确保 sql/library_management.sql 中的表已创建 (users 表必须存在)。
"""
import argparse
import sys

from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal, engine
from app.models import User
from app.security import hash_password


def main(username: str, password: str) -> None:
    session: Session = SessionLocal()
    try:
        user = session.query(User).filter(User.username == username).first()
        new_hash = hash_password(password)
        if user is None:
            session.add(
                User(
                    username=username,
                    password_hash=new_hash,
                    real_name="系统管理员",
                    role="admin",
                )
            )
            print(f"已创建管理员账号: {username}")
        else:
            user.password_hash = new_hash
            print(f"已重置账号 {username} 的密码")
        session.commit()
        print(f"用户名: {username}")
        print(f"密码:   {password}")
        print("现在可以用该账号登录了。")
    finally:
        session.close()
    engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="创建或重置管理员账号")
    parser.add_argument("-u", "--username", default="admin", help="用户名 (默认 admin)")
    parser.add_argument("-p", "--password", default="admin123", help="密码 (默认 admin123)")
    args = parser.parse_args()
    try:
        main(args.username, args.password)
    except Exception as exc:  # noqa: BLE001
        print(f"操作失败: {exc}", file=sys.stderr)
        print(
            "请检查 config.py 的数据库配置, 并确认已执行 sql/library_management.sql 建表。",
            file=sys.stderr,
        )
        sys.exit(1)