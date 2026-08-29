"""启动时自动补齐默认数据, 保证开箱即用。

- 若 users 表中不存在默认管理员, 则自动创建 admin / admin123
- 若 categories 表为空, 则自动填充默认图书分类
仅当数据缺失时写入, 幂等, 不会覆盖已有数据。
"""
import logging

from sqlalchemy.orm import Session

from .models import Category, User
from .security import hash_password

logger = logging.getLogger("seed")

DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"
DEFAULT_CATEGORIES = ["计算机/IT", "文学小说", "历史传记", "科学技术", "其他"]


def ensure_defaults(db: Session) -> None:
    admin = db.query(User).filter(User.username == DEFAULT_ADMIN_USERNAME).first()
    if admin is None:
        db.add(
            User(
                username=DEFAULT_ADMIN_USERNAME,
                password_hash=hash_password(DEFAULT_ADMIN_PASSWORD),
                real_name="系统管理员",
                role="admin",
            )
        )
        logger.info(
            "已创建默认管理员账号: %s / %s", DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD
        )

    if db.query(Category).count() == 0:
        for name in DEFAULT_CATEGORIES:
            db.add(Category(name=name))
        logger.info("已填充默认图书分类: %s", ", ".join(DEFAULT_CATEGORIES))

    db.commit()