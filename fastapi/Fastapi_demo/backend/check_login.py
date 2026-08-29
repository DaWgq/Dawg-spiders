"""诊断登录问题的脚本: 直连后端使用的同一个数据库, 复现登录校验逻辑。

在 backend 目录下运行:
    python check_login.py [-u admin] [-p admin123]

会打印:
  1. users 表中所有账号
  2. 每个账号存储的密码哈希的长度与准确内容
  3. 分别用 verify_password(捕获异常) 和 bcrypt.checkpw(抛出异常) 校验,
     以定位是"哈希被截断/损坏"还是"校验代码环境不一致"。
"""
import argparse
import sys
import os

# 让脚本能 import app.*
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bcrypt  # noqa: E402

from app.config import settings  # noqa: E402
from app.database import SessionLocal, engine  # noqa: E402
from app.models import User  # noqa: E402
from app.security import verify_password  # noqa: E402


def main(username: str, password: str) -> None:
    print(f"目标账号: {username} / {password}")
    print(f"数据库连接: {settings.DATABASE_URL!r}")
    print("-" * 70)

    session = SessionLocal()
    try:
        users = session.query(User).all()
        if not users:
            print("!! users 表为空, 没有任何账号 (请先执行建表/seed)。")
            return

        print(f"users 表共 {len(users)} 条记录:")
        for u in users:
            h = u.password_hash
            exact_match = h == (
                "$2b$12$w20RwwrR/I6ZLIZDuOMtcOblUscXrso/wJgH.rZ2QMNozx6MFHmRO"
            )
            print(f"\n- username={u.username!r} role={u.role!r} real_name={u.real_name!r}")
            print(f"  hash 长度 = {len(h)}  (正确长度应为 60)")
            print(f"  hash 内容 = {h!r}")
            print(f"  hash 是否为脚本内置的 admin123 哈希 = {exact_match}")
            if u.username != username:
                continue

            print(f"\n  -- 校验 {password!r} --")
            ok_caught = verify_password(password, h)
            print(f"  verify_password(捕获异常) = {ok_caught}")
            try:
                ok_raw = bcrypt.checkpw(password.encode("utf-8"), h.encode("utf-8"))
                print(f"  bcrypt.checkpw(抛出异常)  = {ok_raw}")
            except (ValueError, TypeError) as exc:
                print(f"  bcrypt.checkpw 抛异常: {exc!r}")
                print("  ==> 说明库里的哈希不是有效的 bcrypt 哈希, 很可能被截断或损坏。")
    finally:
        session.close()
    engine.dispose()

    print("-" * 70)
    print("结论: 若 hash 长度 != 60 或 checkpw 抛异常 → 运行 `python create_admin.py` 重新生成哈希;")
    print("      若 checkpw 返回 True 但仍 401 → 前后端连的不是同一个后端/数据库。")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="诊断登录校验")
    parser.add_argument("-u", "--username", default="admin")
    parser.add_argument("-p", "--password", default="admin123")
    args = parser.parse_args()
    main(args.username, args.password)